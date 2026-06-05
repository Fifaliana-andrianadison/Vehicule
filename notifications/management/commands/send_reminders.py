from datetime import date, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.management.base import BaseCommand
from vehicles.models import Vehicle
from maintenance.models import MaintenanceRecord
from documents.models import TechnicalInspection, Insurance, CarteGrise
from notifications.models import Reminder, NotificationLog


class Command(BaseCommand):
    help = 'Envoie les rappels par email (vidange, CT, assurance, carte grise)'

    def add_arguments(self, parser):
        parser.add_argument('--type', choices=['all', 'oil', 'inspection', 'insurance', 'registration'], default='all')

    def handle(self, *args, **options):
        today = date.today()
        sent_count = 0

        if options['type'] in ('all', 'oil'):
            sent_count += self._send_oil_reminders(today)
        if options['type'] in ('all', 'inspection'):
            sent_count += self._send_inspection_reminders(today)
        if options['type'] in ('all', 'insurance'):
            sent_count += self._send_insurance_reminders(today)
        if options['type'] in ('all', 'registration'):
            sent_count += self._send_registration_reminders(today)

        self.stdout.write(self.style.SUCCESS(f'{sent_count} rappels envoyés avec succès'))

    def _send_oil_reminders(self, today):
        count = 0
        warning_date = today + timedelta(days=30)
        records = MaintenanceRecord.objects.filter(
            maintenance_type='oil_change',
            next_due_date__lte=warning_date,
        ).select_related('vehicle__user__profile')

        for record in records:
            user = record.vehicle.user
            if not user.email or not getattr(user.profile, 'notification_email', True):
                continue

            if Reminder.objects.filter(
                vehicle=record.vehicle, reminder_type='oil_change',
                due_date=record.next_due_date, is_sent=True
            ).exists():
                continue

            days_left = (record.next_due_date - today).days
            subject = f'Rappel vidange - {record.vehicle.name}'
            html = render_to_string('notifications/emails/oil_change.html', {
                'user': user, 'vehicle': record.vehicle,
                'days_left': days_left, 'due_date': record.next_due_date,
            })
            plain = strip_tags(html)

            try:
                send_mail(subject, plain, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html)
                NotificationLog.objects.create(vehicle=record.vehicle, recipient=user.email, subject=subject, message=plain, is_success=True)
                Reminder.objects.create(vehicle=record.vehicle, reminder_type='oil_change',
                    title=f'Vidange - {record.vehicle.name}',
                    message=f'Vidange prévue le {record.next_due_date} ({days_left} jours)',
                    due_date=record.next_due_date, is_sent=True)
                count += 1
            except Exception as e:
                NotificationLog.objects.create(vehicle=record.vehicle, recipient=user.email, subject=subject, message=str(e), is_success=False)
        return count

    def _send_inspection_reminders(self, today):
        count = 0
        warning_date = today + timedelta(days=90)
        inspections = TechnicalInspection.objects.filter(
            expiry_date__lte=warning_date,
        ).select_related('vehicle__user__profile')

        for inspection in inspections:
            user = inspection.vehicle.user
            if not user.email or not getattr(user.profile, 'notification_email', True):
                continue

            if Reminder.objects.filter(
                vehicle=inspection.vehicle, reminder_type='inspection',
                due_date=inspection.expiry_date, is_sent=True
            ).exists():
                continue

            days_left = (inspection.expiry_date - today).days
            subject = f'Rappel contrôle technique - {inspection.vehicle.name}'
            html = render_to_string('notifications/emails/inspection.html', {
                'user': user, 'vehicle': inspection.vehicle,
                'days_left': days_left, 'expiry_date': inspection.expiry_date,
            })
            plain = strip_tags(html)

            try:
                send_mail(subject, plain, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html)
                NotificationLog.objects.create(vehicle=inspection.vehicle, recipient=user.email, subject=subject, message=plain, is_success=True)
                Reminder.objects.create(vehicle=inspection.vehicle, reminder_type='inspection',
                    title=f'Contrôle technique - {inspection.vehicle.name}',
                    message=f'Contrôle technique expire le {inspection.expiry_date} ({days_left} jours)',
                    due_date=inspection.expiry_date, is_sent=True)
                count += 1
            except Exception as e:
                NotificationLog.objects.create(vehicle=inspection.vehicle, recipient=user.email, subject=subject, message=str(e), is_success=False)
        return count

    def _send_insurance_reminders(self, today):
        count = 0
        warning_date = today + timedelta(days=30)
        insurances = Insurance.objects.filter(
            is_active=True, end_date__lte=warning_date,
        ).select_related('vehicle__user__profile')

        for insurance in insurances:
            user = insurance.vehicle.user
            if not user.email or not getattr(user.profile, 'notification_email', True):
                continue

            if Reminder.objects.filter(
                vehicle=insurance.vehicle, reminder_type='insurance',
                due_date=insurance.end_date, is_sent=True
            ).exists():
                continue

            days_left = (insurance.end_date - today).days
            subject = f'Rappel assurance - {insurance.vehicle.name}'
            html = render_to_string('notifications/emails/insurance.html', {
                'user': user, 'vehicle': insurance.vehicle,
                'company': insurance.company_name,
                'days_left': days_left, 'end_date': insurance.end_date,
            })
            plain = strip_tags(html)

            try:
                send_mail(subject, plain, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html)
                NotificationLog.objects.create(vehicle=insurance.vehicle, recipient=user.email, subject=subject, message=plain, is_success=True)
                Reminder.objects.create(vehicle=insurance.vehicle, reminder_type='insurance',
                    title=f'Assurance - {insurance.vehicle.name}',
                    message=f'Assurance {insurance.company_name} expire le {insurance.end_date} ({days_left} jours)',
                    due_date=insurance.end_date, is_sent=True)
                count += 1
            except Exception as e:
                NotificationLog.objects.create(vehicle=insurance.vehicle, recipient=user.email, subject=subject, message=str(e), is_success=False)
        return count

    def _send_registration_reminders(self, today):
        count = 0
        warning_date = today + timedelta(days=90)
        cartes = CarteGrise.objects.filter(
            expiry_date__lte=warning_date,
        ).select_related('vehicle__user__profile')

        for carte in cartes:
            user = carte.vehicle.user
            if not user.email or not getattr(user.profile, 'notification_email', True):
                continue

            if Reminder.objects.filter(
                vehicle=carte.vehicle, reminder_type='registration',
                due_date=carte.expiry_date, is_sent=True
            ).exists():
                continue

            days_left = (carte.expiry_date - today).days
            subject = f'Rappel carte grise - {carte.vehicle.name}'
            html = render_to_string('notifications/emails/registration.html', {
                'user': user, 'vehicle': carte.vehicle,
                'registration': carte.registration_number,
                'days_left': days_left, 'expiry_date': carte.expiry_date,
            })
            plain = strip_tags(html)

            try:
                send_mail(subject, plain, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html)
                NotificationLog.objects.create(vehicle=carte.vehicle, recipient=user.email, subject=subject, message=plain, is_success=True)
                Reminder.objects.create(vehicle=carte.vehicle, reminder_type='registration',
                    title=f'Carte grise - {carte.vehicle.name}',
                    message=f'Carte grise expire le {carte.expiry_date} ({days_left} jours)',
                    due_date=carte.expiry_date, is_sent=True)
                count += 1
            except Exception as e:
                NotificationLog.objects.create(vehicle=carte.vehicle, recipient=user.email, subject=subject, message=str(e), is_success=False)
        return count
