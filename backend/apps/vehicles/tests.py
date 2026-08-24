from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.vehicles.models import Vehicle
from apps.maintenance.models import MaintenanceRecord
from apps.documents.models import Insurance, CarteGrise, TechnicalInspection


class VehicleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user,
            name='Clio',
            brand='Renault',
            model='Clio 4',
            year=2020,
            vehicle_type='car',
            fuel_type='diesel',
            vin='VF1AAAAAABBBBBBB',
            registration_number='AB-123-CD',
            mileage=50000,
            purchase_date=date(2020, 6, 15),
            is_active=True,
        )

    def test_str(self):
        self.assertEqual(str(self.vehicle), "Renault Clio 4 (AB-123-CD)")

    def test_str_sans_plaque(self):
        v = Vehicle.objects.create(
            user=self.user, name='Test', brand='Test',
            model='Test', year=2020,
        )
        self.assertIn("Sans plaque", str(v))

    def test_fields(self):
        self.assertEqual(self.vehicle.user, self.user)
        self.assertEqual(self.vehicle.name, 'Clio')
        self.assertEqual(self.vehicle.brand, 'Renault')
        self.assertEqual(self.vehicle.year, 2020)
        self.assertEqual(self.vehicle.vehicle_type, 'car')
        self.assertEqual(self.vehicle.fuel_type, 'diesel')
        self.assertEqual(self.vehicle.mileage, 50000)
        self.assertTrue(self.vehicle.is_active)

    def test_ordering(self):
        v2 = Vehicle.objects.create(
            user=self.user, name='Zoe', brand='Renault',
            model='Zoe', year=2021,
        )
        qs = Vehicle.objects.all()
        self.assertEqual(qs.first(), v2)

    def test_get_last_oil_change_no_record(self):
        self.assertIsNone(self.vehicle.get_last_oil_change())

    def test_get_last_oil_change_with_record(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
        )
        result = self.vehicle.get_last_oil_change()
        self.assertIsNotNone(result)

    def test_get_active_insurance_no_insurance(self):
        self.assertIsNone(self.vehicle.get_active_insurance())

    def test_get_active_insurance_valid(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='POL123',
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=300),
            is_active=True,
        )
        self.assertIsNotNone(self.vehicle.get_active_insurance())

    def test_get_active_insurance_expired(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='POL123',
            start_date=date.today() - timedelta(days=400),
            end_date=date.today() - timedelta(days=30),
            is_active=True,
        )
        self.assertIsNone(self.vehicle.get_active_insurance())

    def test_get_active_insurance_not_active(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='POL123',
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=300),
            is_active=False,
        )
        self.assertIsNone(self.vehicle.get_active_insurance())

    def test_get_latest_inspection_no_record(self):
        self.assertIsNone(self.vehicle.get_latest_inspection())

    def test_get_latest_inspection_with_record(self):
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=30),
            result='passed',
            expiry_date=date.today() + timedelta(days=300),
        )
        result = self.vehicle.get_latest_inspection()
        self.assertIsNotNone(result)

    def test_get_health_status_delegates(self):
        health = self.vehicle.get_health_status()
        self.assertIn('overall_status', health)
        self.assertIn('recommendations', health)


class VehicleViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.other_user = User.objects.create_user(username='other', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, vehicle_type='car',
            fuel_type='diesel', mileage=50000,
        )
        cls.other_vehicle = Vehicle.objects.create(
            user=cls.other_user, name='Other', brand='Other',
            model='X', year=2020,
        )

    def setUp(self):
        self.client.login(username='testuser', password='pass1234')

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('vehicles:list'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('vehicles:list')}")

    def test_list_shows_only_user_vehicles(self):
        response = self.client.get(reverse('vehicles:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clio')
        self.assertNotContains(response, 'Other')

    def test_detail_own_vehicle(self):
        response = self.client.get(reverse('vehicles:detail', kwargs={'pk': self.vehicle.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clio')

    def test_detail_other_vehicle_404(self):
        response = self.client.get(reverse('vehicles:detail', kwargs={'pk': self.other_vehicle.pk}))
        self.assertEqual(response.status_code, 404)

    def test_create_get(self):
        response = self.client.get(reverse('vehicles:create'))
        self.assertEqual(response.status_code, 200)

    def test_create_post_valid(self):
        data = {
            'name': 'Megane',
            'brand': 'Renault',
            'model': 'Megane 3',
            'year': 2018,
            'vehicle_type': 'car',
            'fuel_type': 'diesel',
            'mileage': 80000,
        }
        response = self.client.post(reverse('vehicles:create'), data)
        self.assertRedirects(response, reverse('vehicles:detail', kwargs={'pk': 3}))
        self.assertEqual(Vehicle.objects.filter(name='Megane').count(), 1)
        self.assertEqual(Vehicle.objects.get(name='Megane').user, self.user)

    def test_create_post_invalid(self):
        data = {'name': '', 'brand': '', 'model': '', 'year': ''}
        response = self.client.post(reverse('vehicles:create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_update_own_vehicle(self):
        data = {
            'name': 'Clio Update',
            'brand': 'Renault',
            'model': 'Clio 4',
            'year': 2020,
            'vehicle_type': 'car',
            'fuel_type': 'diesel',
            'mileage': 55000,
        }
        response = self.client.post(
            reverse('vehicles:update', kwargs={'pk': self.vehicle.pk}), data
        )
        self.assertRedirects(response, reverse('vehicles:detail', kwargs={'pk': self.vehicle.pk}))
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.name, 'Clio Update')
        self.assertEqual(self.vehicle.mileage, 55000)

    def test_update_other_vehicle_404(self):
        response = self.client.post(
            reverse('vehicles:update', kwargs={'pk': self.other_vehicle.pk}), {}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_own_vehicle(self):
        response = self.client.post(
            reverse('vehicles:delete', kwargs={'pk': self.vehicle.pk})
        )
        self.assertRedirects(response, reverse('vehicles:list'))
        self.assertEqual(Vehicle.objects.filter(pk=self.vehicle.pk).count(), 0)

    def test_delete_other_vehicle_404(self):
        response = self.client.post(
            reverse('vehicles:delete', kwargs={'pk': self.other_vehicle.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_get_confirmation(self):
        response = self.client.get(
            reverse('vehicles:delete', kwargs={'pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_context_contains_methods(self):
        response = self.client.get(reverse('vehicles:detail', kwargs={'pk': self.vehicle.pk}))
        self.assertIn('vehicle', response.context)
        self.assertIn('today', response.context)
        self.assertIsNone(response.context['last_oil'])
        self.assertIsNone(response.context['active_insurance'])
        self.assertIsNone(response.context['last_inspection'])

    def test_detail_with_maintenance_total_cost(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today(),
            mileage_at_service=45000,
            cost=Decimal('150.00'),
        )
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='brake',
            date=date.today(),
            mileage_at_service=45000,
            cost=Decimal('300.00'),
        )
        response = self.client.get(reverse('vehicles:detail', kwargs={'pk': self.vehicle.pk}))
        self.assertEqual(response.context['maintenance_count'], 2)
        self.assertEqual(response.context['total_cost'], Decimal('450.00'))

    def test_detail_inactive_vehicle_still_accessible(self):
        self.vehicle.is_active = False
        self.vehicle.save()
        response = self.client.get(reverse('vehicles:detail', kwargs={'pk': self.vehicle.pk}))
        self.assertEqual(response.status_code, 200)


class VehiclePermissionsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', password='pass1234')
        self.v1 = Vehicle.objects.create(
            user=self.user1, name='V1', brand='A', model='X', year=2020,
        )

    def test_user2_cannot_access_user1_vehicle_detail(self):
        self.client.login(username='user2', password='pass1234')
        response = self.client.get(reverse('vehicles:detail', kwargs={'pk': self.v1.pk}))
        self.assertEqual(response.status_code, 404)

    def test_user2_cannot_delete_user1_vehicle(self):
        self.client.login(username='user2', password='pass1234')
        response = self.client.post(reverse('vehicles:delete', kwargs={'pk': self.v1.pk}))
        self.assertEqual(response.status_code, 404)

    def test_user2_cannot_update_user1_vehicle(self):
        self.client.login(username='user2', password='pass1234')
        response = self.client.post(
            reverse('vehicles:update', kwargs={'pk': self.v1.pk}),
            {'name': 'Hacked', 'brand': 'H', 'model': 'H', 'year': 2020},
        )
        self.assertEqual(response.status_code, 404)
        self.v1.refresh_from_db()
        self.assertEqual(self.v1.name, 'V1')

    def test_unauthenticated_redirected(self):
        response = self.client.get(reverse('vehicles:list'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('vehicles:list')}")
