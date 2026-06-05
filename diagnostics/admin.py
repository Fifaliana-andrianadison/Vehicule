from django.contrib import admin
from .models import DiagnosticReport


@admin.register(DiagnosticReport)
class DiagnosticReportAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'report_date', 'overall_status', 'is_critical']
    list_filter = ['overall_status', 'is_critical']
    search_fields = ['vehicle__name']
    date_hierarchy = 'report_date'
