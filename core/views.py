import io
import math
import qrcode
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Avg, Count, Sum, Q
from django.db.models.functions import ExtractHour
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .forms import RegisterForm, VehicleForm, BookingForm, ReviewForm
from .models import Vehicle, Station, Booking, Review


# ---------- Auth and home ----------

def home(request):
    return render(request, 'home.html')


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'registration/register.html', {'form': form})


# ---------- Stations (search, availability, map) ----------

def station_list(request):
    q = request.GET.get('q', '')
    ctype = request.GET.get('type', '')
    stations = Station.objects.filter(is_open=True).annotate(
        avg_rating=Avg('review__rating'), review_count=Count('review'))
    if q:
        stations = stations.filter(Q(name__icontains=q) | Q(address__icontains=q))
    if ctype:
        stations = stations.filter(charger_type=ctype)

    now = timezone.now()
    for s in stations:
        current = Booking.objects.filter(
            station=s, status__in=['booked', 'charging'],
            start_time__lte=now, end_time__gte=now)
        s.free_slots = max(s.total_slots - current.count(), 0)
        s.waiting = Booking.objects.filter(
            station=s, status='booked', start_time__gt=now).count()

        s.wait_min = None
        if s.free_slots == 0:
            nxt = current.order_by('end_time').first()
            if nxt:
                s.wait_min = max(int((nxt.end_time - now).total_seconds() // 60), 1)

    types = Station.objects.values_list('charger_type', flat=True).distinct()
    map_data = [{'id': s.id, 'name': s.name, 'lat': s.latitude, 'lng': s.longitude,
                 'free': s.free_slots, 'type': s.charger_type} for s in stations]
    return render(request, 'stations.html', {
        'stations': stations, 'q': q, 'types': types,
        'ctype': ctype, 'map_data': map_data})
def station_detail(request, pk):
    station = get_object_or_404(Station, pk=pk)
    reviews = Review.objects.filter(station=station).select_related('user').order_by('-id')
    agg = reviews.aggregate(avg=Avg('rating'), n=Count('id'))

    form = None
    if request.user.is_authenticated:
        existing = reviews.filter(user=request.user).first()
        form = ReviewForm(request.POST or None, instance=existing)
        if request.method == 'POST' and form.is_valid():
            r = form.save(commit=False)
            r.user, r.station = request.user, station
            r.save()
            return redirect('station_detail', pk=pk)

    return render(request, 'station_detail.html', {
        'station': station, 'reviews': reviews, 'agg': agg, 'form': form})


# ---------- Vehicle and booking ----------

@login_required
def add_vehicle(request):
    form = VehicleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        v = form.save(commit=False)
        v.owner = request.user
        v.save()
        return redirect('stations')
    return render(request, 'form_page.html', {'form': form, 'title': 'Add your EV'})


@login_required
def book_station(request, pk):
    station = get_object_or_404(Station, pk=pk)
    form = BookingForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        b = form.save(commit=False)

        if b.target_battery <= b.current_battery or b.target_battery > 100:
            form.add_error('target_battery',
                           'Target must be higher than current and max 100.')
        elif b.start_time < timezone.now():
            form.add_error('start_time', 'Choose a future time.')
        else:
            energy = b.vehicle.battery_kwh * (b.target_battery - b.current_battery) / 100
            hours = energy / station.power_kw
            b.end_time = b.start_time + timedelta(hours=hours)
            b.est_cost = round(energy * station.price_per_kwh, 2)

            clash = Booking.objects.filter(
                station=station, status__in=['booked', 'charging'],
                start_time__lt=b.end_time, end_time__gt=b.start_time).count()

            if clash >= station.total_slots:
                form.add_error(None, 'No slot free at that time. Try another time.')
            else:
                b.user, b.station = request.user, station
                b.save()

                if request.user.email:
                    try:
                        send_mail(
                            f'Booking confirmed: {station.name}',
                            f'Hi {request.user.username},\n\n'
                            f'Your slot is booked.\n'
                            f'Station: {station.name}\n'
                            f'Time: {b.start_time:%d %b %Y, %H:%M} to {b.end_time:%H:%M}\n'
                            f'Estimated cost: Rs {b.est_cost}\n'
                            f'Booking ID: {b.id}\n\n'
                            f'Show your QR ticket at the station.',
                            None, [request.user.email])
                    except Exception:
                        pass

                return redirect('ticket', pk=b.pk)

    return render(request, 'book.html', {'form': form, 'station': station})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, pk):
    b = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST' and b.status == 'booked':
        b.status = 'cancelled'
        b.save()
    return redirect('my_bookings')


# ---------- QR ticket and verification ----------

@login_required
def ticket(request, pk):
    b = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'ticket.html', {'b': b})


