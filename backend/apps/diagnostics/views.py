from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from vehicles.models import Vehicle
from diagnostics.models import DiagnosticReport
from diagnostics.utils import get_vehicle_health


@login_required
def diagnostic_view(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk, user=request.user)
    health = get_vehicle_health(vehicle)

    DiagnosticReport.objects.create(
        vehicle=vehicle,
        overall_status=health['overall_status'],
        mileage=health['mileage'],
        oil_change_status=health['oil_change_status'],
        inspection_status=health['inspection_status'],
        insurance_status=health['insurance_status'],
        registration_status=health['registration_status'],
        days_until_next_oil_change=health['days_until_next_oil_change'],
        km_until_next_oil_change=health['km_until_next_oil_change'],
        days_until_inspection=health['days_until_inspection'],
        days_until_insurance_expiry=health['days_until_insurance_expiry'],
        recommendations=health['recommendations'],
        is_critical=health['is_critical'],
    )

    return render(request, 'diagnostics/report.html', {
        'vehicle': vehicle,
        'health': health,
    })


@login_required
def diagnostic_history(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk, user=request.user)
    reports = vehicle.diagnostic_reports.all()[:20]
    return render(request, 'diagnostics/history.html', {
        'vehicle': vehicle,
        'reports': reports,
    })
