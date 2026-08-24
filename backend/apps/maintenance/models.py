from django.db import models
from django.contrib.auth.models import User
from apps.vehicles.models import Vehicle


class TrackedItem(models.Model):
    class Status(models.TextChoices):
        UP_TO_DATE = 'up_to_date', 'À jour'
        WARNING = 'warning', 'À surveiller'
        CRITICAL = 'critical', 'Critique'

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='tracked_items',
        verbose_name='Véhicule',
    )
    name = models.CharField('Nom', max_length=200)
    part = models.ForeignKey(
        'parts.Part', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tracked_items', verbose_name='Pièce liée',
    )
    interval_km = models.IntegerField('Intervalle (km)', null=True, blank=True)
    interval_months = models.IntegerField('Intervalle (mois)', null=True, blank=True)
    last_service_km = models.IntegerField('Dernier service (km)', null=True, blank=True)
    last_service_date = models.DateField('Dernier service (date)', null=True, blank=True)
    status = models.CharField('Statut', max_length=20, choices=Status.choices, default=Status.UP_TO_DATE)
    recalced_at = models.DateTimeField('Recalculé le', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Élément suivi'
        verbose_name_plural = 'Éléments suivis'
        ordering = ['vehicle', 'name']

    def __str__(self):
        return f"{self.name} ({self.vehicle})"

    def compute_status(self, mileage=None, today=None):
        from datetime import date
        mileage = mileage if mileage is not None else self.vehicle.mileage
        today = today or date.today()
        ratio = 0.0
        if self.interval_km and self.last_service_km is not None:
            km_ratio = (mileage - self.last_service_km) / self.interval_km
            ratio = max(ratio, km_ratio)
        if self.interval_months and self.last_service_date:
            elapsed = (today - self.last_service_date).days
            month_ratio = elapsed / (self.interval_months * 30.44)
            ratio = max(ratio, month_ratio)
        if ratio >= 1.0:
            self.status = self.Status.CRITICAL
        elif ratio >= 0.8:
            self.status = self.Status.WARNING
        else:
            self.status = self.Status.UP_TO_DATE
        return self.status


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
