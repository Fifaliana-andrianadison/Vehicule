from django.db import models
from django.contrib.auth.models import User
from apps.vehicles.models import Vehicle
from apps.parts.models import Part


class Garage(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='garage', verbose_name='Propriétaire')
    name = models.CharField('Nom', max_length=200)
    address = models.TextField('Adresse', blank=True)
    phone = models.CharField('Téléphone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    siret = models.CharField('SIRET', max_length=14, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Garage'
        verbose_name_plural = 'Garages'

    def __str__(self):
        return self.name


class GarageStaff(models.Model):
    class Role(models.TextChoices):
        MECHANIC = 'mechanic', 'Mécanicien'
        MANAGER = 'manager', 'Manager'
        ADMIN = 'admin', 'Administrateur'

    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='staff', verbose_name='Garage')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', verbose_name='Utilisateur')
    role = models.CharField('Rôle', max_length=20, choices=Role.choices, default=Role.MECHANIC)
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Employé du garage'
        verbose_name_plural = 'Employés du garage'

    def __str__(self):
        return f"{self.user.username} @ {self.garage.name}"


class RepairOrder(models.Model):
    class Status(models.TextChoices):
        QUOTE = 'quote', 'Devis'
        IN_PROGRESS = 'in_progress', 'En cours'
        WAITING_PARTS = 'waiting_parts', 'Attente pièces'
        INVOICED = 'invoiced', 'Facturé'
        CANCELLED = 'cancelled', 'Annulé'

    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='repair_orders', verbose_name='Garage')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='repair_orders', verbose_name='Véhicule')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_repair_orders', verbose_name='Client')
    title = models.CharField('Titre', max_length=200)
    description = models.TextField('Description', blank=True)
    status = models.CharField('Statut', max_length=20, choices=Status.choices, default=Status.QUOTE)
    estimated_cost = models.DecimalField('Coût estimé (€)', max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField('Coût total (€)', max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ordre de réparation'
        verbose_name_plural = 'Ordres de réparation'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.vehicle} ({self.get_status_display()})"

    @property
    def parts_total(self):
        return sum((p.total for p in self.parts.all()), self.total_cost or 0)


class RepairOrderPart(models.Model):
    repair_order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name='parts')
    part = models.ForeignKey(Part, on_delete=models.SET_NULL, null=True, blank=True, related_name='repair_order_parts')
    name = models.CharField('Nom', max_length=200)
    quantity = models.PositiveIntegerField('Quantité', default=1)
    unit_price = models.DecimalField('Prix unitaire (€)', max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Pièce d\'ordre de réparation'
        verbose_name_plural = 'Pièces d\'ordre de réparation'

    def __str__(self):
        return f"{self.quantity}x {self.name}"

    @property
    def total(self):
        return self.unit_price * self.quantity