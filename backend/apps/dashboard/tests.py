from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from vehicles.models import Vehicle
from maintenance.models import MaintenanceRecord
from documents.models import Insurance, TechnicalInspection


class DashboardViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')

    def setUp(self):
        self.client.login(username='testuser', password='pass1234')

    def test_home_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('dashboard:home')}")

    def test_home_no_vehicles_shows_welcome(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bienvenue')
        self.assertContains(response, 'Ajouter mon premier véhicule')

    def test_home_with_vehicles_shows_stats(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clio')
        self.assertEqual(response.context['total_vehicles'], 1)
        self.assertEqual(response.context['total_maintenance'], 0)
        self.assertEqual(response.context['total_cost'], 0)
        self.assertEqual(response.context['critical_count'], 0)
        self.assertEqual(response.context['warning_count'], 0)

    def test_home_with_maintenance_stats(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        MaintenanceRecord.objects.create(
            vehicle=vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            cost=Decimal('150.00'),
        )
        MaintenanceRecord.objects.create(
            vehicle=vehicle,
            maintenance_type='brake',
            date=date.today() - timedelta(days=60),
            mileage_at_service=40000,
            cost=Decimal('300.00'),
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.context['total_maintenance'], 2)
        self.assertEqual(response.context['total_cost'], Decimal('450.00'))

    def test_home_multiple_vehicles_with_statuses(self):
        v1 = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        v2 = Vehicle.objects.create(
            user=self.user, name='Zoe', brand='Renault',
            model='Zoe', year=2021, mileage=30000,
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(len(response.context['vehicle_statuses']), 2)
        self.assertEqual(response.context['total_vehicles'], 2)

    def test_home_critical_count(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        Vehicle.objects.create(
            user=self.user, name='Zoe', brand='Renault',
            model='Zoe', year=2021, mileage=30000,
        )
        TechnicalInspection.objects.create(
            vehicle=vehicle,
            inspection_date=date.today() - timedelta(days=400),
            result='passed',
            expiry_date=date.today() - timedelta(days=30),
        )
        Insurance.objects.create(
            vehicle=vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=400),
            end_date=date.today() - timedelta(days=10),
            is_active=True,
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.context['critical_count'], 1)
        self.assertContains(response, 'Action requise')

    def test_home_upcoming_reminders_shown(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        MaintenanceRecord.objects.create(
            vehicle=vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(len(response.context['upcoming_reminders']), 1)

    def test_home_reminders_sorted_by_urgency(self):
        v1 = Vehicle.objects.create(
            user=self.user, name='A', brand='A', model='A', year=2020, mileage=10000,
        )
        v2 = Vehicle.objects.create(
            user=self.user, name='B', brand='B', model='B', year=2020, mileage=20000,
        )
        MaintenanceRecord.objects.create(
            vehicle=v1,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=60),
            mileage_at_service=5000,
            next_due_date=date.today() + timedelta(days=25),
        )
        MaintenanceRecord.objects.create(
            vehicle=v2,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=90),
            mileage_at_service=15000,
            next_due_date=date.today() + timedelta(days=5),
        )
        response = self.client.get(reverse('dashboard:home'))
        reminders = response.context['upcoming_reminders']
        self.assertEqual(reminders[0]['days_left'], 5)
        self.assertEqual(reminders[1]['days_left'], 25)

    def test_home_shows_recent_maintenance(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        for i in range(15):
            MaintenanceRecord.objects.create(
                vehicle=vehicle,
                maintenance_type='oil_change',
                date=date.today() - timedelta(days=i),
                mileage_at_service=50000 - i * 1000,
            )
        response = self.client.get(reverse('dashboard:home'))
        self.assertLessEqual(len(response.context['recent_maintenance']), 10)

    def test_home_context_keys(self):
        Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        response = self.client.get(reverse('dashboard:home'))
        expected_keys = [
            'total_vehicles', 'total_maintenance', 'total_cost',
            'critical_count', 'warning_count', 'vehicle_statuses',
            'upcoming_reminders', 'recent_maintenance',
        ]
        for key in expected_keys:
            self.assertIn(key, response.context)

    def test_home_only_user_data(self):
        other_user = User.objects.create_user(username='other', password='pass1234')
        Vehicle.objects.create(
            user=other_user, name='Other Car', brand='O', model='X', year=2020,
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertNotContains(response, 'Other Car')
        self.assertEqual(response.context['total_vehicles'], 0)

    def test_home_empty_state_after_deleting_all_vehicles(self):
        Vehicle.objects.create(
            user=self.user, name='Temp', brand='T', model='T', year=2020,
        ).delete()
        response = self.client.get(reverse('dashboard:home'))
        self.assertContains(response, 'Bienvenue')

    def test_home_displays_insurance_reminder_in_upcoming(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        Insurance.objects.create(
            vehicle=vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=300),
            end_date=date.today() + timedelta(days=15),
            is_active=True,
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertGreater(len(response.context['upcoming_reminders']), 0)
        self.assertEqual(response.context['upcoming_reminders'][0]['type'], 'Assurance')

    def test_home_displays_inspection_reminder_in_upcoming(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        TechnicalInspection.objects.create(
            vehicle=vehicle,
            inspection_date=date.today() - timedelta(days=300),
            result='passed',
            expiry_date=date.today() + timedelta(days=30),
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertGreater(len(response.context['upcoming_reminders']), 0)
        self.assertEqual(response.context['upcoming_reminders'][0]['type'], 'Contrôle technique')

    def test_home_no_reminders_when_out_of_range(self):
        vehicle = Vehicle.objects.create(
            user=self.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        Insurance.objects.create(
            vehicle=vehicle, company_name='AXA', policy_number='P1',
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=200),
            is_active=True,
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(len(response.context['upcoming_reminders']), 0)
