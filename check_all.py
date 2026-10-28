from django.test import Client
from django.contrib.auth.models import User
from core.models import Booking, Station

def run(c, urls):
    for u in urls:
        try:
            print(c.get(u).status_code, u)
        except Exception as e:
            print("ERROR", u, "->", type(e).__name__, e)

s = Station.objects.first()
b = Booking.objects.first()
print("stations:", Station.objects.count(), "| bookings:", Booking.objects.count())

print("\n--- Public ---")
run(Client(HTTP_HOST="127.0.0.1"), ["/", "/accounts/login/", "/register/", "/stations/"] + ([f"/station/{s.id}/"] if s else []))

print("\n--- User (arjun) ---")
c = Client(HTTP_HOST="127.0.0.1")
print("login ok:", c.login(username="arjun", password="demo12345"))
pages = ["/my-bookings/", "/planner/", "/vehicle/add/"]
if s: pages.append(f"/book/{s.id}/")
mine = Booking.objects.filter(user__username="arjun").first()
if mine: pages += [f"/ticket/{mine.id}/", f"/booking/{mine.id}/qr/"]
run(c, pages)

print("\n--- Admin ---")
su = User.objects.filter(is_superuser=True).first()
if su:
    print("admin:", su.username, "|", su.email or "(no email)")
    c2 = Client(HTTP_HOST="127.0.0.1")
    c2.force_login(su)
    run(c2, ["/dashboard/", "/admin/"] + ([f"/verify/{b.id}/"] if b else []))
else:
    print("No superuser. Run: python manage.py createsuperuser")