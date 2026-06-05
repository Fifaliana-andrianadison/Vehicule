from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.maintenance_list, name='list'),
    path('ajouter/', views.maintenance_create, name='create'),
    path('<int:pk>/modifier/', views.maintenance_update, name='update'),
    path('<int:pk>/supprimer/', views.maintenance_delete, name='delete'),
    path('vehicule/<int:vehicle_pk>/', views.maintenance_by_vehicle, name='by_vehicle'),
]
