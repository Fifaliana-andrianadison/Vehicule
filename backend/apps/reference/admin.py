from django.contrib import admin

from apps.reference.models import VehicleReference, MaintenanceSchedule


class MaintenanceScheduleInline(admin.TabularInline):
    model = MaintenanceSchedule
    extra = 0


@admin.register(VehicleReference)
class VehicleReferenceAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'vehicle_type', 'year_start', 'year_end', 'body_type']
    list_filter = ['vehicle_type', 'brand']
    search_fields = ['brand', 'model']
    inlines = [MaintenanceScheduleInline]


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ['label', 'vehicle_reference', 'intervention_type', 'interval_km', 'interval_months']