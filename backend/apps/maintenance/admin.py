from django.contrib import admin
from .models import MaintenanceRecord, TrackedItem


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'maintenance_type', 'date', 'mileage_at_service', 'cost', 'next_due_date']
    list_filter = ['maintenance_type', 'date']
    search_fields = ['vehicle__name', 'vehicle__registration_number', 'description']
    date_hierarchy = 'date'


@admin.register(TrackedItem)
class TrackedItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle', 'interval_km', 'interval_months', 'status', 'last_service_km', 'last_service_date']
    list_filter = ['status']
    search_fields = ['name', 'vehicle__name']
