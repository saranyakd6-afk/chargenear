from django.urls import path, include
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns =  [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('accounts/login/', views.SmartLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('stations/', views.station_list, name='stations'),
    path('station/<int:pk>/', views.station_detail, name='station_detail'),
    path('vehicle/add/', views.add_vehicle, name='add_vehicle'),
    path('book/<int:pk>/', views.book_station, name='book'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:pk>/', views.cancel_booking, name='cancel'),
    path('planner/', views.trip_planner, name='planner'),
    path('api/plan/', views.plan_trip_api, name='plan_api'),
    path('ticket/<int:pk>/', views.ticket, name='ticket'),
    path('booking/<int:pk>/qr/', views.booking_qr, name='booking_qr'),
    path('verify/<int:pk>/', views.verify_booking, name='verify'),
    path('dashboard/', views.dashboard, name='dashboard'),
   


]
