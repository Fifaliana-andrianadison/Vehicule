from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from apps.vehicles.models import Vehicle
from apps.documents.models import Insurance, CarteGrise, TechnicalInspection


class InsuranceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020,
        )
        cls.insurance = Insurance.objects.create(
            vehicle=cls.vehicle,
            company_name='AXA',
            policy_number='POL-12345',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            premium_amount=Decimal('600.00'),
            is_active=True,
        )

    def test_str(self):
        self.assertEqual(str(self.insurance), f"AXA - {self.vehicle}")

    def test_active_default(self):
        self.assertTrue(self.insurance.is_active)

    def test_optional_fields(self):
        i = Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='Test',
            policy_number='T-001',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )
        self.assertIsNone(i.premium_amount)
        self.assertEqual(i.notes, '')

    def test_ordering(self):
        i2 = Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='MMA',
            policy_number='POL-67890',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        qs = Insurance.objects.all()
        self.assertEqual(qs.first(), self.insurance)


class CarteGriseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020,
        )
        cls.cg = CarteGrise.objects.create(
            vehicle=cls.vehicle,
            registration_number='AB-123-CD',
            issue_date=date(2020, 6, 15),
            expiry_date=date(2030, 6, 15),
        )

    def test_str(self):
        self.assertEqual(str(self.cg), "Carte Grise AB-123-CD")

    def test_one_to_one(self):
        with self.assertRaises(Exception):
            CarteGrise.objects.create(
                vehicle=self.vehicle,
                registration_number='XY-999-ZZ',
                issue_date=date.today(),
            )

    def test_expiry_date_nullable(self):
        v2 = Vehicle.objects.create(
            user=self.user, name='Zoe', brand='Renault',
            model='Zoe', year=2021,
        )
        cg2 = CarteGrise.objects.create(
            vehicle=v2,
            registration_number='XY-999-ZZ',
            issue_date=date.today(),
        )
        self.assertIsNone(cg2.expiry_date)


class TechnicalInspectionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020,
        )
        cls.ct = TechnicalInspection.objects.create(
            vehicle=cls.vehicle,
            inspection_date=date(2024, 6, 15),
            result='passed',
            expiry_date=date(2026, 6, 15),
            mileage_at_inspection=45000,
            garage_name='Centre Auto Test',
        )

    def test_str(self):
        self.assertEqual(str(self.ct), f"CT {self.vehicle} - 2024-06-15")

    def test_result_choices(self):
        self.assertEqual(TechnicalInspection.Result.PASSED.value, 'passed')
        self.assertEqual(TechnicalInspection.Result.PASSED.label, 'Favorable')
        self.assertEqual(TechnicalInspection.Result.FAILED.value, 'failed')
        self.assertEqual(TechnicalInspection.Result.FAILED.label, 'Défavorable')
        self.assertEqual(TechnicalInspection.Result.PARTIAL.value, 'partial')
        self.assertEqual(TechnicalInspection.Result.PARTIAL.label, 'Favorable avec réserves')

    def test_optional_fields(self):
        ct2 = TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today(),
            result='passed',
            expiry_date=date.today() + timedelta(days=365),
        )
        self.assertIsNone(ct2.mileage_at_inspection)
        self.assertEqual(ct2.garage_name, '')
        self.assertEqual(ct2.notes, '')


