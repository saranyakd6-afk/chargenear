from django.test import Client
from django.contrib.auth.models import User
from core.models import Booking, Station

c = Client(HTTP_HOST="127.0.0.1")
print("login:", c.login(username="arjun", password="demo12345"))
b = Booking.objects.filter(user__username="arjun").first()
s = Station.objects.first()

urls = ["/", "/stations/", f"/station/{s.id}/", f"/book/{s.id}/", "/my-bookings/",
        "/planner/", "/vehicle/add/", "/accounts/login/", "/register/"]
if b:
    urls += [f"/ticket/{b.id}/", f"/booking/{b.id}/qr/"]

def test(urls):
    for u in urls:
        try:
            print(c.get(u).status_code, u)
        except Exception as e:
            print("ERROR", u, "->", type(e).__name__, e)

test(urls)

su = User.objects.filter(is_superuser=True).first()
if su:
    c.force_login(su)
    test(["/dashboard/"] + ([f"/verify/{b.id}/"] if b else []))