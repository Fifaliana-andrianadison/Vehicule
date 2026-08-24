from django.contrib import admin
from .models import Vehicle, VehicleType, Brand, VehicleModel


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'model', 'registration_number', 'user', 'mileage', 'is_active']
    list_filter = ['vehicle_type', 'fuel_type', 'is_active', 'year']
    search_fields = ['name', 'brand', 'model', 'registration_number', 'vin']
    date_hierarchy = 'created_at'


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'label']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'nhtsa_id']
    search_fields = ['name']
    filter_horizontal = ['vehicle_types']


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'year', 'vehicle_type']
    search_fields = ['name', 'brand__name']
    list_filter = ['year', 'vehicle_type']