from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets 
from rest_framework import permissions
import mercadopago
from django.conf import settings
from datetime import date, timedelta
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.http import HttpResponse # Import HttpResponse for MercadoPagoFeedbackView

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from .models import (
    Usuario, Categoria, Tecnico, Tecnico_Categorias, FotoTrabajos,
    Solicitud, FotoSolicitud, Distritos, DistritosTecnicos
)
from .serializers import (
    UsuarioSerializer, CategoriaSerializer, TecnicoSerializer, Tecnico_CategoriasSerializer,
    FotoTrabajosSerializer, SolicitudSerializer, FotoSolicitudSerializer,
    DistritosSerializer, DistritosTecnicosSerializer,
    UserProfileSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self): 
        # Esta lógica se mantiene como la tenías, ya que la definiste explícitamente.
        if self.action == 'create':
            self.permission_classes = [permissions.AllowAny] 
        else:
            self.permission_classes = [permissions.IsAuthenticated] 
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) 

        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Usuario registrado exitosamente.",
                "id": user.id,
                "username": user.username,
                "correo": user.correo,
                "token": token.key
            },
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data)
        )

    @action(detail=True, methods=['post'], url_path='create-subscription-payment')
    def create_subscription_payment(self, request, pk=None):
        user = self.get_object()
        if user.tipo != 'tecnico':
            return Response({'error': 'Solo los usuarios de tipo técnico pueden crear suscripciones.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            tecnico_profile = user.tecnico
        except Tecnico.DoesNotExist:
            return Response({'error': 'El usuario no tiene un perfil de técnico asociado.'}, status=status.HTTP_400_BAD_REQUEST)

        if tecnico_profile.is_subscription_active():
            return Response({'message': 'El técnico ya tiene una suscripción activa.'}, status=status.HTTP_200_OK)

        subscription_title = "Suscripción Mensual Chambea Ya"
        subscription_price = 10.00
        subscription_currency = "PEN"

        base_url = request.build_absolute_uri('/')[:-1]
        back_urls = {
            "success": f"{base_url}/api/mercadopago/feedback/success/",
            "pending": f"{base_url}/api/mercadopago/feedback/pending/",
            "failure": f"{base_url}/api/mercadopago/feedback/failure/",
        }

        preference_data = {
            "items": [
                {
                    "title": subscription_title,
                    "quantity": 1,
                    "unit_price": float(subscription_price),
                    "currency_id": subscription_currency,
                    "description": f"Suscripción mensual para {user.username}",
                }
            ],
            "payer": {
                "name": user.first_name,
                "surname": user.last_name,
                "email": user.correo,
            },
            "back_urls": back_urls,
            "auto_return": "approved",
            "notification_url": f"{base_url}/api/mercadopago/webhook/",
            "external_reference": f"chambea-ya-sub-{user.id}-{date.today().strftime('%Y%m%d')}",
        }

        try:
            sdk = get_mercadopago_sdk()
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            tecnico_profile.mercadopago_preference_id = preference.get('id')
            tecnico_profile.save()

            return Response({
                'preference_id': preference.get('id'),
                'init_point': preference.get('init_point'),
                'sandbox_init_point': preference.get('sandbox_init_point'),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e), 'details': 'Error al crear la preferencia de pago en Mercado Pago.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # permission_classes = [] 

class TecnicoViewSet(viewsets.ModelViewSet):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer
    # permission_classes = [] 

class Tecnico_CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Tecnico_Categorias.objects.all()
    serializer_class = Tecnico_CategoriasSerializer
    # permission_classes = [] 

class FotoTrabajosViewSet(viewsets.ModelViewSet):
    queryset = FotoTrabajos.objects.all()
    serializer_class = FotoTrabajosSerializer
    # permission_classes = [] 

class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    # permission_classes = [] 

class FotoSolicitudViewSet(viewsets.ModelViewSet):
    queryset = FotoSolicitud.objects.all()
    serializer_class = FotoSolicitudSerializer
    # permission_classes = [] 

class DistritosViewSet(viewsets.ModelViewSet):
    queryset = Distritos.objects.all()
    serializer_class = DistritosSerializer
    # permission_classes = [] 

class DistritosTecnicosViewSet(viewsets.ModelViewSet):
    queryset = DistritosTecnicos.objects.all()
    serializer_class = DistritosTecnicosSerializer
    # permission_classes = [] 

def get_mercadopago_sdk():
    """
    Inicializa y devuelve el SDK de Mercado Pago.
    Esta función se llama solo cuando el SDK es realmente necesario,
    asegurando que las settings estén completamente cargadas.
    """
    return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

@method_decorator(csrf_exempt, name='dispatch')
class MercadoPagoWebhookView(APIView):
    authentication_classes = []
    # permission_classes = [] 

    def post(self, request, *args, **kwargs):
        data = request.data
        topic = data.get('topic')
        resource_url = data.get('resource')

        if topic == 'payment' and resource_url:
            try:
                sdk = get_mercadopago_sdk()
                payment_id = resource_url.split('/')[-1]
                payment_info = sdk.payment().get(payment_id)

                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    payment_status = payment.get('status')
                    external_reference = payment.get('external_reference')
                    payer_id = payment.get('payer', {}).get('id')

                    try:
                        parts = external_reference.split('-')
                        if len(parts) >= 4 and parts[0] == 'chambea' and parts[1] == 'ya' and parts[2] == 'sub':
                            user_id = int(parts[3])
                        else:
                            user_id = None
                    except (ValueError, IndexError):
                        user_id = None

                    if not user_id:
                        print(f"Webhook: No se pudo analizar el ID de usuario de external_reference: {external_reference}")
                        return Response(status=status.HTTP_200_OK)

                    try:
                        tecnico = Tecnico.objects.get(usuario__id=user_id)
                    except Tecnico.DoesNotExist:
                        print(f"Webhook: Técnico con ID de usuario {user_id} no encontrado.")
                        return Response(status=status.HTTP_200_OK)

                    if payment_status == 'approved':
                        tecnico.suscripcion_activa = True
                        tecnico.fecha_inicio_suscripcion = date.today()
                        tecnico.fecha_fin_suscripcion = date.today() + timedelta(days=30)
                        tecnico.mercadopago_collector_id = payer_id
                        tecnico.save()
                        print(f"Webhook: Suscripción aprobada para el técnico {tecnico.usuario.username}")

                    elif payment_status == 'pending':
                        print(f"Webhook: Suscripción pendiente para el técnico {tecnico.usuario.username}")
                        tecnico.suscripcion_activa = False
                        tecnico.save()
                    elif payment_status == 'rejected':
                        print(f"Webhook: Suscripción rechazada para el técnico {tecnico.usuario.username}")
                        tecnico.suscripcion_activa = False
                        tecnico.save()

                return Response(status=status.HTTP_200_OK)

            except Exception as e:
                print(f"Error procesando webhook de Mercado Pago: {e}")
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)

class MercadoPagoFeedbackView(APIView):
    authentication_classes = []
    # permission_classes = [] 

    def get(self, request, status_type):
        print(f"Mercado Pago Feedback - Estado: {status_type}, Parámetros de consulta: {request.GET}")
        # Make sure HttpResponse is imported for this line
        return HttpResponse(f"<html><body><h1>¡Pago {status_type.capitalize()}!</h1><p>Revisa tu aplicación para conocer el estado.</p></body></html>", status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    authentication_classes = [TokenAuthentication]
    # permission_classes = [] 

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)