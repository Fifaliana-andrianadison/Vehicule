from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('comptes/', include('accounts.urls')),
    path('vehicules/', include('vehicles.urls')),
    path('api/', include('vehicles.api_urls')),
    path('entretien/', include('maintenance.urls')),
    path('documents/', include('documents.urls')),
    path('diagnostic/', include('diagnostics.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
