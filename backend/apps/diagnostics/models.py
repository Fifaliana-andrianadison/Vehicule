from django.db import models
from vehicles.models import Vehicle


class DiagnosticReport(models.Model):
    class OverallStatus(models.TextChoices):
        GOOD = 'good', 'Bon état'
        WARNING = 'warning', 'Attention nécessaire'
        CRITICAL = 'critical', 'État critique'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='diagnostic_reports', verbose_name='Véhicule')
    overall_status = models.CharField('Statut global', max_length=10, choices=OverallStatus.choices, default=OverallStatus.GOOD)
    report_date = models.DateTimeField("Date du diagnostic", auto_now_add=True)
    mileage = models.IntegerField('Kilométrage actuel')
    oil_change_status = models.CharField('État vidange', max_length=50, blank=True)
    inspection_status = models.CharField('État contrôle technique', max_length=50, blank=True)
    insurance_status = models.CharField('État assurance', max_length=50, blank=True)
    registration_status = models.CharField('État carte grise', max_length=50, blank=True)
    days_until_next_oil_change = models.IntegerField('Jours avant prochaine vidange', null=True, blank=True)
    km_until_next_oil_change = models.IntegerField('KM avant prochaine vidange', null=True, blank=True)
    days_until_inspection = models.IntegerField('Jours avant contrôle technique', null=True, blank=True)
    days_until_insurance_expiry = models.IntegerField('Jours avant expiration assurance', null=True, blank=True)
    recommendations = models.TextField('Recommandations', blank=True)
    is_critical = models.BooleanField('État critique', default=False)

    class Meta:
        verbose_name = 'Rapport de diagnostic'
        verbose_name_plural = 'Rapports de diagnostic'
        ordering = ['-report_date']

    def __str__(self):
        return f"Diagnostic {self.vehicle} - {self.report_date.date()}"
