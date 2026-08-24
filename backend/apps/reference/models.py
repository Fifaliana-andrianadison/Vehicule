from django.db import models
from apps.vehicles.models import Vehicle


class VehicleReference(models.Model):
    class VehicleType(models.TextChoices):
        CAR = 'car', 'Voiture'
        MOTORCYCLE = 'motorcycle', 'Moto'
        TRUCK = 'truck', 'Camion'
        VAN = 'van', 'Utilitaire'
        BUS = 'bus', 'Bus'
        OTHER = 'other', 'Autre'

    vehicle_type = models.CharField('Type', max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    brand = models.CharField('Marque', max_length=100)
    model = models.CharField('Modèle', max_length=100)
    year_start = models.IntegerField('Année début', null=True, blank=True)
    year_end = models.IntegerField('Année fin', null=True, blank=True)
    engine_info = models.CharField('Motorisation', max_length=200, blank=True)
    body_type = models.CharField('Carrosserie', max_length=100, blank=True)
    description = models.TextField('Description', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fiche véhicule (encyclopédie)'
        verbose_name_plural = 'Fiches véhicules (encyclopédie)'
        ordering = ['brand', 'model', 'year_start']
        unique_together = ('vehicle_type', 'brand', 'model', 'year_start', 'year_end')

    def __str__(self):
        span = f"{self.year_start}-{self.year_end}" if self.year_start else ''
        return f"{self.brand} {self.model} {span}".strip()


class MaintenanceSchedule(models.Model):
    INTERVENTION_TYPES = [
        ('oil_change', 'Vidange'),
        ('brake', 'Freins'),
        ('tire', 'Pneus'),
        ('belt', 'Courroie'),
        ('timing_belt', 'Distribution'),
        ('battery', 'Batterie'),
        ('filter', 'Filtres'),
        ('clutch', 'Embrayage'),
        ('suspension', 'Suspension'),
        ('exhaust', 'Échappement'),
        ('electric', 'Système électrique'),
        ('air_conditioning', 'Climatisation'),
        ('cooling', 'Refroidissement'),
        ('other', 'Autre'),
    ]

    vehicle_reference = models.ForeignKey(
        VehicleReference, on_delete=models.CASCADE, related_name='schedule',
        verbose_name='Véhicule',
    )
    intervention_type = models.CharField('Intervention', max_length=30, choices=INTERVENTION_TYPES)
    label = models.CharField('Libellé', max_length=100)
    interval_km = models.IntegerField('Intervalle (km)', null=True, blank=True)
    interval_months = models.IntegerField('Intervalle (mois)', null=True, blank=True)
    cost_estimate = models.DecimalField('Coût estimé (€)', max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Plan d\'entretien'
        verbose_name_plural = 'Plans d\'entretien'
        ordering = ['intervention_type']

    def __str__(self):
        return f"{self.label} ({self.vehicle_reference})"

    @staticmethod
    def for_vehicle(vehicle):
        return MaintenanceSchedule.objects.filter(
            vehicle_reference__brand__iexact=vehicle.brand,
            vehicle_reference__model__iexact=vehicle.model,
        )