from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Insurance, CarteGrise, TechnicalInspection
from .forms import InsuranceForm, CarteGriseForm, TechnicalInspectionForm


@login_required
def documents_list(request):
    insurances = Insurance.objects.filter(vehicle__user=request.user).select_related('vehicle')
    inspections = TechnicalInspection.objects.filter(vehicle__user=request.user).select_related('vehicle')
    cartes_grise = CarteGrise.objects.filter(vehicle__user=request.user).select_related('vehicle')
    return render(request, 'documents/list.html', {
        'insurances': insurances,
        'inspections': inspections,
        'cartes_grise': cartes_grise,
        'today': date.today(),
    })


@login_required
def insurance_create(request):
    if request.method == 'POST':
        form = InsuranceForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assurance ajoutée avec succès !')
            return redirect('documents:list')
    else:
        form = InsuranceForm(user=request.user)
    return render(request, 'documents/insurance_form.html', {'form': form, 'title': 'Ajouter une assurance'})


@login_required
def insurance_update(request, pk):
    insurance = get_object_or_404(Insurance, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        form = InsuranceForm(user=request.user, data=request.POST, files=request.FILES, instance=insurance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assurance modifiée avec succès !')
            return redirect('documents:list')
    else:
        form = InsuranceForm(user=request.user, instance=insurance)
    return render(request, 'documents/insurance_form.html', {'form': form, 'title': "Modifier l'assurance"})


@login_required
def insurance_delete(request, pk):
    insurance = get_object_or_404(Insurance, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        insurance.delete()
        messages.success(request, 'Assurance supprimée.')
    return redirect('documents:list')


@login_required
def carte_grise_create(request):
    if request.method == 'POST':
        form = CarteGriseForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carte grise ajoutée avec succès !')
            return redirect('documents:list')
    else:
        form = CarteGriseForm(user=request.user)
    return render(request, 'documents/carte_grise_form.html', {'form': form, 'title': 'Ajouter une carte grise'})


@login_required
def carte_grise_update(request, pk):
    carte_grise = get_object_or_404(CarteGrise, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        form = CarteGriseForm(user=request.user, data=request.POST, files=request.FILES, instance=carte_grise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carte grise modifiée avec succès !')
            return redirect('documents:list')
    else:
        form = CarteGriseForm(user=request.user, instance=carte_grise)
    return render(request, 'documents/carte_grise_form.html', {'form': form, 'title': 'Modifier la carte grise'})


@login_required
def carte_grise_delete(request, pk):
    carte_grise = get_object_or_404(CarteGrise, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        carte_grise.delete()
        messages.success(request, 'Carte grise supprimée.')
    return redirect('documents:list')


@login_required
def inspection_create(request):
    if request.method == 'POST':
        form = TechnicalInspectionForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrôle technique ajouté avec succès !')
            return redirect('documents:list')
    else:
        form = TechnicalInspectionForm(user=request.user)
    return render(request, 'documents/inspection_form.html', {'form': form, 'title': 'Ajouter un contrôle technique'})


@login_required
def inspection_update(request, pk):
    inspection = get_object_or_404(TechnicalInspection, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        form = TechnicalInspectionForm(user=request.user, data=request.POST, files=request.FILES, instance=inspection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrôle technique modifié avec succès !')
            return redirect('documents:list')
    else:
        form = TechnicalInspectionForm(user=request.user, instance=inspection)
    return render(request, 'documents/inspection_form.html', {'form': form, 'title': "Modifier le contrôle technique"})


@login_required
def inspection_delete(request, pk):
    inspection = get_object_or_404(TechnicalInspection, pk=pk, vehicle__user=request.user)
    if request.method == 'POST':
        inspection.delete()
        messages.success(request, 'Contrôle technique supprimé.')
    return redirect('documents:list')
