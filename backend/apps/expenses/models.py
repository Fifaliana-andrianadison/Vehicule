from django.db import models
from apps.vehicles.models import Vehicle


class ExpenseCategory(models.Model):
    name = models.CharField('Nom', max_length=100, unique=True)
    description = models.TextField('Description', blank=True)

    class Meta:
        verbose_name = 'Catégorie de dépense'
        verbose_name_plural = 'Catégories de dépenses'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='expenses',
        verbose_name='Véhicule',
    )
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.PROTECT, related_name='expenses',
        verbose_name='Catégorie',
    )
    amount = models.DecimalField('Montant (€)', max_digits=10, decimal_places=2)
    date = models.DateField('Date')
    description = models.CharField('Description', max_length=200, blank=True)
    repair_order = models.OneToOneField(
        'garage.RepairOrder', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='expense', verbose_name='Ordre de réparation lié',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-date']

    def __str__(self):
        return f"{self.amount} € - {self.vehicle} ({self.date})"