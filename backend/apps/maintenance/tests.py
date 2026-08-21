from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from vehicles.models import Vehicle
from maintenance.models import MaintenanceRecord


class MaintenanceRecordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020,
        )
        cls.record = MaintenanceRecord.objects.create(
            vehicle=cls.vehicle,
            maintenance_type='oil_change',
            description='Vidange moteur',
            date=date(2025, 1, 15),
            mileage_at_service=45000,
            cost=Decimal('150.00'),
            garage_name='Garage Durand',
            next_due_mileage=55000,
            next_due_date=date(2025, 7, 15),
            notes='Huile 5W30',
        )

    def test_str(self):
        expected = f"Vidange - {self.vehicle} (2025-01-15)"
        self.assertEqual(str(self.record), expected)

    def test_maintenance_type_choices(self):
        expected_choices = {
            'oil_change': 'Vidange',
            'brake': 'Freins',
            'tire': 'Pneus',
            'belt': 'Courroie de distribution',
            'battery': 'Batterie',
            'filter': 'Filtres',
            'clutch': 'Embrayage',
            'suspension': 'Suspension',
            'exhaust': 'Échappement',
            'electric': 'Système électrique',
            'air_conditioning': 'Climatisation',
            'timing_belt': 'Distribution',
            'cooling': 'Refroidissement',
            'other': 'Autre',
        }
        for value, label in expected_choices.items():
            self.assertIn((value, label), MaintenanceRecord.MaintenanceType.choices)

    def test_ordering_by_date_desc(self):
        older = MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='brake',
            date=date(2024, 12, 1),
            mileage_at_service=40000,
        )
        newest = MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='tire',
            date=date(2025, 3, 1),
            mileage_at_service=50000,
        )
        qs = MaintenanceRecord.objects.all()
        self.assertEqual(qs[0], newest)
        self.assertEqual(qs[2], older)

    def test_optional_fields_blank(self):
        r = MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='other',
            date=date.today(),
            mileage_at_service=0,
        )
        self.assertEqual(r.description, '')
        self.assertIsNone(r.cost)
        self.assertEqual(r.garage_name, '')
        self.assertIsNone(r.next_due_mileage)
        self.assertIsNone(r.next_due_date)
        self.assertEqual(r.notes, '')


class MaintenanceViewsTest(TestCase):
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
        cls.record = MaintenanceRecord.objects.create(
            vehicle=cls.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
        )
        cls.other_record = MaintenanceRecord.objects.create(
            vehicle=cls.other_vehicle,
            maintenance_type='brake',
            date=date.today(),
            mileage_at_service=10000,
        )

    def setUp(self):
        self.client.login(username='testuser', password='pass1234')

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('maintenance:list'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('maintenance:list')}")

    def test_list_shows_only_user_records(self):
        response = self.client.get(reverse('maintenance:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clio')
        self.assertNotContains(response, 'Other')

    def test_list_context(self):
        response = self.client.get(reverse('maintenance:list'))
        self.assertIn('records', response.context)
        self.assertEqual(len(response.context['records']), 1)

    def test_create_get(self):
        response = self.client.get(reverse('maintenance:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_create_post_valid(self):
        data = {
            'vehicle': self.vehicle.pk,
            'maintenance_type': 'brake',
            'description': 'Changement plaquettes',
            'date': date.today().isoformat(),
            'mileage_at_service': 50000,
            'cost': '250.00',
            'garage_name': 'Garage Test',
        }
        response = self.client.post(reverse('maintenance:create'), data)
        self.assertRedirects(response, reverse('maintenance:list'))
        self.assertEqual(MaintenanceRecord.objects.filter(description='Changement plaquettes').count(), 1)

    def test_create_post_other_vehicle_not_in_choices(self):
        data = {
            'vehicle': self.other_vehicle.pk,
            'maintenance_type': 'brake',
            'date': date.today().isoformat(),
            'mileage_at_service': 10000,
        }
        response = self.client.post(reverse('maintenance:create'), data)
        self.assertEqual(response.status_code, 200)

    def test_create_post_invalid(self):
        data = {'vehicle': '', 'maintenance_type': '', 'date': '', 'mileage_at_service': ''}
        response = self.client.post(reverse('maintenance:create'), data)
        self.assertEqual(response.status_code, 200)

    def test_update_own_record(self):
        data = {
            'vehicle': self.vehicle.pk,
            'maintenance_type': 'oil_change',
            'date': date.today().isoformat(),
            'mileage_at_service': 50000,
            'cost': '200.00',
        }
        response = self.client.post(
            reverse('maintenance:update', kwargs={'pk': self.record.pk}), data
        )
        self.assertRedirects(response, reverse('maintenance:list'))
        self.record.refresh_from_db()
        self.assertEqual(self.record.cost, Decimal('200.00'))

    def test_update_other_record_404(self):
        data = {
            'vehicle': self.vehicle.pk,
            'maintenance_type': 'oil_change',
            'date': date.today().isoformat(),
            'mileage_at_service': 10000,
        }
        response = self.client.post(
            reverse('maintenance:update', kwargs={'pk': self.other_record.pk}), data
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_own_record(self):
        pk = self.record.pk
        response = self.client.post(reverse('maintenance:delete', kwargs={'pk': pk}))
        self.assertRedirects(response, reverse('maintenance:list'))
        self.assertEqual(MaintenanceRecord.objects.filter(pk=pk).count(), 0)

    def test_delete_other_record_404(self):
        response = self.client.post(
            reverse('maintenance:delete', kwargs={'pk': self.other_record.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_by_vehicle_filtered(self):
        Vehicle.objects.create(
            user=self.user, name='Zoe', brand='Renault', model='Zoe', year=2021,
        )
        response = self.client.get(
            reverse('maintenance:by_vehicle', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clio')

    def test_by_vehicle_other_user(self):
        response = self.client.get(
            reverse('maintenance:by_vehicle', kwargs={'vehicle_pk': self.other_vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Other')

    def test_delete_get_confirmation(self):
        response = self.client.get(
            reverse('maintenance:delete', kwargs={'pk': self.record.pk})
        )
        self.assertEqual(response.status_code, 200)
