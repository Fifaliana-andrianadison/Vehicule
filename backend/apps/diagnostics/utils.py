from datetime import date, timedelta
from apps.vehicles.models import Vehicle


def get_vehicle_health(vehicle):
    from apps.maintenance.models import MaintenanceRecord
    from apps.documents.models import TechnicalInspection, Insurance, CarteGrise

    today = date.today()
    issues = []
    status = 'good'
    is_critical = False

    last_oil = vehicle.get_last_oil_change()
    oil_status = 'Non renseigné'
    days_until_oil = None
    km_until_oil = None
    if last_oil:
        if last_oil.next_due_date:
            days_until_oil = (last_oil.next_due_date - today).days
            if days_until_oil < 0:
                oil_status = f'En retard de {abs(days_until_oil)} jours'
                issues.append(f'Vidange en retard depuis le {last_oil.next_due_date}')
                status = 'critical'
            elif days_until_oil <= 30:
                oil_status = f'Prévue dans {days_until_oil} jours'
                issues.append(f'Vidange à prévoir dans {days_until_oil} jours')
                if status != 'critical':
                    status = 'warning'
            else:
                oil_status = f'OK - Prochaine dans {days_until_oil} jours'
        if last_oil.next_due_mileage and vehicle.mileage:
            km_until_oil = last_oil.next_due_mileage - vehicle.mileage
            if km_until_oil < 0:
                oil_status += ' - Kilométrage dépassé'
                issues.append(f'Vidange nécessaire (kilométrage dépassé de {abs(km_until_oil)} km)')
                status = 'critical'
            elif km_until_oil <= 1000:
                oil_status += f' - Plus que {km_until_oil} km'
                if status != 'critical':
                    status = 'warning'
    else:
        issues.append('Aucune vidange enregistrée')
        oil_status = 'Aucune vidange'

    last_inspection = vehicle.get_latest_inspection()
    inspection_status = 'Non renseigné'
    days_until_inspection = None
    if last_inspection and last_inspection.expiry_date:
        days_until_inspection = (last_inspection.expiry_date - today).days
        if days_until_inspection < 0:
            inspection_status = f'Expiré depuis {abs(days_until_inspection)} jours'
            issues.append(f'Contrôle technique expiré depuis le {last_inspection.expiry_date}')
            status = 'critical'
            is_critical = True
        elif days_until_inspection <= 90:
            inspection_status = f'Expire dans {days_until_inspection} jours'
            issues.append(f'Contrôle technique à renouveler dans {days_until_inspection} jours')
            if status != 'critical':
                status = 'warning'
        else:
            inspection_status = f'OK - Valide jusqu\'au {last_inspection.expiry_date}'
    else:
        issues.append('Aucun contrôle technique enregistré')
        inspection_status = 'Aucun contrôle'

    active_insurance = vehicle.get_active_insurance()
    insurance_status = 'Non renseigné'
    days_until_insurance = None
    if active_insurance:
        days_until_insurance = (active_insurance.end_date - today).days
        if days_until_insurance < 0:
            insurance_status = f'Expirée depuis {abs(days_until_insurance)} jours'
            issues.append(f'Assurance expirée')
            status = 'critical'
            is_critical = True
        elif days_until_insurance <= 30:
            insurance_status = f'Expire dans {days_until_insurance} jours'
            issues.append(f'Assurance à renouveler dans {days_until_insurance} jours')
            if status != 'critical':
                status = 'warning'
        else:
            insurance_status = f'OK - Valide jusqu\'au {active_insurance.end_date}'
    else:
        issues.append('Aucune assurance active')
        insurance_status = 'Aucune assurance active'

    carte_grise = hasattr(vehicle, 'carte_grise') and vehicle.carte_grise
    registration_status = 'Non renseigné'
    if carte_grise and carte_grise.expiry_date:
        days_until_registration = (carte_grise.expiry_date - today).days
        if days_until_registration < 0:
            registration_status = f'Expirée depuis {abs(days_until_registration)} jours'
            issues.append(f'Carte grise expirée')
            status = 'critical'
        elif days_until_registration <= 90:
            registration_status = f'Expire dans {days_until_registration} jours'
            if status != 'critical':
                status = 'warning'
        else:
            registration_status = 'OK'
    elif carte_grise:
        registration_status = 'OK - Sans date d\'expiration'

    recommendations = '\n'.join(f'- {issue}' for issue in issues[:5])
    if not recommendations:
        recommendations = 'Aucun problème détecté. Votre véhicule est en bon état.'

    return {
        'overall_status': status,
        'is_critical': is_critical or status == 'critical',
        'oil_change_status': oil_status,
        'inspection_status': inspection_status,
        'insurance_status': insurance_status,
        'registration_status': registration_status,
        'days_until_next_oil_change': days_until_oil,
        'km_until_next_oil_change': km_until_oil,
        'days_until_inspection': days_until_inspection,
        'days_until_insurance_expiry': days_until_insurance,
        'recommendations': recommendations,
        'mileage': vehicle.mileage,
    }
