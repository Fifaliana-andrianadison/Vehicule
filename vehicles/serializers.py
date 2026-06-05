from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'brand', 'model', 'name', 'year', 'registration_number', 'mileage', 'fuel_type', 'vehicle_type']
