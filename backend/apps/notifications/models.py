from django.db import models
from apps.vehicles.models import Vehicle


class Reminder(models.Model):
    class ReminderType(models.TextChoices):
        OIL_CHANGE = 'oil_change', 'Vidange'
        INSPECTION = 'inspection', 'Contrôle technique'
        INSURANCE = 'insurance', 'Assurance'
        REGISTRATION = 'registration', 'Carte grise'
        MAINTENANCE = 'maintenance', 'Entretien général'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reminders', verbose_name='Véhicule')
    reminder_type = models.CharField('Type', max_length=20, choices=ReminderType.choices)
    title = models.CharField('Titre', max_length=200)
    message = models.TextField('Message')
    due_date = models.DateField("Date d'échéance")
    is_sent = models.BooleanField('Envoyé', default=False)
    sent_date = models.DateTimeField('Date denvoi', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rappel'
        verbose_name_plural = 'Rappels'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.get_reminder_type_display()} - {self.vehicle} ({self.due_date})"


class NotificationLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='notification_logs', verbose_name='Véhicule', null=True, blank=True)
    recipient = models.EmailField('Destinataire')
    subject = models.CharField('Sujet', max_length=200)
    message = models.TextField('Message')
    sent_at = models.DateTimeField('Envoyé le', auto_now_add=True)
    is_success = models.BooleanField('Succès', default=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-sent_at']

    def __str__(self):
        return f"Notification: {self.subject} -> {self.recipient}"
