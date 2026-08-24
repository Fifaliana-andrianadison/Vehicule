from celery import shared_task
from django.apps import apps
from django.utils import timezone


@shared_task
def recalculate_alerts():
    """Recalcule les statuts de tous les éléments suivis (alertes d'entretien)."""
    TrackedItem = apps.get_model('maintenance', 'TrackedItem')
    Vehicle = apps.get_model('vehicles', 'Vehicle')
    updated = 0
    for item in TrackedItem.objects.select_related('vehicle').all():
        old = item.status
        item.compute_status()
        item.recalced_at = timezone.now()
        if old != item.status:
            item.save(update_fields=['status', 'recalced_at'])
            updated += 1
    return f"{updated} alertes mises à jour pour {Vehicle.objects.count()} véhicules"


def recalculate_alerts_sync():
    from apps.maintenance.models import TrackedItem
    from django.utils import timezone
    updated = 0
    for item in TrackedItem.objects.select_related('vehicle').all():
        old = item.status
        item.compute_status()
        item.recalced_at = timezone.now()
        if old != item.status:
            item.save(update_fields=['status', 'recalced_at'])
            updated += 1
    return updated