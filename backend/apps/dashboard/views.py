from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import date, timedelta
from apps.vehicles.models import Vehicle
from apps.maintenance.models import MaintenanceRecord
from apps.documents.models import Insurance, TechnicalInspection
from apps.diagnostics.utils import get_vehicle_health


@login_required
def home(request):
    vehicles = request.user.vehicles.all()
    total_vehicles = vehicles.count()
    total_maintenance = MaintenanceRecord.objects.filter(vehicle__user=request.user).count()
    total_cost = MaintenanceRecord.objects.filter(vehicle__user=request.user).aggregate(Sum('cost'))['cost__sum'] or 0

    critical_count = 0
    warning_count = 0
    vehicle_statuses = []

    for v in vehicles:
        health = get_vehicle_health(v)
        vehicle_statuses.append({'vehicle': v, 'health': health})
        if health['is_critical']:
            critical_count += 1
        elif health['overall_status'] == 'warning':
            warning_count += 1

    today = date.today()
    upcoming_reminders = []

    for v in vehicles:
        last_oil = v.get_last_oil_change()
        if last_oil and last_oil.next_due_date:
            days = (last_oil.next_due_date - today).days
            if 0 <= days <= 30:
                upcoming_reminders.append({
                    'vehicle': v,
                    'type': 'Vidange',
                    'due_date': last_oil.next_due_date,
                    'days_left': days,
                })

        last_inspection = v.get_latest_inspection()
        if last_inspection and last_inspection.expiry_date:
            days = (last_inspection.expiry_date - today).days
            if 0 <= days <= 90:
                upcoming_reminders.append({
                    'vehicle': v,
                    'type': 'Contrôle technique',
                    'due_date': last_inspection.expiry_date,
                    'days_left': days,
                })

        active_ins = v.get_active_insurance()
        if active_ins:
            days = (active_ins.end_date - today).days
            if 0 <= days <= 30:
                upcoming_reminders.append({
                    'vehicle': v,
                    'type': 'Assurance',
                    'due_date': active_ins.end_date,
                    'days_left': days,
                })

    upcoming_reminders.sort(key=lambda x: x['days_left'])

    recent_maintenance = MaintenanceRecord.objects.filter(
        vehicle__user=request.user
    ).select_related('vehicle')[:10]

    context = {
        'total_vehicles': total_vehicles,
        'total_maintenance': total_maintenance,
        'total_cost': total_cost,
        'critical_count': critical_count,
        'warning_count': warning_count,
        'vehicle_statuses': vehicle_statuses,
        'upcoming_reminders': upcoming_reminders,
        'recent_maintenance': recent_maintenance,
    }
    return render(request, 'dashboard/home.html', context)
