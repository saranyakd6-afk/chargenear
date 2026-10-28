from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "ChargeNear Admin"
admin.site.site_title = "ChargeNear"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]