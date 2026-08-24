import requests
from decouple import config

NHTSA_API_BASE = config('NHTSA_API_BASE', default='https://vpic.nhtsa.dot.gov/api')
TIMEOUT = 20


def _get(endpoint, params=None):
    url = f"{NHTSA_API_BASE}{endpoint}"
    params = params or {}
    params.setdefault('format', 'json')
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get('Results', data if isinstance(data, list) else [])


def get_vehicle_types_for_make(make):
    try:
        return _get(f"/vehicles/GetVehicleTypesForMake/{make}")
    except requests.RequestException:
        return []


def get_makes_for_vehicle_type(vehicle_type):
    try:
        return _get(f"/vehicles/GetMakesForVehicleType/{vehicle_type}")
    except requests.RequestException:
        return []


def get_models_for_make_year(make, year, vehicle_type):
    try:
        endpoint = (
            f"/vehicles/GetModelsForMakeYear/make/{make}"
            f"/modelyear/{year}/vehicletype/{vehicle_type}"
        )
        return _get(endpoint)
    except requests.RequestException:
        return []


def get_models_for_make_id(make_id):
    try:
        return _get(f"/vehicles/GetModelsForMakeId/{make_id}")
    except requests.RequestException:
        return []


def decode_vin(vin):
    try:
        return _get(f"/vehicles/decodevin/{vin}")
    except requests.RequestException:
        return []


def decode_vin_to_vehicle_data(vin):
    results = decode_vin(vin)
    if not results:
        return None
    flat = {}
    for row in results:
        variable = row.get('Variable')
        value = row.get('Value')
        if variable and value:
            flat[variable.lower()] = value
    return {
        'vin': vin,
        'brand': flat.get('make') or flat.get('make name'),
        'model': flat.get('model') or flat.get('model name'),
        'year': flat.get('model year'),
        'vehicle_type': (flat.get('vehicle type') or '').lower(),
        'body_type': flat.get('body class'),
        'engine': flat.get('engine model') or flat.get('displacement (l)'),
        'fuel_type': flat.get('fuel type - primary'),
    }