class DocumentsViewsTest(TestCase):
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

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('documents:list'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('documents:list')}")

    def test_list_shows_only_user_documents(self):
        Insurance.objects.create(
            vehicle=self.vehicle, company_name='AXA',
            policy_number='P1', start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )
        Insurance.objects.create(
            vehicle=self.other_vehicle, company_name='Other',
            policy_number='P2', start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )
        response = self.client.get(reverse('documents:list'))
        self.assertContains(response, 'AXA')
        self.assertNotContains(response, 'Other')

    def test_insurance_create_get(self):
        response = self.client.get(reverse('documents:insurance_create'))
        self.assertEqual(response.status_code, 200)

    def test_insurance_create_post_valid(self):
        data = {
            'vehicle': self.vehicle.pk,
            'company_name': 'MAIF',
            'policy_number': 'POL-999',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=365)).isoformat(),
            'premium_amount': '500.00',
            'is_active': True,
        }
        response = self.client.post(reverse('documents:insurance_create'), data)
        self.assertRedirects(response, reverse('documents:list'))
        self.assertEqual(Insurance.objects.filter(company_name='MAIF').count(), 1)

    def test_insurance_update(self):
        ins = Insurance.objects.create(
            vehicle=self.vehicle, company_name='AXA',
            policy_number='P1', start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )
        data = {
            'vehicle': self.vehicle.pk,
            'company_name': 'AXA Updated',
            'policy_number': 'P1-UPD',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=365)).isoformat(),
        }
        response = self.client.post(
            reverse('documents:insurance_update', kwargs={'pk': ins.pk}), data
        )
        self.assertRedirects(response, reverse('documents:list'))
        ins.refresh_from_db()
        self.assertEqual(ins.company_name, 'AXA Updated')

    def test_insurance_delete(self):
        ins = Insurance.objects.create(
            vehicle=self.vehicle, company_name='Temp',
            policy_number='T1', start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        pk = ins.pk
        response = self.client.post(
            reverse('documents:insurance_delete', kwargs={'pk': pk})
        )
        self.assertRedirects(response, reverse('documents:list'))
        self.assertEqual(Insurance.objects.filter(pk=pk).count(), 0)

    def test_carte_grise_create_get(self):
        response = self.client.get(reverse('documents:carte_grise_create'))
        self.assertEqual(response.status_code, 200)

    def test_carte_grise_create_post_valid(self):
        data = {
            'vehicle': self.vehicle.pk,
            'registration_number': 'AB-123-CD',
            'issue_date': date.today().isoformat(),
            'expiry_date': (date.today() + timedelta(days=3650)).isoformat(),
        }
        response = self.client.post(reverse('documents:carte_grise_create'), data)
        self.assertRedirects(response, reverse('documents:list'))
        self.assertEqual(CarteGrise.objects.filter(registration_number='AB-123-CD').count(), 1)

    def test_carte_grise_update(self):
        cg = CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today(),
        )
        data = {
            'vehicle': self.vehicle.pk,
            'registration_number': 'XY-999-ZZ',
            'issue_date': date.today().isoformat(),
        }
        response = self.client.post(
            reverse('documents:carte_grise_update', kwargs={'pk': cg.pk}), data
        )
        self.assertRedirects(response, reverse('documents:list'))
        cg.refresh_from_db()
        self.assertEqual(cg.registration_number, 'XY-999-ZZ')

    def test_carte_grise_delete(self):
        cg = CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='TEMP-01',
            issue_date=date.today(),
        )
        pk = cg.pk
        response = self.client.post(
            reverse('documents:carte_grise_delete', kwargs={'pk': pk})
        )
        self.assertRedirects(response, reverse('documents:list'))
        self.assertEqual(CarteGrise.objects.filter(pk=pk).count(), 0)

    def test_inspection_create_get(self):
        response = self.client.get(reverse('documents:inspection_create'))
        self.assertEqual(response.status_code, 200)

    def test_inspection_create_post_valid(self):
        data = {
            'vehicle': self.vehicle.pk,
            'inspection_date': date.today().isoformat(),
            'result': 'passed',
            'expiry_date': (date.today() + timedelta(days=730)).isoformat(),
            'mileage_at_inspection': 50000,
        }
        response = self.client.post(reverse('documents:inspection_create'), data)
        self.assertRedirects(response, reverse('documents:list'))
        self.assertEqual(TechnicalInspection.objects.filter(result='passed').count(), 1)

    def test_inspection_update(self):
        ct = TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today(),
            result='passed',
            expiry_date=date.today() + timedelta(days=365),
        )
        data = {
            'vehicle': self.vehicle.pk,
            'inspection_date': date.today().isoformat(),
            'result': 'failed',
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
        }
        response = self.client.post(
            reverse('documents:inspection_update', kwargs={'pk': ct.pk}), data
        )
        self.assertRedirects(response, reverse('documents:list'))
        ct.refresh_from_db()
        self.assertEqual(ct.result, 'failed')

    def test_inspection_delete(self):
        ct = TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today(),
            result='passed',
            expiry_date=date.today() + timedelta(days=365),
        )
        pk = ct.pk
        response = self.client.post(
            reverse('documents:inspection_delete', kwargs={'pk': pk})
        )
        self.assertRedirects(response, reverse('documents:list'))
        self.assertEqual(TechnicalInspection.objects.filter(pk=pk).count(), 0)

    def test_create_post_other_vehicle_not_in_choices(self):
        data = {
            'vehicle': self.other_vehicle.pk,
            'company_name': 'Test',
            'policy_number': 'T1',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat(),
        }
        response = self.client.post(reverse('documents:insurance_create'), data)
        self.assertEqual(response.status_code, 200)

    def test_update_other_insurance_404(self):
        ins = Insurance.objects.create(
            vehicle=self.other_vehicle, company_name='Other',
            policy_number='O1', start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        response = self.client.post(
            reverse('documents:insurance_update', kwargs={'pk': ins.pk}), {}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_other_inspection_404(self):
        ct = TechnicalInspection.objects.create(
            vehicle=self.other_vehicle,
            inspection_date=date.today(),
            result='passed',
            expiry_date=date.today() + timedelta(days=365),
        )
        response = self.client.post(
            reverse('documents:inspection_delete', kwargs={'pk': ct.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_carte_grise_only_one_per_vehicle(self):
        CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today(),
        )
        data = {
            'vehicle': self.vehicle.pk,
            'registration_number': 'XY-999-ZZ',
            'issue_date': date.today().isoformat(),
        }
        response = self.client.post(reverse('documents:carte_grise_create'), data)
        self.assertEqual(response.status_code, 200)

    def test_list_displays_document_counts(self):
        CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today(),
        )
        Insurance.objects.create(
            vehicle=self.vehicle, company_name='AXA',
            policy_number='P1', start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('insurances', response.context)
        self.assertIn('cartes_grise', response.context)
        self.assertIn('inspections', response.context)
