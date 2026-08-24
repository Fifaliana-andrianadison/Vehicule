from datetime import date, timedelta
from collections import defaultdict
from decimal import Decimal

from django.db.models import Q, Sum
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.vehicles.models import Vehicle
from apps.vehicles import services as nhtsa
from apps.vehicles.serializers import (
    VehicleSerializer, VehicleCreateSerializer,
    MaintenanceSerializer, ExpenseSerializer, TrackedItemSerializer,
)
from apps.maintenance.models import MaintenanceRecord, TrackedItem
from apps.expenses.models import Expense, ExpenseCategory


def get_owned_vehicle(request, pk):
    return get_object_or_404(Vehicle, pk=pk, user=request.user)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vehicle_list(request):
    if request.method == 'GET':
        q = request.GET.get('q', '').strip()
        vehicles = Vehicle.objects.filter(user=request.user).order_by('-created_at')
        if q:
            vehicles = vehicles.filter(
                Q(brand__icontains=q) | Q(model__icontains=q) | Q(name__icontains=q)
            )
        return Response(VehicleSerializer(vehicles, many=True).data)

    serializer = VehicleCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def vehicle_detail(request, pk):
    vehicle = get_owned_vehicle(request, pk)
    if request.method == 'DELETE':
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == 'PATCH':
        serializer = VehicleCreateSerializer(vehicle, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(VehicleSerializer(vehicle).data)
    return Response(VehicleSerializer(vehicle).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_dashboard(request, pk):
    vehicle = get_owned_vehicle(request, pk)

    expenses = vehicle.expenses.all()
    maintenance = vehicle.maintenance_records.all()

    total_expenses = expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_maintenance = maintenance.aggregate(t=Sum('cost'))['t'] or Decimal('0')
    total_cost = total_expenses + total_maintenance

    by_category = defaultdict(Decimal)
    for e in expenses:
        by_category[e.category.name] += e.amount
    for m in maintenance:
        if m.cost:
            by_category[m.get_maintenance_type_display()] += m.cost

    by_month = defaultdict(Decimal)
    for e in expenses:
        by_month[e.date.strftime('%Y-%m')] += e.amount
    for m in maintenance:
        if m.cost:
            by_month[m.date.strftime('%Y-%m')] += m.cost

    months = sorted(by_month.keys(), reverse=True)
    month_labels = []
    month_values = []
    if months:
        start = months[-1]
        end = months[0]
        cur = date.fromisoformat(f"{start}-01")
        end_dt = date.fromisoformat(f"{end}-01")
        while cur <= end_dt:
            key = cur.strftime('%Y-%m')
            month_labels.append(key)
            month_values.append(float(by_month.get(key, 0)))
            if cur.month == 12:
                cur = cur.replace(year=cur.year + 1, month=1)
            else:
                cur = cur.replace(month=cur.month + 1)

    from apps.diagnostics.utils import get_vehicle_health
    health = get_vehicle_health(vehicle)

    data = {
        'vehicle': VehicleSerializer(vehicle).data,
        'health': health,
        'totals': {
            'total_expenses': float(total_expenses),
            'total_maintenance': float(total_maintenance),
            'total_cost': float(total_cost),
            'count_maintenance': maintenance.count(),
            'count_expenses': expenses.count(),
        },
        'by_category': {k: float(v) for k, v in sorted(by_category.items(), key=lambda x: -x[1])},
        'by_month': {'labels': month_labels, 'values': month_values},
        'recent_maintenance': MaintenanceSerializer(maintenance[:5], many=True).data,
        'recent_expenses': ExpenseSerializer(expenses[:5], many=True).data,
    }
    return Response(data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vehicle_maintenances(request, pk):
    vehicle = get_owned_vehicle(request, pk)
    if request.method == 'POST':
        serializer = MaintenanceSerializer(data=request.data, context={'vehicle': vehicle})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    qs = vehicle.maintenance_records.all()
    mtype = request.GET.get('type')
    if mtype:
        qs = qs.filter(maintenance_type=mtype)
    return Response(MaintenanceSerializer(qs, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vehicle_expenses(request, pk):
    vehicle = get_owned_vehicle(request, pk)
    if request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data, context={'vehicle': vehicle})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    qs = vehicle.expenses.select_related('category').all()
    category = request.GET.get('category')
    if category:
        qs = qs.filter(category_id=category)
    return Response(ExpenseSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_expenses_summary(request, pk):
    vehicle = get_owned_vehicle(request, pk)
    qs = vehicle.expenses.select_related('category').all()
    total = qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    by_category = defaultdict(Decimal)
    by_month = defaultdict(Decimal)
    for e in qs:
        by_category[e.category.name] += e.amount
        by_month[e.date.strftime('%Y-%m')] += e.amount
    month = request.GET.get('month')
    filtered = qs
    if month:
        filtered = qs.filter(date__year=int(month[:4]), date__month=int(month[5:7]))
    return Response({
        'total': float(total),
        'count': qs.count(),
        'by_category': {k: float(v) for k, v in by_category.items()},
        'by_month': {k: float(v) for k, v in sorted(by_month.items())},
        'current_month_total': float(filtered.aggregate(t=Sum('amount'))['t'] or 0),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_alerts(request, pk):
    vehicle = get_owned_vehicle(request, pk)
    today = date.today()
    alerts = []

    for item in vehicle.tracked_items.all():
        ratio = 0.0
        if item.interval_km and item.last_service_km is not None:
            ratio = max(ratio, (vehicle.mileage - item.last_service_km) / item.interval_km)
        if item.interval_months and item.last_service_date:
            ratio = max(ratio, (today - item.last_service_date).days / (item.interval_months * 30.44))
        alerts.append({
            'type': 'item',
            'item_id': item.id,
            'title': item.name,
            'severity': item.compute_status(vehicle.mileage, today),
            'progress': round(ratio * 100),
            'message': f"{item.name} - {item.get_status_display()}",
            'date': item.last_service_date,
        })

    for m in vehicle.maintenance_records.filter(next_due_date__isnull=False):
        days_left = (m.next_due_date - today).days
        severity = 'critical' if days_left < 0 else ('warning' if days_left <= 30 else 'up_to_date')
        alerts.append({
            'type': 'maintenance',
            'title': f"{m.get_maintenance_type_display()} due",
            'severity': severity,
            'progress': 0,
            'message': f"{m.get_maintenance_type_display()} prévue le {m.next_due_date}",
            'date': m.next_due_date,
        })

    ins = vehicle.insurances.filter(is_active=True).first()
    if ins:
        days_left = (ins.end_date - today).days
        severity = 'critical' if days_left < 0 else ('warning' if days_left <= 30 else 'up_to_date')
        alerts.append({
            'type': 'insurance', 'title': 'Assurance', 'severity': severity,
            'progress': 0,
            'message': f"Assurance {ins.company_name} expire le {ins.end_date}",
            'date': ins.end_date,
        })

    insp = vehicle.technical_inspections.order_by('-inspection_date').first()
    if insp and insp.expiry_date:
        days_left = (insp.expiry_date - today).days
        severity = 'critical' if days_left < 0 else ('warning' if days_left <= 90 else 'up_to_date')
        alerts.append({
            'type': 'inspection', 'title': 'Contrôle technique', 'severity': severity,
            'progress': 0,
            'message': f"Contrôle technique expire le {insp.expiry_date}",
            'date': insp.expiry_date,
        })

    cg = getattr(vehicle, 'carte_grise', None)
    if cg and cg.expiry_date:
        days_left = (cg.expiry_date - today).days
        severity = 'critical' if days_left < 0 else ('warning' if days_left <= 90 else 'up_to_date')
        alerts.append({
            'type': 'registration', 'title': 'Carte grise', 'severity': severity,
            'progress': 0,
            'message': f"Carte grise expire le {cg.expiry_date}",
            'date': cg.expiry_date,
        })

    order = {'critical': 0, 'warning': 1, 'up_to_date': 2}
    alerts.sort(key=lambda a: (order.get(a['severity'], 3), a['date'] or today))
    return Response(alerts)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nhtsa_makes(request):
    vehicle_type = request.GET.get('type', 'car')
    results = nhtsa.get_makes_for_vehicle_type(vehicle_type)
    makes = sorted({r.get('MakeName') for r in results if r.get('MakeName')})
    return Response({'type': vehicle_type, 'makes': makes})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nhtsa_models(request):
    make = request.GET.get('make', '')
    vehicle_type = request.GET.get('type', 'car')
    year = request.GET.get('year')
    if not make:
        return Response({'error': 'Paramètre make requis'}, status=400)
    if year:
        results = nhtsa.get_models_for_make_year(make, year, vehicle_type)
    else:
        results = nhtsa.get_models_for_make(make)
    models = sorted({r.get('Model_Name') for r in results if r.get('Model_Name')})
    return Response({'make': make, 'type': vehicle_type, 'year': year, 'models': models})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nhtsa_decode_vin(request, vin):
    data = nhtsa.decode_vin_to_vehicle_data(vin)
    if not data:
        return Response({'error': 'VIN non décodable'}, status=404)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_search(request):
    q = request.GET.get('q', '').strip()
    vehicles = Vehicle.objects.filter(user=request.user)
    if q:
        words = q.split()
        query = Q()
        for word in words:
            query |= Q(brand__icontains=word)
            query |= Q(model__icontains=word)
            query |= Q(name__icontains=word)
        vehicles = vehicles.filter(query)
    vehicles = vehicles.distinct().order_by('brand', 'model')[:20]
    return Response(VehicleSerializer(vehicles, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tracked_items(request, pk):
    vehicle = get_owned_vehicle(request, pk)
    if request.method == 'POST':
        data = request.data.copy()
        data['vehicle'] = vehicle.id
        serializer = TrackedItemSerializer(data=data, context={'vehicle': vehicle})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    items = vehicle.tracked_items.all()
    return Response(TrackedItemSerializer(items, many=True, context={'vehicle': vehicle}).data)