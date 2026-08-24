from django.contrib import admin

from apps.parts.models import Part, PartCategory, PartCompatibility


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'reference', 'price', 'vehicle_type']
    list_filter = ['category', 'vehicle_type']
    search_fields = ['name', 'brand', 'reference']


@admin.register(PartCompatibility)
class PartCompatibilityAdmin(admin.ModelAdmin):
    list_display = ['part', 'vehicle']
    autocomplete_fields = ['part']