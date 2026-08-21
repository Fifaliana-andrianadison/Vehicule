from django.urls import path
from . import api

app_name = 'vehicles_api'

urlpatterns = [
    path('vehicules/', api.vehicle_search, name='search'),
]
