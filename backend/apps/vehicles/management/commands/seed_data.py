from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from apps.vehicles.models import Vehicle
from apps.maintenance.models import MaintenanceRecord, TrackedItem
from apps.documents.models import Insurance, CarteGrise, TechnicalInspection
from apps.diagnostics.models import DiagnosticReport
from apps.expenses.models import Expense, ExpenseCategory
from apps.parts.models import Part, PartCategory, PartCompatibility
from apps.garage.models import Garage, GarageStaff, RepairOrder, RepairOrderPart
from apps.reference.models import VehicleReference, MaintenanceSchedule
from random import randint, choice


class Command(BaseCommand):
    help = 'Crée des données d\'exemple complètes (propriétaire + garage + encyclopédie)'

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

        garage_user = User.objects.create_user(
            username='garage',
            email='garage@example.com',
            password='garage12345',
            first_name='Marc',
            last_name='Martin',
        )
        self.stdout.write(self.style.SUCCESS('[OK] Utilisateur "garage" créé (mdp: garage12345)'))

        today = date.today()

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
                vehicle_type='car',
                fuel_type=choice(['gasoline', 'diesel', 'hybrid']),
                vin=vd['vin'],
                registration_number=vd['registration'],
                mileage=vd['mileage'],
                purchase_date=date(vd['year'] - 1, randint(1, 6), randint(1, 28)),
            )
            vehicles.append(v)
            self.stdout.write(self.style.SUCCESS(f'  [OK] Véhicule {v.brand} {v.model} créé'))

        # -------------------------------------------------------------
        # Entretiens
        # -------------------------------------------------------------
        maintenance_types = [
            {'type': 'oil_change', 'next_km': 10000, 'next_days': 365},
            {'type': 'brake', 'next_km': 30000, 'next_days': None},
            {'type': 'tire', 'next_km': 40000, 'next_days': None},
            {'type': 'filter', 'next_km': 20000, 'next_days': None},
            {'type': 'battery', 'next_km': None, 'next_days': 730},
        ]
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
        self.stdout.write(self.style.SUCCESS('[OK] Entretiens créés'))

        # -------------------------------------------------------------
        # Documents
        # -------------------------------------------------------------
        Insurance.objects.create(vehicle=vehicles[0], company_name='MAIF', policy_number='POL-2021-001',
                                 start_date=date(2024, 1, 1), end_date=today + timedelta(days=randint(30, 200)),
                                 premium_amount=randint(300, 800), is_active=True)
        Insurance.objects.create(vehicle=vehicles[1], company_name='AXA', policy_number='POL-2022-002',
                                 start_date=date(2024, 6, 1), end_date=today + timedelta(days=randint(5, 25)),
                                 premium_amount=randint(400, 900), is_active=True)
        Insurance.objects.create(vehicle=vehicles[2], company_name='Groupama', policy_number='POL-2023-003',
                                 start_date=date(2023, 3, 1), end_date=today - timedelta(days=30),
                                 premium_amount=randint(350, 700), is_active=False)
        TechnicalInspection.objects.create(vehicle=vehicles[0], inspection_date=today - timedelta(days=180), result='passed',
                                           expiry_date=today + timedelta(days=randint(60, 200)), mileage_at_inspection=35000,
                                           garage_name='Autosécurité', notes='Contrôle favorable')
        TechnicalInspection.objects.create(vehicle=vehicles[1], inspection_date=today - timedelta(days=400), result='partial',
                                           expiry_date=today - timedelta(days=30), mileage_at_inspection=55000,
                                           garage_name='Sécuritest', notes='Pneus avant à changer')
        TechnicalInspection.objects.create(vehicle=vehicles[2], inspection_date=today - timedelta(days=90), result='passed',
                                           expiry_date=today + timedelta(days=randint(180, 250)), mileage_at_inspection=20000,
                                           garage_name='Autovision', notes='OK')
        CarteGrise.objects.create(vehicle=vehicles[0], registration_number='AB-123-CD', issue_date=date(2021, 3, 15),
                                  expiry_date=today + timedelta(days=randint(100, 300)))
        CarteGrise.objects.create(vehicle=vehicles[1], registration_number='EF-456-GH', issue_date=date(2020, 7, 10),
                                  expiry_date=today + timedelta(days=randint(100, 300)))
        CarteGrise.objects.create(vehicle=vehicles[2], registration_number='IJ-789-KL', issue_date=date(2022, 1, 20),
                                  expiry_date=None)
        for v in vehicles:
            DiagnosticReport.objects.create(vehicle=v, overall_status='good', mileage=v.mileage,
                                            oil_change_status='OK', inspection_status='OK',
                                            insurance_status='OK', registration_status='OK',
                                            recommendations='Aucun problème détecté.')
        self.stdout.write(self.style.SUCCESS('[OK] Documents et diagnostics créés'))

        # -------------------------------------------------------------
        # Dépenses
        # -------------------------------------------------------------
        cat_fuel, _ = ExpenseCategory.objects.get_or_create(name='Carburant')
        cat_insurance, _ = ExpenseCategory.objects.get_or_create(name='Assurance')
        cat_maintenance, _ = ExpenseCategory.objects.get_or_create(name='Entretien')
        cat_repair, _ = ExpenseCategory.objects.get_or_create(name='Réparation')
        cat_tax, _ = ExpenseCategory.objects.get_or_create(name='Taxes')
        ExpenseCategory.objects.get_or_create(name='Autre')
        for v in vehicles:
            for _ in range(6):
                Expense.objects.create(
                    vehicle=v,
                    category=choice([cat_fuel, cat_fuel, cat_insurance, cat_maintenance, cat_repair, cat_tax]),
                    amount=randint(20, 500),
                    date=today - timedelta(days=randint(0, 300)),
                    description=choice(['Plein de carburant', 'Vignette', 'Assurance annuelle', 'Révision', 'Réparation freins', 'Changement pneus']),
                )
        self.stdout.write(self.style.SUCCESS('[OK] Dépenses créées'))

        # -------------------------------------------------------------
        # Pièces + compatibilités
        # -------------------------------------------------------------
        cat_brakes, _ = PartCategory.objects.get_or_create(name='Freins')
        cat_motor, _ = PartCategory.objects.get_or_create(name='Moteur')
        cat_electric, _ = PartCategory.objects.get_or_create(name='Électrique')
        cat_filter, _ = PartCategory.objects.get_or_create(name='Filtres')
        cat_tires, _ = PartCategory.objects.get_or_create(name='Pneus')
        PartCategory.objects.get_or_create(name='Carrosserie')
        parts_data = [
            {'name': 'Plaquettes de frein avant', 'category': cat_brakes, 'reference': 'BRK-100', 'brand': 'Brembo', 'price': 45},
            {'name': 'Disques de frein avant', 'category': cat_brakes, 'reference': 'BRK-200', 'brand': 'Brembo', 'price': 120},
            {'name': 'Courroie de distribution', 'category': cat_motor, 'reference': 'MOT-301', 'brand': 'Gates', 'price': 90},
            {'name': 'Filtre à huile', 'category': cat_filter, 'reference': 'FIL-401', 'brand': 'Mann', 'price': 12},
            {'name': 'Filtre à air', 'category': cat_filter, 'reference': 'FIL-402', 'brand': 'Mann', 'price': 18},
            {'name': 'Batterie 12V 70Ah', 'category': cat_electric, 'reference': 'ELE-501', 'brand': 'Varta', 'price': 150},
            {'name': 'Bougies d\'allumage', 'category': cat_electric, 'reference': 'ELE-502', 'brand': 'NGK', 'price': 40},
            {'name': 'Pneus 205/55 R16', 'category': cat_tires, 'reference': 'TIR-601', 'brand': 'Michelin', 'price': 110},
        ]
        parts = []
        for pd in parts_data:
            p = Part.objects.create(**pd, vehicle_type='car', description=f'{pd["name"]} compatible avec véhicules particuliers.')
            parts.append(p)
        for p in parts:
            for v in vehicles:
                PartCompatibility.objects.get_or_create(part=p, vehicle=v)
        self.stdout.write(self.style.SUCCESS('[OK] Pièces et compatibilités créées'))

        # -------------------------------------------------------------
        # Éléments suivis (alertes)
        # -------------------------------------------------------------
        tracked_data = [
            {'name': 'Vidange moteur', 'interval_km': 10000, 'interval_months': 12, 'part': parts[3]},
            {'name': 'Plaquettes avant', 'interval_km': 30000, 'interval_months': None, 'part': parts[0]},
            {'name': 'Batterie', 'interval_km': None, 'interval_months': 48, 'part': parts[5]},
            {'name': 'Courroie de distribution', 'interval_km': 120000, 'interval_months': None, 'part': parts[2]},
        ]
        for v in vehicles:
            for td in tracked_data:
                last_km = max(0, v.mileage - randint(2000, 15000))
                TrackedItem.objects.create(
                    vehicle=v, name=td['name'], part=td['part'],
                    interval_km=td['interval_km'], interval_months=td['interval_months'],
                    last_service_km=last_km,
                    last_service_date=today - timedelta(days=randint(30, 500)),
                )
        self.stdout.write(self.style.SUCCESS('[OK] Éléments suivis créés (alertes)'))

        # -------------------------------------------------------------
        # Garage + ordres de réparation
        # -------------------------------------------------------------
        garage = Garage.objects.create(
            owner=garage_user, name='Garage Martin',
            address='8 Rue du Garage, 75011 Paris',
            phone='01 42 00 00 00', email='contact@garagemartin.fr', siret='12345678900011',
        )
        GarageStaff.objects.create(garage=garage, user=garage_user, role=GarageStaff.Role.ADMIN)
        ro1 = RepairOrder.objects.create(
            garage=garage, vehicle=vehicles[0], customer=user,
            title='Révision 45000 km', description='Révision complète avec vidange.',
            status=RepairOrder.Status.IN_PROGRESS, estimated_cost=250,
        )
        RepairOrderPart.objects.create(repair_order=ro1, part=parts[3], name=parts[3].name, quantity=1, unit_price=12)
        ro2 = RepairOrder.objects.create(
            garage=garage, vehicle=vehicles[1], customer=user,
            title='Remplacement plaquettes avant', description='Usure constatée au contrôle technique.',
            status=RepairOrder.Status.QUOTE, estimated_cost=180,
        )
        RepairOrderPart.objects.create(repair_order=ro2, part=parts[0], name=parts[0].name, quantity=1, unit_price=45)
        ro3 = RepairOrder.objects.create(
            garage=garage, vehicle=vehicles[2], customer=user,
            title='Vidange + filtres', description='Vidange moteur et filtres.',
            status=RepairOrder.Status.INVOICED, total_cost=220, estimated_cost=220,
        )
        RepairOrderPart.objects.create(repair_order=ro3, part=parts[3], name=parts[3].name, quantity=1, unit_price=12)
        RepairOrderPart.objects.create(repair_order=ro3, part=parts[4], name=parts[4].name, quantity=1, unit_price=18)
        cat_garage, _ = ExpenseCategory.objects.get_or_create(name='Garage')
        Expense.objects.create(vehicle=vehicles[2], category=cat_garage, amount=220, date=today,
                               description='Facture garage : Vidange + filtres', repair_order=ro3)
        self.stdout.write(self.style.SUCCESS('[OK] Garage et ordres de réparation créés'))

        # -------------------------------------------------------------
        # Encyclopédie mécanique
        # -------------------------------------------------------------
        ref_data = [
            {'vehicle_type': 'car', 'brand': 'Renault', 'model': 'Clio', 'year_start': 2019, 'year_end': 2024,
             'engine_info': 'Essence / Diesel', 'body_type': 'Citadine'},
            {'vehicle_type': 'car', 'brand': 'Peugeot', 'model': '308', 'year_start': 2017, 'year_end': 2024,
             'engine_info': 'Essence / Diesel / Hybride', 'body_type': 'Compacte'},
            {'vehicle_type': 'car', 'brand': 'Volkswagen', 'model': 'Golf', 'year_start': 2020, 'year_end': 2024,
             'engine_info': 'Essence / Diesel / Hybride', 'body_type': 'Compacte'},
        ]
        schedule_data = [
            {'intervention_type': 'oil_change', 'label': 'Vidange moteur', 'interval_km': 10000, 'interval_months': 12, 'cost_estimate': 120},
            {'intervention_type': 'filter', 'label': 'Filtre à huile', 'interval_km': 20000, 'interval_months': 24, 'cost_estimate': 30},
            {'intervention_type': 'brake', 'label': 'Plaquettes de frein', 'interval_km': 30000, 'interval_months': None, 'cost_estimate': 180},
            {'intervention_type': 'tire', 'label': 'Rotation des pneus', 'interval_km': 15000, 'interval_months': None, 'cost_estimate': 50},
            {'intervention_type': 'battery', 'label': 'Remplacement batterie', 'interval_km': None, 'interval_months': 48, 'cost_estimate': 150},
            {'intervention_type': 'timing_belt', 'label': 'Distribution', 'interval_km': 120000, 'interval_months': None, 'cost_estimate': 600},
            {'intervention_type': 'air_conditioning', 'label': 'Recharge climatisation', 'interval_km': None, 'interval_months': 24, 'cost_estimate': 90},
        ]
        for rd in ref_data:
            ref = VehicleReference.objects.create(**rd, description=f"Fiche technique générique {rd['brand']} {rd['model']}.")
            for sd in schedule_data:
                MaintenanceSchedule.objects.create(vehicle_reference=ref, **sd)
        self.stdout.write(self.style.SUCCESS('[OK] Encyclopédie mécanique créée'))

        self.stdout.write(self.style.SUCCESS('\n[OK] Données d\'exemple complètes créées avec succès !'))
        self.stdout.write('   Propriétaire : demo / demo12345')
        self.stdout.write('   Garage      : garage / garage12345')
        self.stdout.write('   Admin       : admin / admin12345')