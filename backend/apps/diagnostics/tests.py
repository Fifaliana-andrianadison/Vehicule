from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from apps.vehicles.models import Vehicle
from apps.maintenance.models import MaintenanceRecord
from apps.documents.models import Insurance, TechnicalInspection, CarteGrise
from apps.diagnostics.models import DiagnosticReport
from apps.diagnostics.utils import get_vehicle_health


class GetVehicleHealthTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )

    def test_no_data_returns_good_with_recommendations(self):
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'good')
        self.assertFalse(health['is_critical'])
        self.assertIn('Aucune vidange', health['oil_change_status'])
        self.assertIn('Aucun contrôle', health['inspection_status'])
        self.assertIn('Aucune assurance active', health['insurance_status'])
        self.assertEqual(health['registration_status'], 'Non renseigné')
        self.assertIn('Aucune vidange enregistrée', health['recommendations'])

    def test_oil_change_ok(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=60),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'good')
        self.assertIn('OK', health['oil_change_status'])

    def test_oil_change_warning_30_days(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_date=date.today() + timedelta(days=15),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'warning')
        self.assertIn('Prévue', health['oil_change_status'])

    def test_oil_change_overdue(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=100),
            mileage_at_service=45000,
            next_due_date=date.today() - timedelta(days=10),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'critical')
        self.assertIn('retard', health['oil_change_status'])

    def test_oil_change_mileage_exceeded(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_mileage=48000,
        )
        self.vehicle.mileage = 50000
        self.vehicle.save()
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'critical')
        self.assertIn('Kilométrage dépassé', health['oil_change_status'])

    def test_oil_change_mileage_warning(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=30),
            mileage_at_service=45000,
            next_due_mileage=50500,
        )
        self.vehicle.mileage = 50000
        self.vehicle.save()
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'warning')

    def test_inspection_ok(self):
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=30),
            result='passed',
            expiry_date=date.today() + timedelta(days=200),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'good')
        self.assertIn('OK', health['inspection_status'])

    def test_inspection_warning_90_days(self):
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=30),
            result='passed',
            expiry_date=date.today() + timedelta(days=30),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'warning')
        self.assertIn('Expire', health['inspection_status'])

    def test_inspection_expired_critical(self):
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=400),
            result='passed',
            expiry_date=date.today() - timedelta(days=30),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'critical')
        self.assertTrue(health['is_critical'])
        self.assertIn('Expiré', health['inspection_status'])

    def test_insurance_ok(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=300),
            is_active=True,
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'good')
        self.assertIn('OK', health['insurance_status'])

    def test_insurance_warning_30_days(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=300),
            end_date=date.today() + timedelta(days=15),
            is_active=True,
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'warning')
        self.assertIn('Expire', health['insurance_status'])

    def test_insurance_expired_is_not_returned_as_active(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=400),
            end_date=date.today() - timedelta(days=10),
            is_active=True,
        )
        self.assertIsNone(self.vehicle.get_active_insurance())

    def test_insurance_not_active(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=300),
            is_active=False,
        )
        health = get_vehicle_health(self.vehicle)
        self.assertIn('Aucune assurance active', health['insurance_status'])

    def test_carte_grise_ok(self):
        CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today() - timedelta(days=365),
            expiry_date=date.today() + timedelta(days=2000),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['registration_status'], 'OK')

    def test_carte_grise_no_expiry(self):
        CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today(),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['registration_status'], "OK - Sans date d'expiration")

    def test_carte_grise_expired(self):
        CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today() - timedelta(days=4000),
            expiry_date=date.today() - timedelta(days=30),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'critical')
        self.assertIn('Expirée', health['registration_status'])

    def test_carte_grise_warning_90_days(self):
        CarteGrise.objects.create(
            vehicle=self.vehicle,
            registration_number='AB-123-CD',
            issue_date=date.today() - timedelta(days=3000),
            expiry_date=date.today() + timedelta(days=30),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'warning')
        self.assertIn('Expire', health['registration_status'])

    def test_multiple_issues_critical_wins(self):
        MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type='oil_change',
            date=date.today() - timedelta(days=100),
            mileage_at_service=45000,
            next_due_date=date.today() - timedelta(days=10),
        )
        TechnicalInspection.objects.create(
            vehicle=self.vehicle,
            inspection_date=date.today() - timedelta(days=30),
            result='passed',
            expiry_date=date.today() + timedelta(days=30),
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'critical')

    def test_recommendations_limited_to_5(self):
        for i in range(7):
            MaintenanceRecord.objects.create(
                vehicle=self.vehicle,
                maintenance_type='oil_change',
                date=date.today() - timedelta(days=100 + i),
                mileage_at_service=45000,
                next_due_date=date.today() - timedelta(days=10 - i),
            )
        health = get_vehicle_health(self.vehicle)
        self.assertLessEqual(len(health['recommendations'].split('\n')), 6)

    def test_mileage_in_result(self):
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['mileage'], 50000)

    def test_no_oil_change_data(self):
        health = get_vehicle_health(self.vehicle)
        self.assertIsNone(health['days_until_next_oil_change'])
        self.assertIsNone(health['km_until_next_oil_change'])

    def test_no_oil_change_but_has_insurance_expired(self):
        Insurance.objects.create(
            vehicle=self.vehicle,
            company_name='AXA',
            policy_number='P1',
            start_date=date.today() - timedelta(days=400),
            end_date=date.today() - timedelta(days=10),
            is_active=True,
        )
        health = get_vehicle_health(self.vehicle)
        self.assertEqual(health['overall_status'], 'good')
        self.assertIn('Aucune assurance active', health['insurance_status'])


class DiagnosticViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pass1234')
        cls.other_user = User.objects.create_user(username='other', password='pass1234')
        cls.vehicle = Vehicle.objects.create(
            user=cls.user, name='Clio', brand='Renault',
            model='Clio 4', year=2020, mileage=50000,
        )
        cls.other_vehicle = Vehicle.objects.create(
            user=cls.other_user, name='Other', brand='O', model='X', year=2020,
        )

    def setUp(self):
        self.client.login(username='testuser', password='pass1234')

    def test_report_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse('diagnostics:report', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        expected = f"{reverse('accounts:login')}?next={reverse('diagnostics:report', kwargs={'vehicle_pk': self.vehicle.pk})}"
        self.assertRedirects(response, expected)

    def test_report_own_vehicle(self):
        response = self.client.get(
            reverse('diagnostics:report', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clio')
        self.assertIn('health', response.context)

    def test_report_other_vehicle_404(self):
        response = self.client.get(
            reverse('diagnostics:report', kwargs={'vehicle_pk': self.other_vehicle.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_report_creates_diagnostic_report(self):
        count_before = DiagnosticReport.objects.count()
        self.client.get(
            reverse('diagnostics:report', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(DiagnosticReport.objects.count(), count_before + 1)

    def test_report_context_has_health(self):
        response = self.client.get(
            reverse('diagnostics:report', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        health = response.context['health']
        self.assertIn('overall_status', health)
        self.assertIn('oil_change_status', health)
        self.assertIn('inspection_status', health)
        self.assertIn('insurance_status', health)
        self.assertIn('registration_status', health)
        self.assertIn('recommendations', health)

    def test_history_own_vehicle(self):
        response = self.client.get(
            reverse('diagnostics:history', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clio')

    def test_history_other_vehicle_404(self):
        response = self.client.get(
            reverse('diagnostics:history', kwargs={'vehicle_pk': self.other_vehicle.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_history_shows_reports(self):
        for _ in range(3):
            DiagnosticReport.objects.create(
                vehicle=self.vehicle,
                overall_status='good',
                mileage=50000,
            )
        response = self.client.get(
            reverse('diagnostics:history', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(len(response.context['reports']), 3)

    def test_history_limited_to_20(self):
        for i in range(25):
            DiagnosticReport.objects.create(
                vehicle=self.vehicle,
                overall_status='good',
                mileage=50000 + i,
            )
        response = self.client.get(
            reverse('diagnostics:history', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertLessEqual(len(response.context['reports']), 20)

    def test_diagnostic_report_fields(self):
        self.client.get(
            reverse('diagnostics:report', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        report = DiagnosticReport.objects.latest('report_date')
        self.assertEqual(report.vehicle, self.vehicle)
        self.assertIsNotNone(report.mileage)
        self.assertIn(report.overall_status, ['good', 'warning', 'critical'])
