from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'model', 'registration_number', 'user', 'mileage', 'is_active']
    list_filter = ['vehicle_type', 'fuel_type', 'is_active', 'year']
    search_fields = ['name', 'brand', 'model', 'registration_number', 'vin']
    date_hierarchy = 'created_at'
