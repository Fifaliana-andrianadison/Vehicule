# Carnet — Suivi de véhicules & garage

Application de suivi de véhicules permettant aux propriétaires de gérer l'entretien, les réparations, les pièces compatibles et les dépenses de leurs véhicules — avec un espace professionnel pour les garages, un système d'alertes de fin de vie des pièces, et une encyclopédie mécanique consultable.

## Fonctionnalités

### Espace propriétaire
- Gestion multi-véhicules (marque, modèle, année, VIN, kilométrage, immatriculation)
- Ajout de véhicule avec pré-remplissage automatique via l'API NHTSA vPIC
- Historique des entretiens et réparations
- Suivi des dépenses (par catégorie, par mois, par véhicule)
- Dashboard par véhicule (résumé financier, timeline, jauges)
- Catalogue de pièces filtrable par compatibilité véhicule
- Gestion documentaire (carte grise, assurance, factures)

### Alertes d'entretien
- Suivi de fin de vie par pièce (vidange, plaquettes, batterie, pneus...) basé sur kilométrage et/ou durée
- Statuts automatiques : à jour / à surveiller / critique
- Recalcul planifié via Celery (tâche quotidienne)

### Encyclopédie mécanique
- Base de fiches techniques génériques par marque/modèle/plage d'années
- Plans d'entretien constructeur type (intervalle km / temps par intervention)
- Alimentée et enrichie via l'API NHTSA vPIC

### Espace garage (compte professionnel)
- Gestion de plusieurs véhicules clients
- Ordres de réparation (devis → en cours → attente pièces → facturé)
- Suivi financier : revenu du mois, impayés, ticket moyen
- Répercussion automatique des factures sur les dépenses du véhicule client

## Stack technique

- **Backend** : Django 5 + Django REST Framework, SimpleJWT, MySQL
- **Frontend** : React (Vite), React Router, Axios, TailwindCSS, Recharts
- **Tâches planifiées** : Celery + Redis (alertes, rappels)
- **Base de données** : MySQL (via XAMPP en local)
- **API externe** : NHTSA vPIC (gratuite, sans clé) — récupération des types, marques, modèles et décodage VIN

## Prérequis

- Python 3.11+
- Node.js 18+
- XAMPP (MySQL + phpMyAdmin)
- Redis (pour les alertes/notifications planifiées)

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd vehicule-tracker
```

### 2. Base de données (XAMPP)

Démarrer **MySQL** depuis le panneau XAMPP, puis créer la base via phpMyAdmin (`http://localhost/phpmyadmin`) :

```sql
CREATE DATABASE vehicule_tracker CHARACTER SET utf8mb4;
```

### 3. Backend (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Fichier `.env` :

```
DEBUG=True
SECRET_KEY=change-me
DB_NAME=vehicule_tracker
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
NHTSA_API_BASE=https://vpic.nhtsa.dot.gov/api
```

> Si `mysqlclient` pose problème à l'installation sous Windows, voir la section Dépannage.

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend : `http://localhost:8000` — Admin : `http://localhost:8000/admin`

### 4. Frontend (React)

```bash
cd frontend
npm install
```

Fichier `.env` :

```
VITE_API_URL=http://localhost:8000/api
```

```bash
npm run dev
```

Frontend : `http://localhost:5173`

### 5. Celery (alertes automatiques)

Nécessite Redis lancé localement.

```bash
# Terminal 1 — worker
celery -A config worker -l info

# Terminal 2 — scheduler (recalcule les alertes chaque nuit)
celery -A config beat -l info
```

## Structure du projet

```
vehicule-tracker/
├── backend/
│   ├── config/                # Settings Django
│   ├── apps/
│   │   ├── users/
│   │   ├── vehicles/          # Vehicle, Brand, VehicleModel, VehicleType
│   │   ├── maintenance/       # Maintenance, MaintenanceRule, TrackedItem, tasks.py
│   │   ├── parts/             # Part, PartCategory, PartCompatibility
│   │   ├── expenses/          # Expense, ExpenseCategory
│   │   ├── documents/         # Documents (carte grise, assurance...)
│   │   ├── garage/            # Garage, GarageStaff, RepairOrder, RepairOrderPart
│   │   └── reference/         # VehicleReference — encyclopédie mécanique
│   ├── core/                  # Permissions, pagination, utils partagés
│   ├── media/
│   └── manage.py
│
└── frontend/
    └── src/
        ├── api/
        ├── components/
        ├── pages/
        ├── context/
        ├── hooks/
        └── routes/
```

## Récupération des véhicules — API NHTSA vPIC (gratuite)

L'application s'appuie sur l'API **NHTSA vPIC** (Vehicle Product Information Catalog), gratuite, sans clé et sans inscription, pour peupler automatiquement les types, marques, modèles et décoder les VIN.

Base URL : `https://vpic.nhtsa.dot.gov/api`

```
# Tous les types de véhicules pour une marque
GET /vehicles/GetVehicleTypesForMake/{make}?format=json

# Toutes les marques pour un type de véhicule
GET /vehicles/GetMakesForVehicleType/{type}?format=json
# ex: /vehicles/GetMakesForVehicleType/car?format=json

# Tous les modèles pour une marque + année + type
GET /vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}/vehicletype/{type}?format=json

# Tous les modèles d'une marque (par ID)
GET /vehicles/GetModelsForMakeId/{makeId}?format=json

# Décoder un VIN complet (marque, modèle, année, moteur, carrosserie...)
GET /vehicles/decodevin/{vin}?format=json

# Toutes les valeurs possibles pour une variable (ex: types de carrosserie)
GET /vehicles/GetVehicleVariableValuesList/{variable}?format=json
```

`apps/vehicles/services.py` centralise ces appels côté backend, avec mise en cache locale des résultats dans `Brand` et `VehicleModel` pour éviter de solliciter l'API à chaque requête. Ces mêmes données alimentent aussi `apps/reference/` pour construire les fiches de l'encyclopédie mécanique.

## Endpoints API principaux

```
POST   /api/auth/register/
POST   /api/auth/login/

GET    /api/vehicles/
POST   /api/vehicles/
GET    /api/vehicles/{id}/
GET    /api/vehicles/{id}/dashboard/
GET    /api/vehicles/{id}/maintenances/
POST   /api/vehicles/{id}/maintenances/
GET    /api/vehicles/{id}/expenses/
GET    /api/vehicles/{id}/expenses/summary/
GET    /api/vehicles/{id}/alerts/

GET    /api/vehicles/nhtsa/makes/?type=car
GET    /api/vehicles/nhtsa/models/?make=&type=&year=
GET    /api/vehicles/nhtsa/decode-vin/{vin}/

GET    /api/parts/?vehicle={id}

GET    /api/reference/vehicles/?type=car&brand=Toyota
GET    /api/reference/vehicles/{id}/
GET    /api/reference/vehicles/{id}/schedule/
GET    /api/reference/vehicles/{id}/parts/

GET    /api/garage/repair-orders/
POST   /api/garage/repair-orders/
GET    /api/garage/dashboard/
```

## Dépannage

**Erreur d'installation `mysqlclient` sous Windows :**

```bash
pip install pymysql
```

Puis dans `backend/config/__init__.py` :

```python
import pymysql
pymysql.install_as_MySQLdb()
```

**Erreur de connexion MySQL :** vérifier que le service MySQL est démarré dans XAMPP et que le port `3306` est libre.

**API NHTSA vPIC lente ou indisponible :** les données étant mises en cache localement après premier appel, l'application reste fonctionnelle pour les véhicules déjà synchronisés.

## Licence

Projet privé — usage personnel.
