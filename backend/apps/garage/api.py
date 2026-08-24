from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.garage.models import Garage, GarageStaff, RepairOrder, RepairOrderPart
from apps.vehicles.models import Vehicle
from apps.expenses.models import Expense, ExpenseCategory


class GarageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garage
        fields = ['id', 'name', 'address', 'phone', 'email', 'siret', 'created_at']


class RepairOrderPartSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)

    class Meta:
        model = RepairOrderPart
        fields = ['id', 'part', 'part_name', 'name', 'quantity', 'unit_price', 'total']
        read_only_fields = ['total']


class RepairOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vehicle_label = serializers.CharField(source='vehicle.__str__', read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    parts = RepairOrderPartSerializer(many=True, read_only=True)
    parts_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = RepairOrder
        fields = [
            'id', 'garage', 'vehicle', 'vehicle_label', 'customer',
            'customer_name', 'title', 'description', 'status', 'status_display',
            'estimated_cost', 'total_cost', 'parts', 'parts_total',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['garage', 'customer', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['garage'] = self.context['garage']
        validated_data['customer'] = self.context['request'].user
        parts_data = self.context['request'].data.get('parts', [])
        order = RepairOrder.objects.create(**validated_data)
        for part in parts_data:
            RepairOrderPart.objects.create(
                repair_order=order,
                part_id=part.get('part'),
                name=part.get('name', ''),
                quantity=part.get('quantity', 1),
                unit_price=part.get('unit_price', 0),
            )
        return order


def get_user_garage(user):
    return getattr(user, 'garage', None)


def is_garage_staff(user, garage):
    return GarageStaff.objects.filter(garage=garage, user=user, is_active=True).exists()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def repair_orders(request):
    garage = get_user_garage(request.user)
    if request.method == 'POST':
        if not garage:
            return Response({'error': 'Un compte garage est requis (profil pro)'}, status=403)
        serializer = RepairOrderSerializer(data=request.data, context={'garage': garage, 'request': request})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order = serializer.save()
            if order.status == RepairOrder.Status.INVOICED and order.total_cost:
                cat, _ = ExpenseCategory.objects.get_or_create(name='Garage')
                Expense.objects.create(
                    vehicle=order.vehicle, category=cat,
                    amount=order.total_cost, date=date.today(),
                    description=f"Facture garage : {order.title}",
                    repair_order=order,
                )
        return Response(RepairOrderSerializer(order).data, status=status.HTTP_201_CREATED)

    qs = RepairOrder.objects.select_related('vehicle', 'customer', 'garage')
    if garage:
        qs = qs.filter(garage=garage)
    else:
        qs = qs.filter(customer=request.user)
    s = request.GET.get('status')
    if s:
        qs = qs.filter(status=s)
    return Response(RepairOrderSerializer(qs, many=True).data)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def repair_order_detail(request, pk):
    garage = get_user_garage(request.user)
    order = get_object_or_404(RepairOrder, pk=pk)
    if not (garage and order.garage == garage) and order.customer != request.user:
        return Response({'error': 'Non autorisé'}, status=403)

    if request.method == 'PATCH':
        if not (garage and order.garage == garage):
            return Response({'error': 'Seul le garage peut modifier'}, status=403)
        serializer = RepairOrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order = serializer.save()
            parts = request.data.get('parts')
            if parts is not None:
                order.parts.all().delete()
                for part in parts:
                    RepairOrderPart.objects.create(
                        repair_order=order,
                        part_id=part.get('part'),
                        name=part.get('name', ''),
                        quantity=part.get('quantity', 1),
                        unit_price=part.get('unit_price', 0),
                    )
            if order.status == RepairOrder.Status.INVOICED and order.total_cost and not hasattr(order, 'expense'):
                cat, _ = ExpenseCategory.objects.get_or_create(name='Garage')
                Expense.objects.create(
                    vehicle=order.vehicle, category=cat,
                    amount=order.total_cost, date=date.today(),
                    description=f"Facture garage : {order.title}",
                    repair_order=order,
                )
        return Response(RepairOrderSerializer(order).data)
    return Response(RepairOrderSerializer(order).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def garage_dashboard(request):
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'Compte garage requis'}, status=403)

    orders = garage.repair_orders.all()
    today = date.today()

    invoiced = orders.filter(status=RepairOrder.Status.INVOICED)
    month_orders = orders.filter(created_at__year=today.year, created_at__month=today.month)
    month_invoiced = invoiced.filter(created_at__year=today.year, created_at__month=today.month)

    revenue_month = month_invoiced.aggregate(t=Sum('total_cost'))['t'] or Decimal('0')
    unpaid = invoiced.filter(total_cost__isnull=False)
    unpaid_total = sum(
        (o.total_cost - (o.expense.amount if hasattr(o, 'expense') and o.expense else 0))
        for o in unpaid
    ) or Decimal('0')

    avg_ticket = Decimal('0')
    if month_invoiced.count():
        avg_ticket = revenue_month / month_invoiced.count()

    by_status = {s.value: orders.filter(status=s.value).count() for s in RepairOrder.Status}

    return Response({
        'garage': GarageSerializer(garage).data,
        'orders_total': orders.count(),
        'orders_month': month_orders.count(),
        'revenue_month': float(revenue_month),
        'unpaid_total': float(unpaid_total),
        'avg_ticket': float(avg_ticket),
        'by_status': by_status,
        'recent_orders': RepairOrderSerializer(orders[:5], many=True).data,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def garage_me(request):
    garage = get_user_garage(request.user)
    if request.method == 'POST':
        serializer = GarageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        garage = serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if not garage:
        return Response({'garage': None})
    return Response({'garage': GarageSerializer(garage).data})