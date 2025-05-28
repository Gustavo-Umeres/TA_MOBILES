from django.urls import path, include

urlpatterns = [
    path('api/', include('core.urls.usuario_urls')),
    path('api/', include('core.urls.tecnico_urls')),
    path('api/', include('core.urls.solicitud_urls')),
]
