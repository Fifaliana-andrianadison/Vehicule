from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from vehicles.models import Vehicle
from maintenance.models import MaintenanceRecord
from documents.models import Insurance, CarteGrise, TechnicalInspection
from diagnostics.models import DiagnosticReport
from random import randint, choice


class Command(BaseCommand):
    help = 'Crée des données d\'exemple pour le développement'

    def handle(self, *args, **options):
        if User.objects.filter(username='demo').exists():
            self.stdout.write(self.style.WARNING('Les données d\'exemple existent déjà.'))
            return

        user = User.objects.create_user(
            username='demo',
            email='demo@example.com',
            password='demo12345',
            first_name='Jean',
            last_name='Dupont',
        )
        user.profile.phone = '06 12 34 56 78'
        user.profile.address = '12 Rue de Paris, 75001 Paris'
        user.profile.save()
        self.stdout.write(self.style.SUCCESS('[OK] Utilisateur "demo" créé (mdp: demo12345)'))

        vehicles_data = [
            {'name': 'Clio', 'brand': 'Renault', 'model': 'Clio 5', 'year': 2021, 'vin': 'VF1AAAAAA12345678', 'registration': 'AB-123-CD', 'mileage': 45000},
            {'name': '308', 'brand': 'Peugeot', 'model': '308', 'year': 2020, 'vin': 'VF3BBBBBB23456789', 'registration': 'EF-456-GH', 'mileage': 62000},
            {'name': 'Golf', 'brand': 'Volkswagen', 'model': 'Golf 8', 'year': 2022, 'vin': 'WVWCCCCC34567890', 'registration': 'IJ-789-KL', 'mileage': 28000},
        ]

        vehicles = []
        for vd in vehicles_data:
            v = Vehicle.objects.create(
                user=user,
                name=vd['name'],
                brand=vd['brand'],
                model=vd['model'],
                year=vd['year'],
                vehicle_type=choice(['car', 'car', 'car', 'motorcycle', 'van']),
                fuel_type=choice(['gasoline', 'diesel', 'hybrid']),
                vin=vd['vin'],
                registration_number=vd['registration'],
                mileage=vd['mileage'],
                purchase_date=date(vd['year'] - 1, randint(1, 6), randint(1, 28)),
            )
            vehicles.append(v)
            self.stdout.write(self.style.SUCCESS(f'  [OK] Véhicule {v.brand} {v.model} créé'))

        today = date.today()

        maintenance_types = [
            {'type': 'oil_change', 'next_km': 10000, 'next_days': 365},
            {'type': 'brake', 'next_km': 30000, 'next_days': None},
            {'type': 'tire', 'next_km': 40000, 'next_days': None},
            {'type': 'filter', 'next_km': 20000, 'next_days': None},
            {'type': 'battery', 'next_km': None, 'next_days': 730},
        ]

        records_created = 0
        for v in vehicles:
            for i, mt in enumerate(maintenance_types):
                service_date = today - timedelta(days=randint(30, 400))
                km = max(0, v.mileage - randint(5000, 15000) + i * 8000)
                next_km = km + mt['next_km'] if mt['next_km'] else None
                next_date = (service_date + timedelta(days=mt['next_days'])) if mt['next_days'] else None

                MaintenanceRecord.objects.create(
                    vehicle=v,
                    maintenance_type=mt['type'],
                    description=f'{mt["type"]} - {v.name}',
                    date=service_date,
                    mileage_at_service=km,
                    cost=randint(50, 500),
                    garage_name=choice(['Garage du Centre', 'Feu Vert', 'Norauto', 'Midas', 'Speedy']),
                    next_due_mileage=next_km,
                    next_due_date=next_date if next_date and next_date > today else (today + timedelta(days=randint(10, 60)) if mt['type'] == 'oil_change' else None),
                    notes='Entretien régulier effectué',
                )
                records_created += 1
        self.stdout.write(self.style.SUCCESS(f'[OK] {records_created} entretiens créés'))

        Insurance.objects.create(
            vehicle=vehicles[0],
            company_name='MAIF',
            policy_number='POL-2021-001',
            start_date=date(2024, 1, 1),
            end_date=today + timedelta(days=randint(30, 200)),
            premium_amount=randint(300, 800),
            is_active=True,
        )
        Insurance.objects.create(
            vehicle=vehicles[1],
            company_name='AXA',
            policy_number='POL-2022-002',
            start_date=date(2024, 6, 1),
            end_date=today + timedelta(days=randint(5, 25)),
            premium_amount=randint(400, 900),
            is_active=True,
        )
        Insurance.objects.create(
            vehicle=vehicles[2],
            company_name='Groupama',
            policy_number='POL-2023-003',
            start_date=date(2023, 3, 1),
            end_date=today - timedelta(days=30),
            premium_amount=randint(350, 700),
            is_active=False,
        )
        self.stdout.write(self.style.SUCCESS('[OK] 3 assurances créées'))

        TechnicalInspection.objects.create(
            vehicle=vehicles[0],
            inspection_date=today - timedelta(days=180),
            result='passed',
            expiry_date=today + timedelta(days=randint(60, 200)),
            mileage_at_inspection=35000,
            garage_name='Autosécurité',
            notes='Contrôle favorable',
        )
        TechnicalInspection.objects.create(
            vehicle=vehicles[1],
            inspection_date=today - timedelta(days=400),
            result='partial',
            expiry_date=today - timedelta(days=30),
            mileage_at_inspection=55000,
            garage_name='Sécuritest',
            notes='Pneus avant à changer',
        )
        TechnicalInspection.objects.create(
            vehicle=vehicles[2],
            inspection_date=today - timedelta(days=90),
            result='passed',
            expiry_date=today + timedelta(days=randint(180, 250)),
            mileage_at_inspection=20000,
            garage_name='Autovision',
            notes='OK',
        )
        self.stdout.write(self.style.SUCCESS('[OK] 3 contrôles techniques créés'))

        CarteGrise.objects.create(
            vehicle=vehicles[0],
            registration_number='AB-123-CD',
            issue_date=date(2021, 3, 15),
            expiry_date=today + timedelta(days=randint(100, 300)),
        )
        CarteGrise.objects.create(
            vehicle=vehicles[1],
            registration_number='EF-456-GH',
            issue_date=date(2020, 7, 10),
            expiry_date=today + timedelta(days=randint(100, 300)),
        )
        CarteGrise.objects.create(
            vehicle=vehicles[2],
            registration_number='IJ-789-KL',
            issue_date=date(2022, 1, 20),
            expiry_date=None,
        )
        self.stdout.write(self.style.SUCCESS('[OK] 3 cartes grises créées'))

        for v in vehicles:
            DiagnosticReport.objects.create(
                vehicle=v,
                overall_status='good',
                mileage=v.mileage,
                oil_change_status='OK',
                inspection_status='OK',
                insurance_status='OK',
                registration_status='OK',
                recommendations='Aucun problème détecté.',
            )
        self.stdout.write(self.style.SUCCESS('[OK] 3 rapports de diagnostic créés'))

        self.stdout.write(self.style.SUCCESS('\n[OK] Donnees d\'exemple creees avec succes !'))
        self.stdout.write('   Connectez-vous avec : demo / demo12345')
