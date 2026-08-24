from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts import api

app_name = 'accounts_api'

urlpatterns = [
    path('register/', api.register, name='register'),
    path('login/', api.LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
]