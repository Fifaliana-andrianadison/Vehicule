from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle
from .forms import VehicleForm


def get_brands():
    return Vehicle.objects.values_list('brand', flat=True).distinct().order_by('brand')


@login_required
def vehicle_select(request):
    return render(request, 'vehicles/select.html')


@login_required
def vehicle_list(request):
    vehicles = request.user.vehicles.all()
    return render(request, 'vehicles/list.html', {'vehicles': vehicles})


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    last_oil = vehicle.get_last_oil_change()
    active_insurance = vehicle.get_active_insurance()
    last_inspection = vehicle.get_latest_inspection()
    maintenance_count = vehicle.maintenance_records.count()
    total_cost = sum(r.cost or 0 for r in vehicle.maintenance_records.all())
    return render(request, 'vehicles/detail.html', {
        'vehicle': vehicle,
        'last_oil': last_oil,
        'active_insurance': active_insurance,
        'last_inspection': last_inspection,
        'maintenance_count': maintenance_count,
        'total_cost': total_cost,
        'today': date.today(),
    })


@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            vehicle.save()
            messages.success(request, 'Véhicule ajouté avec succès !')
            return redirect('vehicles:detail', pk=vehicle.pk)
    else:
        form = VehicleForm()
    return render(request, 'vehicles/form.html', {'form': form, 'title': 'Ajouter un véhicule', 'brands': get_brands()})


@login_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Véhicule modifié avec succès !')
            return redirect('vehicles:detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'vehicles/form.html', {'form': form, 'title': 'Modifier le véhicule', 'brands': get_brands()})


@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Véhicule supprimé.')
        return redirect('vehicles:list')
    return render(request, 'vehicles/confirm_delete.html', {'vehicle': vehicle})
