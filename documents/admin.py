from django.contrib import admin
from .models import Insurance, CarteGrise, TechnicalInspection


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'company_name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'company_name']
    search_fields = ['vehicle__name', 'policy_number', 'company_name']


@admin.register(CarteGrise)
class CarteGriseAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'registration_number', 'issue_date', 'expiry_date']
    search_fields = ['vehicle__name', 'registration_number']


@admin.register(TechnicalInspection)
class TechnicalInspectionAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'inspection_date', 'result', 'expiry_date']
    list_filter = ['result']
    search_fields = ['vehicle__name', 'garage_name']
    date_hierarchy = 'inspection_date'
