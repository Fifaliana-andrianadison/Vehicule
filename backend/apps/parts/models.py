from django.db import models
from apps.vehicles.models import Vehicle


class PartCategory(models.Model):
    name = models.CharField('Nom', max_length=100, unique=True)
    description = models.TextField('Description', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catégorie de pièce'
        verbose_name_plural = 'Catégories de pièces'
        ordering = ['name']

    def __str__(self):
        return self.name


class Part(models.Model):
    class VehicleType(models.TextChoices):
        CAR = 'car', 'Voiture'
        MOTORCYCLE = 'motorcycle', 'Moto'
        TRUCK = 'truck', 'Camion'
        VAN = 'van', 'Utilitaire'
        BUS = 'bus', 'Bus'
        OTHER = 'other', 'Autre'
        ALL = '', 'Tous types'

    name = models.CharField('Nom', max_length=200)
    category = models.ForeignKey(
        PartCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='parts', verbose_name='Catégorie',
    )
    reference = models.CharField('Référence', max_length=100, blank=True)
    brand = models.CharField('Marque', max_length=100, blank=True)
    vehicle_type = models.CharField(
        'Type de véhicule', max_length=20, choices=VehicleType.choices,
        default=VehicleType.ALL, blank=True,
    )
    description = models.TextField('Description', blank=True)
    price = models.DecimalField('Prix (€)', max_digits=10, decimal_places=2, null=True, blank=True)
    compatible_vehicles = models.ManyToManyField(
        Vehicle, through='PartCompatibility', blank=True,
        related_name='parts', verbose_name='Véhicules compatibles',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pièce'
        verbose_name_plural = 'Pièces'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.reference or 'sans réf.'})"

    def is_compatible_with(self, vehicle):
        if self.compatible_vehicles.filter(pk=vehicle.pk).exists():
            return True
        if not self.compatible_vehicles.exists():
            return not self.vehicle_type or self.vehicle_type == vehicle.vehicle_type
        return False


class PartCompatibility(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='compatibilities')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='compatible_parts')
    notes = models.CharField('Notes', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Compatibilité pièce'
        verbose_name_plural = 'Compatibilités pièces'
        unique_together = ('part', 'vehicle')

    def __str__(self):
        return f"{self.part} → {self.vehicle}"