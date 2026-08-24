from django.db import models
from django.contrib.auth.models import User
from apps.vehicles.models import Vehicle


class Insurance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='insurances', verbose_name='Véhicule')
    company_name = models.CharField("Compagnie d'assurance", max_length=200)
    policy_number = models.CharField('Numéro de police', max_length=100)
    start_date = models.DateField('Date de début')
    end_date = models.DateField("Date d'expiration")
    premium_amount = models.DecimalField('Prime (€/an)', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Active', default=True)
    document = models.FileField('Document', upload_to='documents/insurances/', blank=True)
    notes = models.TextField('Notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assurance'
        verbose_name_plural = 'Assurances'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.company_name} - {self.vehicle}"


class CarteGrise(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='carte_grise', verbose_name='Véhicule')
    registration_number = models.CharField("Numéro d'immatriculation", max_length=20)
    issue_date = models.DateField("Date de délivrance")
    expiry_date = models.DateField("Date d'expiration", null=True, blank=True)
    document = models.FileField('Document', upload_to='documents/cartes_grises/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carte Grise'
        verbose_name_plural = 'Cartes Grises'

    def __str__(self):
        return f"Carte Grise {self.registration_number}"


class TechnicalInspection(models.Model):
    class Result(models.TextChoices):
        PASSED = 'passed', 'Favorable'
        FAILED = 'failed', 'Défavorable'
        PARTIAL = 'partial', 'Favorable avec réserves'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='technical_inspections', verbose_name='Véhicule')
    inspection_date = models.DateField("Date du contrôle")
    result = models.CharField('Résultat', max_length=10, choices=Result.choices)
    expiry_date = models.DateField("Date d'expiration")
    mileage_at_inspection = models.IntegerField('Kilométrage lors du contrôle', null=True, blank=True)
    garage_name = models.CharField('Centre de contrôle', max_length=200, blank=True)
    document = models.FileField('Document', upload_to='documents/inspections/', blank=True)
    notes = models.TextField('Notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contrôle Technique'
        verbose_name_plural = 'Contrôles Techniques'
        ordering = ['-inspection_date']

    def __str__(self):
        return f"CT {self.vehicle} - {self.inspection_date}"
