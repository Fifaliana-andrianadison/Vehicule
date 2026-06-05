from django.db import models
from django.contrib.auth.models import User
from vehicles.models import Vehicle


class MaintenanceRecord(models.Model):
    class MaintenanceType(models.TextChoices):
        OIL_CHANGE = 'oil_change', 'Vidange'
        BRAKE = 'brake', 'Freins'
        TIRE = 'tire', 'Pneus'
        BELT = 'belt', 'Courroie de distribution'
        BATTERY = 'battery', 'Batterie'
        FILTER = 'filter', 'Filtres'
        CLUTCH = 'clutch', 'Embrayage'
        SUSPENSION = 'suspension', 'Suspension'
        EXHAUST = 'exhaust', 'Échappement'
        ELECTRIC = 'electric', 'Système électrique'
        AIR_CONDITIONING = 'air_conditioning', 'Climatisation'
        TIMING_BELT = 'timing_belt', 'Distribution'
        COOLING = 'cooling', 'Refroidissement'
        OTHER = 'other', 'Autre'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name='Véhicule')
    maintenance_type = models.CharField('Type', max_length=30, choices=MaintenanceType.choices)
    description = models.CharField('Description', max_length=200, blank=True)
    date = models.DateField('Date')
    mileage_at_service = models.IntegerField('Kilométrage lors de l\'intervention')
    cost = models.DecimalField('Coût (€)', max_digits=10, decimal_places=2, null=True, blank=True)
    garage_name = models.CharField('Garage', max_length=200, blank=True)
    next_due_mileage = models.IntegerField('Prochain kilométrage recommandé', null=True, blank=True)
    next_due_date = models.DateField('Prochaine date recommandée', null=True, blank=True)
    notes = models.TextField('Notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Entretien'
        verbose_name_plural = 'Entretiens'
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_maintenance_type_display()} - {self.vehicle} ({self.date})"
