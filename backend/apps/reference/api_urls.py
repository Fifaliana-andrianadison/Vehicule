from django.urls import path
from apps.reference import api

app_name = 'reference_api'

urlpatterns = [
    path('vehicles/', api.reference_list, name='list'),
    path('vehicles/<int:pk>/', api.reference_detail, name='detail'),
    path('vehicles/<int:pk>/schedule/', api.reference_schedule, name='schedule'),
    path('vehicles/<int:pk>/parts/', api.reference_parts, name='parts'),
]