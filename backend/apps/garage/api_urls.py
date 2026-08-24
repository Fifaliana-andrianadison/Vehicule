from django.urls import path
from apps.garage import api

app_name = 'garage_api'

urlpatterns = [
    path('me/', api.garage_me, name='me'),
    path('repair-orders/', api.repair_orders, name='repair_orders'),
    path('repair-orders/<int:pk>/', api.repair_order_detail, name='repair_order_detail'),
    path('dashboard/', api.garage_dashboard, name='dashboard'),
]