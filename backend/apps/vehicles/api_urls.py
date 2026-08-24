from django.urls import path
from apps.vehicles import api

app_name = 'vehicles_api'

urlpatterns = [
    path('vehicules/', api.vehicle_search, name='search'),
    path('vehicles/', api.vehicle_list, name='list'),
    path('vehicles/<int:pk>/', api.vehicle_detail, name='detail'),
    path('vehicles/<int:pk>/dashboard/', api.vehicle_dashboard, name='dashboard'),
    path('vehicles/<int:pk>/maintenances/', api.vehicle_maintenances, name='maintenances'),
    path('vehicles/<int:pk>/expenses/', api.vehicle_expenses, name='expenses'),
    path('vehicles/<int:pk>/expenses/summary/', api.vehicle_expenses_summary, name='expenses_summary'),
    path('vehicles/<int:pk>/alerts/', api.vehicle_alerts, name='alerts'),
    path('vehicles/<int:pk>/tracked-items/', api.tracked_items, name='tracked_items'),
    path('vehicles/nhtsa/makes/', api.nhtsa_makes, name='nhtsa_makes'),
    path('vehicles/nhtsa/models/', api.nhtsa_models, name='nhtsa_models'),
    path('vehicles/nhtsa/decode-vin/<str:vin>/', api.nhtsa_decode_vin, name='nhtsa_decode_vin'),
]