from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Vehicle
from .serializers import VehicleSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_search(request):
    q = request.GET.get('q', '').strip()
    vehicles = Vehicle.objects.all()

    if q:
        words = q.split()
        query = Q()
        for word in words:
            query |= Q(brand__icontains=word)
            query |= Q(model__icontains=word)
            query |= Q(name__icontains=word)
        vehicles = vehicles.filter(query)

    vehicles = vehicles.distinct().order_by('brand', 'model')[:20]
    serializer = VehicleSerializer(vehicles, many=True)
    return Response(serializer.data)
