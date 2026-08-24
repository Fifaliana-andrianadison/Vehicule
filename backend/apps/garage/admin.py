from django.contrib import admin

from apps.garage.models import Garage, GarageStaff, RepairOrder, RepairOrderPart


class RepairOrderPartInline(admin.TabularInline):
    model = RepairOrderPart
    extra = 0


@admin.register(Garage)
class GarageAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'phone', 'email']
    search_fields = ['name', 'owner__username']


@admin.register(GarageStaff)
class GarageStaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'garage', 'role', 'is_active']
    list_filter = ['role', 'is_active']


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'vehicle', 'customer', 'garage', 'status', 'total_cost', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'vehicle__name', 'customer__username']
    inlines = [RepairOrderPartInline]


@admin.register(RepairOrderPart)
class RepairOrderPartAdmin(admin.ModelAdmin):
    list_display = ['name', 'repair_order', 'quantity', 'unit_price']