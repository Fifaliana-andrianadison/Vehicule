from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('rappels/', views.reminder_list, name='reminders'),
    path('historique/', views.notification_history, name='history'),
]
