from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MaintenanceRecord
from .forms import MaintenanceForm


@login_required
def maintenance_list(request):
    records = MaintenanceRecord.objects.filter(vehicle__user=request.user).select_related('vehicle')
    return render(request, 'maintenance/list.html', {'records': records})


@login_required
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entretien enregistré avec succès !')
            return redirect('maintenance:list')
    else:
        form = MaintenanceForm(user=request.user)
    return render(request, 'maintenance/form.html', {'form': form, 'title': 'Ajouter un entretien'})


@login_required
def maintenance_update(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        form = MaintenanceForm(user=request.user, data=request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entretien modifié avec succès !')
            return redirect('maintenance:list')
    else:
        form = MaintenanceForm(user=request.user, instance=record)
    return render(request, 'maintenance/form.html', {'form': form, 'title': 'Modifier lentretien'})


@login_required
def maintenance_delete(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Entretien supprimé.')
        return redirect('maintenance:list')
    return render(request, 'maintenance/confirm_delete.html', {'record': record})


@login_required
def maintenance_by_vehicle(request, vehicle_pk):
    records = MaintenanceRecord.objects.filter(vehicle__pk=vehicle_pk, vehicle__user=request.user).select_related('vehicle')
    return render(request, 'maintenance/list.html', {'records': records})
