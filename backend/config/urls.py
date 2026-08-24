from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('comptes/', include('apps.accounts.urls')),
    path('vehicules/', include('apps.vehicles.urls')),
    path('entretien/', include('apps.maintenance.urls')),
    path('documents/', include('apps.documents.urls')),
    path('diagnostic/', include('apps.diagnostics.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('api/auth/', include('apps.accounts.api_urls')),
    path('api/', include('apps.vehicles.api_urls')),
    path('api/parts/', include('apps.parts.api_urls')),
    path('api/reference/', include('apps.reference.api_urls')),
    path('api/garage/', include('apps.garage.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
