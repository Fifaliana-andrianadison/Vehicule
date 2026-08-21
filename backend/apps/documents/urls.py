from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_list, name='list'),
    path('assurance/ajouter/', views.insurance_create, name='insurance_create'),
    path('assurance/<int:pk>/modifier/', views.insurance_update, name='insurance_update'),
    path('assurance/<int:pk>/supprimer/', views.insurance_delete, name='insurance_delete'),
    path('carte-grise/ajouter/', views.carte_grise_create, name='carte_grise_create'),
    path('carte-grise/<int:pk>/modifier/', views.carte_grise_update, name='carte_grise_update'),
    path('carte-grise/<int:pk>/supprimer/', views.carte_grise_delete, name='carte_grise_delete'),
    path('controle-technique/ajouter/', views.inspection_create, name='inspection_create'),
    path('controle-technique/<int:pk>/modifier/', views.inspection_update, name='inspection_update'),
    path('controle-technique/<int:pk>/supprimer/', views.inspection_delete, name='inspection_delete'),
]