@login_required
def booking_qr(request, pk):
    b = get_object_or_404(Booking, pk=pk, user=request.user)
    url = request.build_absolute_uri(reverse('verify', args=[b.pk]))
    buf = io.BytesIO()
    qrcode.make(url).save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')


@staff_member_required
def verify_booking(request, pk):
    b = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST' and b.status == 'booked':
        b.status = 'charging'
        b.save()
    return render(request, 'verify.html', {'b': b})


# ---------- Trip range planner ----------

def haversine(a, b, c, d):
    r = math.radians
    h = math.sin(r(c - a) / 2) ** 2 + math.cos(r(a)) * math.cos(r(c)) * math.sin(r(d - b) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


@login_required
def trip_planner(request):
    vehicles = Vehicle.objects.filter(owner=request.user)
    return render(request, 'planner.html', {'vehicles': vehicles})


@login_required
def plan_trip_api(request):
    try:
        v = Vehicle.objects.get(pk=request.GET['vehicle'], owner=request.user)
        pct = float(request.GET['battery'])
        lat, lng, dlat, dlng = [float(request.GET[k]) for k in ('lat', 'lng', 'dlat', 'dlng')]
    except (KeyError, ValueError, Vehicle.DoesNotExist):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    # assumes 0.15 kWh/km consumption and a 10% safety margin
    range_km = round(v.battery_kwh * pct / 100 / 0.15 * 0.9, 1)
    dist = round(haversine(lat, lng, dlat, dlng) * 1.3, 1)   # x1.3 = road distance
    result = {'range_km': range_km, 'distance_km': dist,
              'reachable': dist <= range_km, 'stations': []}

    if not result['reachable']:
        opts = []
        for s in Station.objects.filter(is_open=True):
            to_station = haversine(lat, lng, s.latitude, s.longitude) * 1.3
            if to_station <= range_km:
                opts.append({
                    'id': s.id, 'name': s.name, 'charger': s.charger_type,
                    'from_you_km': round(to_station, 1),
                    'to_dest_km': round(haversine(s.latitude, s.longitude, dlat, dlng) * 1.3, 1)})
        opts.sort(key=lambda x: x['to_dest_km'])
        result['stations'] = opts[:3]
    return JsonResponse(result)


# ---------- Admin analytics dashboard ----------

@staff_member_required
def dashboard(request):
    valid = Booking.objects.exclude(status='cancelled')

    counts = {r['h']: r['n'] for r in
              valid.annotate(h=ExtractHour('start_time')).values('h').annotate(n=Count('id'))}
    peak = [counts.get(h, 0) for h in range(24)]

    rows = valid.values('station__name').annotate(
        n=Count('id'), rev=Sum('est_cost')).order_by('-n')

    chart_data = {
        'hours': [f'{h}:00' for h in range(24)],
        'peak': peak,
        'stations': [r['station__name'] for r in rows],
        'bookings': [r['n'] for r in rows],
        'revenue': [round(r['rev'] or 0, 2) for r in rows],
    }
    stats = {
        'total': Booking.objects.count(),
        'revenue': round(valid.aggregate(t=Sum('est_cost'))['t'] or 0, 2),
        'charging': Booking.objects.filter(status='charging').count(),
        'cancelled': Booking.objects.filter(status='cancelled').count(),
        'stations': Station.objects.count(),
        'vehicles': Vehicle.objects.count(),
    }
    return render(request, 'dashboard.html', {'stats': stats, 'chart_data': chart_data})

from django.contrib.auth.views import LoginView

class SmartLoginView(LoginView):
    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        return reverse('admin:index') if self.request.user.is_staff else reverse('home')