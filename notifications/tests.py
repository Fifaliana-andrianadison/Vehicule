from datetime import date, timedelta
from io import StringIO
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command
from django.core import mail
from vehicles.models import Vehicle
from maintenance.models import MaintenanceRecord
from documents.models import Insurance, TechnicalInspection, CarteGrise
from notifications.models import Reminder, NotificationLog


class ReminderAndNotificationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020,
        )

    def test_reminder_str(self):
        r = Reminder.objects.create(
            vehicle=self.vehicle,
            reminder_type='oil_change',
            title='Vidange Clio',
            message='Vidange prévue',
            due_date=date.today(),
            is_sent=False,
        )
        self.assertIn('Vidange', str(r))
        self.assertIn(str(self.vehicle), str(r))

    def test_reminder_is_sent_default(self):
        r = Reminder.objects.create(
            vehicle=self.vehicle,
            reminder_type='insurance',
            title='Test',
            message='Test',
            due_date=date.today(),
        )
        self.assertFalse(r.is_sent)

    def test_notification_log_str(self):
        log = NotificationLog.objects.create(
            vehicle=self.vehicle,
            recipient='test@test.com',
            subject='Rappel vidange',
            message='Test',
        )
        self.assertIn('Rappel vidange', str(log))

    def test_notification_log_vehicle_nullable(self):
        log = NotificationLog.objects.create(
            recipient='test@test.com',
            subject='Test',
            message='Test',
        )
        self.assertIsNone(log.vehicle)


class NotificationViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.other_user = User.objects.create_user(username='other', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020,
        )
        cls.other_vehicle = Vehicle.objects.create(
            user=cls.other_user, name='Other', brand='O', model='X', year=2020,
        )

    def setUp(self):
        self.client.login(username='testuser', password='pass1234')

    def test_reminder_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('notifications:reminders'))
        expected = f"{reverse('accounts:login')}?next={reverse('notifications:reminders')}"
        self.assertRedirects(response, expected)

    def test_reminder_list_shows_only_user_reminders(self):
        Reminder.objects.create(
            vehicle=self.vehicle, reminder_type='oil_change',
            title='Clio vidange', message='Test',
            due_date=date.today(),
        )
        Reminder.objects.create(
            vehicle=self.other_vehicle, reminder_type='insurance',
            title='Other insurance', message='Test',
            due_date=date.today(),
        )
        response = self.client.get(reverse('notifications:reminders'))
        self.assertContains(response, 'Clio')
        self.assertNotContains(response, 'Other insurance')

    def test_reminder_list_empty(self):
        response = self.client.get(reverse('notifications:reminders'))
        self.assertEqual(response.status_code, 200)

    def test_notification_history_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('notifications:history'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('notifications:history')}")

    def test_notification_history_shows_only_user_logs(self):
        NotificationLog.objects.create(
            vehicle=self.vehicle, recipient='user@test.com',
            subject='Log A', message='Test',
        )
        NotificationLog.objects.create(
            vehicle=self.other_vehicle, recipient='other@test.com',
            subject='Log B', message='Test',
        )
        response = self.client.get(reverse('notifications:history'))
        self.assertContains(response, 'Log A')
        self.assertNotContains(response, 'Log B')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SendRemindersCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='pass1234',
        )
        cls.user.profile.notification_email = True
        cls.user.profile.save()
        cls.user_no_email = User.objects.create_user(
            username='noemail', email='', password='pass1234',
        )
        cls.user_disabled = User.objects.create_user(
            username='disabled', email='disabled@test.com', password='pass1234',
        )
        cls.user_disabled.profile.notification_email = False
        cls.user_disabled.profile.save()
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020,
        )
        cls.vehicle_no_email = Vehicle.objects.create(
            user=cls.user_no_email, name='NoEmail', brand='X', model='X', year=2020,
        )
        cls.vehicle_disabled = Vehicle.objects.create(
            user=cls.user_disabled, name='Disabled', brand='X', model='X', year=2020,
        )

    def setUp(self):
        mail.outbox = []

    def test_oil_reminder_sends_email(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        out = StringIO()
        call_command('send_reminders', '--type=oil', stdout=out)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Rappel vidange', mail.outbox[0].subject)
        self.assertIn('Clio', mail.outbox[0].body)

    def test_oil_reminder_no_due_date_skipped(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
        )
        out = StringIO()
        call_command('send_reminders', '--type=oil', stdout=out)
        self.assertEqual(len(mail.outbox), 0)

    def test_oil_reminder_future_date_skipped(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=60),
        )
        out = StringIO()
        call_command('send_reminders', '--type=oil', stdout=out)
        self.assertEqual(len(mail.outbox), 0)

    def test_oil_reminder_creates_reminder_record(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        call_command('send_reminders', '--type=oil')
        self.assertEqual(Reminder.objects.filter(reminder_type='oil_change').count(), 1)

    def test_oil_reminder_dedup(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        call_command('send_reminders', '--type=oil')
        call_command('send_reminders', '--type=oil')
        self.assertEqual(Reminder.objects.filter(reminder_type='oil_change').count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_no_email_user_skipped(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle_no_email,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=10000,
            next_due_date=date.today() + timedelta(days=15),
        )
        out = StringIO()
        call_command('send_reminders', '--type=oil', stdout=out)
        self.assertEqual(len(mail.outbox), 0)

    def test_disabled_notification_skipped(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle_disabled,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=10000,
            next_due_date=date.today() + timedelta(days=15),
        )
        out = StringIO()
        call_command('send_reminders', '--type=oil', stdout=out)
        self.assertEqual(len(mail.outbox), 0)

    def test_inspection_reminder_sends_email(self):
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=30),
            result='passed',
            expiry_date=date.today() + timedelta(days=30),
        )
        out = StringIO()
        call_command('send_reminders', '--type=inspection', stdout=out)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('contrôle technique', mail.outbox[0].subject.lower())

    def test_inspection_past_expiry_sends_email(self):
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=400),
            result='passed',
            expiry_date=date.today() - timedelta(days=30),
        )
        out = StringIO()
        call_command('send_reminders', '--type=inspection', stdout=out)
        self.assertEqual(len(mail.outbox), 1)

    def test_insurance_reminder_sends_email(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=300),
            end_date=date.today() + timedelta(days=15),
            is_active=True,
        )
        out = StringIO()
        call_command('send_reminders', '--type=insurance', stdout=out)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('assurance', mail.outbox[0].subject.lower())

    def test_insurance_not_active_skipped(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=300),
            end_date=date.today() + timedelta(days=15),
            is_active=False,
        )
        out = StringIO()
        call_command('send_reminders', '--type=insurance', stdout=out)
        self.assertEqual(len(mail.outbox), 0)

    def test_registration_reminder_sends_email(self):
        CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today() - timedelta(days=3000),
            expiry_date=date.today() + timedelta(days=30),
        )
        out = StringIO()
        call_command('send_reminders', '--type=registration', stdout=out)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('carte grise', mail.outbox[0].subject.lower())

    def test_all_types_sends_all(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=30),
            result='passed',
            expiry_date=date.today() + timedelta(days=30),
        )
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=300),
            end_date=date.today() + timedelta(days=15),
            is_active=True,
        )
        out = StringIO()
        call_command('send_reminders', '--type=all', stdout=out)
        self.assertEqual(len(mail.outbox), 3)

    def test_creates_notification_log(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        call_command('send_reminders', '--type=oil')
        self.assertEqual(NotificationLog.objects.count(), 1)
        self.assertTrue(NotificationLog.objects.first().is_success)

    def test_output_message(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        out = StringIO()
        call_command('send_reminders', '--type=oil', stdout=out)
        self.assertIn('1 rappels envoyés', out.getvalue())
