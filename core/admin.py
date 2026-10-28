from django.contrib import admin
from .models import Vehicle, Station, Booking, Review

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    can_delete = False
    fields = ('user', 'vehicle', 'start_time', 'end_time', 'est_cost', 'status')
    readonly_fields = ('user', 'vehicle', 'start_time', 'end_time', 'est_cost')

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'charger_type', 'power_kw', 'price_per_kwh',
                    'total_slots', 'is_open')
    list_editable = ('price_per_kwh', 'total_slots', 'is_open')  # quick edit
    list_filter = ('charger_type', 'is_open')
    search_fields = ('name', 'address')
    inlines = [BookingInline]   # see bookings + vehicles per station

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'station', 'start_time', 'end_time',
                    'est_cost', 'status')
    list_filter = ('status', 'station')
    search_fields = ('user__username', 'vehicle__name')
    date_hierarchy = 'start_time'
    actions = ['mark_charging', 'mark_done']