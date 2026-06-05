from django.db import models
from django.contrib.auth.models import User


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        CAR = 'car', 'Voiture'
        MOTORCYCLE = 'motorcycle', 'Moto'
        TRUCK = 'truck', 'Camion'
        VAN = 'van', 'Utilitaire'
        BUS = 'bus', 'Bus'
        OTHER = 'other', 'Autre'

    class FuelType(models.TextChoices):
        GASOLINE = 'gasoline', 'Essence'
        DIESEL = 'diesel', 'Diesel'
        ELECTRIC = 'electric', 'Électrique'
        HYBRID = 'hybrid', 'Hybride'
        LPG = 'lpg', 'GPL'
        OTHER = 'other', 'Autre'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles', verbose_name='Propriétaire')
    name = models.CharField('Nom du véhicule', max_length=100)
    brand = models.CharField('Marque', max_length=100)
    model = models.CharField('Modèle', max_length=100)
    year = models.IntegerField('Année')
    vehicle_type = models.CharField('Type', max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    fuel_type = models.CharField('Carburant', max_length=20, choices=FuelType.choices, default=FuelType.GASOLINE)
    vin = models.CharField('Numéro VIN', max_length=17, blank=True)
    registration_number = models.CharField("Numéro d'immatriculation", max_length=20, blank=True)
    mileage = models.IntegerField('Kilométrage', default=0)
    photo = models.ImageField('Photo', upload_to='vehicles/', blank=True)
    purchase_date = models.DateField("Date d'achat", null=True, blank=True)
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number or 'Sans plaque'})"

    def get_health_status(self):
        from diagnostics.utils import get_vehicle_health
        return get_vehicle_health(self)

    def get_last_oil_change(self):
        return self.maintenance_records.filter(
            maintenance_type='oil_change'
        ).order_by('-date').first()

    def get_active_insurance(self):
        from datetime import date
        return self.insurances.filter(
            is_active=True,
            end_date__gte=date.today()
        ).first()

    def get_latest_inspection(self):
        return self.technical_inspections.order_by('-inspection_date').first()
