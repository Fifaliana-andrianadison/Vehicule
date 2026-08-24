from rest_framework import serializers

from apps.vehicles.models import Vehicle
from apps.maintenance.models import MaintenanceRecord, TrackedItem
from apps.expenses.models import Expense


class VehicleSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='user.username', read_only=True)
    health = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'name', 'brand', 'model', 'year', 'vehicle_type', 'fuel_type',
            'vin', 'registration_number', 'mileage', 'photo', 'purchase_date',
            'is_active', 'owner_name', 'health', 'created_at', 'updated_at',
        ]
        read_only_fields = ['owner_name', 'health', 'created_at', 'updated_at']

    def get_health(self, obj):
        from apps.diagnostics.utils import get_vehicle_health
        return get_vehicle_health(obj)

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        return attrs


class VehicleCreateSerializer(VehicleSerializer):
    class Meta(VehicleSerializer.Meta):
        read_only_fields = ['owner_name', 'health', 'created_at', 'updated_at']


class MaintenanceSerializer(serializers.ModelSerializer):
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'vehicle', 'maintenance_type', 'maintenance_type_display',
            'description', 'date', 'mileage_at_service', 'cost', 'garage_name',
            'next_due_mileage', 'next_due_date', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['vehicle', 'created_at', 'updated_at']

    def validate(self, attrs):
        attrs['vehicle'] = self.context['vehicle']
        return attrs


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'vehicle', 'category', 'category_name', 'amount', 'date',
            'description', 'repair_order', 'created_at', 'updated_at',
        ]
        read_only_fields = ['vehicle', 'created_at', 'updated_at']

    def validate(self, attrs):
        attrs['vehicle'] = self.context['vehicle']
        return attrs


class TrackedItemSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TrackedItem
        fields = [
            'id', 'vehicle', 'name', 'part', 'interval_km', 'interval_months',
            'last_service_km', 'last_service_date', 'status', 'status_display',
            'recalced_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['vehicle', 'status', 'status_display', 'recalced_at', 'created_at', 'updated_at']

    def validate(self, attrs):
        attrs['vehicle'] = self.context['vehicle']
        return attrs