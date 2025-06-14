# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    UsuarioViewSet, CategoriaViewSet, TecnicoViewSet, Tecnico_CategoriasViewSet,
    FotoTrabajosViewSet, SolicitudViewSet, FotoSolicitudViewSet,
    DistritosViewSet, DistritosTecnicosViewSet,
    MercadoPagoWebhookView, MercadoPagoFeedbackView # Import new views
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'tecnicos', TecnicoViewSet)
router.register(r'tecnicos-categorias', Tecnico_CategoriasViewSet)
router.register(r'fotos-trabajos', FotoTrabajosViewSet)
router.register(r'solicitudes', SolicitudViewSet)
router.register(r'fotos-solicitud', FotoSolicitudViewSet)
router.register(r'distritos', DistritosViewSet)
router.register(r'distritos-tecnicos', DistritosTecnicosViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', obtain_auth_token, name='api_token_auth'),
    # Mercado Pago specific URLs
    path('mercadopago/webhook/', MercadoPagoWebhookView.as_view(), name='mercadopago-webhook'),
    path('mercadopago/feedback/<str:status_type>/', MercadoPagoFeedbackView.as_view(), name='mercadopago-feedback'),
    
]