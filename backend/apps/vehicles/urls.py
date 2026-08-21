from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.vehicle_list, name='list'),
    path('selectionner/', views.vehicle_select, name='select'),
    path('ajouter/', views.vehicle_create, name='create'),
    path('<int:pk>/', views.vehicle_detail, name='detail'),
    path('<int:pk>/modifier/', views.vehicle_update, name='update'),
    path('<int:pk>/supprimer/', views.vehicle_delete, name='delete'),
]
