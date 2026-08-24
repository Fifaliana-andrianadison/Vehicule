from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.parts.models import Part, PartCategory, PartCompatibility
from apps.vehicles.models import Vehicle


class PartCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartCategory
        fields = ['id', 'name', 'description']


class PartSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    compatible = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = [
            'id', 'name', 'category', 'category_name', 'reference', 'brand',
            'vehicle_type', 'description', 'price', 'compatible', 'created_at',
        ]
        read_only_fields = ['compatible', 'created_at']

    def get_compatible(self, obj):
        request = self.context.get('request')
        vehicle_id = request.GET.get('vehicle') if request else None
        if not vehicle_id:
            return None
        vehicle = Vehicle.objects.filter(pk=vehicle_id, user=request.user).first()
        if not vehicle:
            return None
        return obj.is_compatible_with(vehicle)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def part_list(request):
    if request.method == 'POST':
        data = request.data.copy()
        serializer = PartSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        part = serializer.save()
        return Response(PartSerializer(part, context={'request': request}).data, status=201)

    qs = Part.objects.select_related('category').all()
    vehicle_id = request.GET.get('vehicle')
    category = request.GET.get('category')
    q = request.GET.get('q', '').strip()
    if vehicle_id:
        vehicle = Vehicle.objects.filter(pk=vehicle_id, user=request.user).first()
        if vehicle:
            ids = [p.id for p in qs if p.is_compatible_with(vehicle)]
            qs = Part.objects.filter(pk__in=ids)
    if category:
        qs = qs.filter(category_id=category)
    if q:
        qs = qs.filter(name__icontains=q)
    return Response(PartSerializer(qs[:100], many=True, context={'request': request}).data)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def part_detail(request, pk):
    part = Part.objects.get(pk=pk)
    if request.method == 'DELETE':
        part.delete()
        return Response(status=204)
    if request.method == 'PATCH':
        serializer = PartSerializer(part, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        part = serializer.save()
    return Response(PartSerializer(part, context={'request': request}).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def part_categories(request):
    if request.method == 'POST':
        serializer = PartCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(PartCategorySerializer(PartCategory.objects.all(), many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_compatibility(request, pk):
    part = Part.objects.get(pk=pk)
    vehicle_id = request.data.get('vehicle')
    vehicle = Vehicle.objects.filter(pk=vehicle_id, user=request.user).first()
    if not vehicle:
        return Response({'error': 'Véhicule introuvable'}, status=404)
    compat, created = PartCompatibility.objects.get_or_create(part=part, vehicle=vehicle)
    return Response({'created': created}, status=201 if created else 200)