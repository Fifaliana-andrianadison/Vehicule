from django.urls import path
from . import views

app_name = 'diagnostics'

urlpatterns = [
    path('<int:vehicle_pk>/', views.diagnostic_view, name='report'),
    path('<int:vehicle_pk>/historique/', views.diagnostic_history, name='history'),
]
