from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.reference.models import VehicleReference, MaintenanceSchedule
from apps.parts.models import Part
from apps.parts.api import PartSerializer


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    intervention_display = serializers.CharField(source='get_intervention_type_display', read_only=True)

    class Meta:
        model = MaintenanceSchedule
        fields = [
            'id', 'intervention_type', 'intervention_display', 'label',
            'interval_km', 'interval_months', 'cost_estimate',
        ]


class VehicleReferenceSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    schedule_count = serializers.IntegerField(source='schedule.count', read_only=True)

    class Meta:
        model = VehicleReference
        fields = [
            'id', 'vehicle_type', 'type_display', 'brand', 'model',
            'year_start', 'year_end', 'engine_info', 'body_type',
            'description', 'schedule_count',
        ]


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reference_list(request):
    if request.method == 'POST':
        serializer = VehicleReferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    qs = VehicleReference.objects.all()
    vehicle_type = request.GET.get('type')
    brand = request.GET.get('brand')
    q = request.GET.get('q', '').strip()
    if vehicle_type:
        qs = qs.filter(vehicle_type=vehicle_type)
    if brand:
        qs = qs.filter(brand__iexact=brand)
    if q:
        qs = qs.filter(brand__icontains=q) | qs.filter(model__icontains=q)
    return Response(VehicleReferenceSerializer(qs[:100], many=True).data)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def reference_detail(request, pk):
    ref = get_object_or_404(VehicleReference, pk=pk)
    if request.method == 'DELETE':
        ref.delete()
        return Response(status=204)
    if request.method == 'PATCH':
        serializer = VehicleReferenceSerializer(ref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        ref = serializer.save()
    return Response(VehicleReferenceSerializer(ref).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reference_schedule(request, pk):
    ref = get_object_or_404(VehicleReference, pk=pk)
    if request.method == 'POST':
        data = request.data.copy()
        data['vehicle_reference'] = ref.id
        serializer = MaintenanceScheduleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save()
        return Response(MaintenanceScheduleSerializer(schedule).data, status=201)
    return Response(MaintenanceScheduleSerializer(ref.schedule.all(), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reference_parts(request, pk):
    ref = get_object_or_404(VehicleReference, pk=pk)
    parts = Part.objects.filter(
        brand__iexact=ref.brand,
        vehicle_type__in=['', ref.vehicle_type],
    )
    return Response(PartSerializer(parts[:50], many=True, context={'request': request}).data)