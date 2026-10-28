from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Vehicle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    battery_kwh = models.FloatField(help_text="Battery capacity in kWh")
    connector_type = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

class Station(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    charger_type = models.CharField(max_length=30)       # e.g. CCS2, Type2
    power_kw = models.FloatField()                        # charger speed
    price_per_kwh = models.FloatField()
    total_slots = models.PositiveIntegerField(default=2)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS = [('booked', 'Booked'), ('charging', 'Charging'),
              ('done', 'Completed'), ('cancelled', 'Cancelled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    current_battery = models.PositiveIntegerField()       # %
    target_battery = models.PositiveIntegerField(default=100)
    est_cost = models.FloatField(default=0)
    status = models.CharField(max_length=10, choices=STATUS, default='booked')

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()                # 1-5
    comment = models.TextField(blank=True)

# Create your models here.
