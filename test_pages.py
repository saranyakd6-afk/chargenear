from django.test import Client
from django.contrib.auth.models import User
from core.models import Booking

c = Client(HTTP_HOST='localhost')
c.login(username='arjun', password='demo12345')
b = Booking.objects.filter(user__username='arjun').first()

for u in ['/my-bookings/', '/planner/', '/vehicle/add/',
          '/book/1/', f'/ticket/{b.id}/', f'/booking/{b.id}/qr/']:
    print(u, c.get(u).status_code)

staff = User.objects.filter(is_staff=True).first()
c.force_login(staff)
for u in ['/dashboard/', f'/verify/{b.id}/']:
    print(u, c.get(u).status_code)