from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import mercadopago
from django.conf import settings # Importa settings para acceder a la configuración
from datetime import date, timedelta
import json # Para analizar los datos del webhook
from django.views.decorators.csrf import csrf_exempt # Para webhooks
from django.utils.decorators import method_decorator
from rest_framework.views import APIView # Necesario para MercadoPagoWebhookView

# Importa tus modelos y serializadores
from rest_framework import viewsets
from .models import (
    Usuario, Categoria, Tecnico, Tecnico_Categorias, FotoTrabajos,
    Solicitud, FotoSolicitud, Distritos, DistritosTecnicos
)
from .serializers import (
    UsuarioSerializer, CategoriaSerializer, TecnicoSerializer, Tecnico_CategoriasSerializer,
    FotoTrabajosSerializer, SolicitudSerializer, FotoSolicitudSerializer,
    DistritosSerializer, DistritosTecnicosSerializer
)

# --- Clases de ViewSet existentes ---

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class TecnicoViewSet(viewsets.ModelViewSet):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer

class Tecnico_CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Tecnico_Categorias.objects.all()
    serializer_class = Tecnico_CategoriasSerializer

class FotoTrabajosViewSet(viewsets.ModelViewSet):
    queryset = FotoTrabajos.objects.all()
    serializer_class = FotoTrabajosSerializer

class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer

class FotoSolicitudViewSet(viewsets.ModelViewSet):
    queryset = FotoSolicitud.objects.all()
    serializer_class = FotoSolicitudSerializer

class DistritosViewSet(viewsets.ModelViewSet):
    queryset = Distritos.objects.all()
    serializer_class = DistritosSerializer

class DistritosTecnicosViewSet(viewsets.ModelViewSet):
    queryset = DistritosTecnicos.objects.all()
    serializer_class = DistritosTecnicosSerializer

def get_mercadopago_sdk():
    """
    Inicializa y devuelve el SDK de Mercado Pago.
    Esta función se llama solo cuando el SDK es realmente necesario,
    asegurando que las settings estén completamente cargadas.
    """
    return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    # ... (otras acciones existentes, si las hay)

    @action(detail=True, methods=['post'], url_path='create-subscription-payment')
    def create_subscription_payment(self, request, pk=None):
        """
        Crea una preferencia de pago en Mercado Pago para la suscripción de un técnico.
        El usuario debe ser de tipo 'tecnico'.
        """
        user = self.get_object()
        if user.tipo != 'tecnico':
            return Response({'error': 'Solo los usuarios de tipo técnico pueden crear suscripciones.'}, status=status.HTTP_403_FORBIDDEN)

        # Verifica si el usuario ya es un técnico
        try:
            tecnico_profile = user.tecnico # Accede al objeto Tecnico relacionado
        except Tecnico.DoesNotExist:
            return Response({'error': 'El usuario no tiene un perfil de técnico asociado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificación básica para evitar la re-suscripción si ya está activa
        if tecnico_profile.is_subscription_active(): # Asegúrate de que este método exista en tu modelo Tecnico
            return Response({'message': 'El técnico ya tiene una suscripción activa.'}, status=status.HTTP_200_OK)

        # Define el monto y detalles de la suscripción
        # Puedes obtener esto de settings o de una configuración de base de datos
        subscription_title = "Suscripción Mensual Chambea Ya"
        subscription_price = 10.00 # Precio de ejemplo en tu moneda local (ej. PEN)
        subscription_currency = "PEN" # O "ARS", "BRL", "CLP", "MXN", "UYU" para otros países

        # Define las URLs de retorno para Mercado Pago (ajústalas a los deep links de tu app Flutter o URLs web)
        # Estas URLs serán llamadas después del proceso de pago en el lado de Mercado Pago
        base_url = request.build_absolute_uri('/')[:-1] # Obtiene tu host actual (ej. http://127.0.0.1:8000)
        # Asegúrate de que estas coincidan con el enrutamiento de tu app Flutter o con una página de éxito/fracaso
        back_urls = {
            "success": f"{base_url}/api/mercadopago/feedback/success/", # URL de feedback de ejemplo
            "pending": f"{base_url}/api/mercadopago/feedback/pending/",
            "failure": f"{base_url}/api/mercadopago/feedback/failure/",
        }

        # Crea los datos de preferencia de pago
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
                # "phone": {"area_code": "", "number": user.telefono}, # Opcional
                # "identification": {"type": "DNI", "number": user.dni}, # Opcional, si es necesario para tu país
            },
            "back_urls": back_urls,
            "auto_return": "approved", # Redirige automáticamente a la URL de éxito para pagos aprobados
            "notification_url": f"{base_url}/api/mercadopago/webhook/", # Tu endpoint de webhook
            "external_reference": f"chambea-ya-sub-{user.id}-{date.today().strftime('%Y%m%d')}", # Identificador único para tu sistema
        }

        try:
            sdk = get_mercadopago_sdk() # Inicializa el SDK aquí
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            # Guarda el ID de preferencia en el perfil del técnico para futura referencia
            tecnico_profile.mercadopago_preference_id = preference.get('id')
            tecnico_profile.save()

            return Response({
                'preference_id': preference.get('id'),
                'init_point': preference.get('init_point'), # URL para redirigir al usuario para el pago
                'sandbox_init_point': preference.get('sandbox_init_point'), # URL de Sandbox
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e), 'details': 'Error al crear la preferencia de pago en Mercado Pago.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vista de Webhook para notificaciones de Mercado Pago
@method_decorator(csrf_exempt, name='dispatch') # Deshabilita CSRF para el endpoint de webhook
class MercadoPagoWebhookView(APIView):
    authentication_classes = [] # No se necesita autenticación para webhooks
    permission_classes = [] # No se necesita permiso para webhooks

    def post(self, request, *args, **kwargs):
        data = request.data
        topic = data.get('topic')
        resource_url = data.get('resource') # URL para obtener los detalles del pago

        if topic == 'payment' and resource_url:
            try:
                sdk = get_mercadopago_sdk() # Inicializa el SDK aquí
                # Obtener los detalles del pago de Mercado Pago
                payment_id = resource_url.split('/')[-1]
                payment_info = sdk.payment().get(payment_id)

                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    payment_status = payment.get('status')
                    external_reference = payment.get('external_reference')
                    payer_id = payment.get('payer', {}).get('id')

                    # Analiza external_reference para obtener el ID del técnico
                    # Formato: chambea-ya-sub-{user.id}-{date}
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
                        return Response(status=status.HTTP_200_OK) # Aun así, devuelve OK a Mercado Pago

                    try:
                        tecnico = Tecnico.objects.get(usuario__id=user_id)
                    except Tecnico.DoesNotExist:
                        print(f"Webhook: Técnico con ID de usuario {user_id} no encontrado.")
                        return Response(status=status.HTTP_200_OK)

                    if payment_status == 'approved':
                        # Activar suscripción
                        tecnico.suscripcion_activa = True
                        tecnico.fecha_inicio_suscripcion = date.today()
                        tecnico.fecha_fin_suscripcion = date.today() + timedelta(days=30) # Suscripción de 1 mes
                        tecnico.mercadopago_collector_id = payer_id # Guarda el ID del comprador si lo necesitas
                        tecnico.save()
                        print(f"Webhook: Suscripción aprobada para el técnico {tecnico.usuario.username}")

                    elif payment_status == 'pending':
                        # Manejar el estado pendiente (ej. pago en revisión)
                        print(f"Webhook: Suscripción pendiente para el técnico {tecnico.usuario.username}")
                        tecnico.suscripcion_activa = False # Mantener inactiva hasta que se apruebe
                        tecnico.save()
                        # Opcionalmente, informa al usuario que el pago está pendiente
                    elif payment_status == 'rejected':
                        # Manejar el estado rechazado
                        print(f"Webhook: Suscripción rechazada para el técnico {tecnico.usuario.username}")
                        tecnico.suscripcion_activa = False
                        tecnico.save()
                        # Opcionalmente, informa al usuario que el pago fue rechazado

                return Response(status=status.HTTP_200_OK)

            except Exception as e:
                print(f"Error procesando webhook de Mercado Pago: {e}")
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK) # Siempre devuelve 200 OK a Mercado Pago para temas/recursos no manejados

# Vista de feedback para Mercado Pago
from django.http import HttpResponse

class MercadoPagoFeedbackView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, status_type):
        # Esta vista es alcanzada por Mercado Pago después de que el usuario completa el pago de su lado.
        # Puedes registrar esto o redirigir a un deep link específico de Flutter.
        # Para una aplicación móvil, a menudo redirigirías a la aplicación con parámetros.
        # Ejemplo: chambeaya://payment_success?status=approved
        # Deberías devolver una redirección aquí, o una página HTML simple para la web.
        print(f"Mercado Pago Feedback - Estado: {status_type}, Parámetros de consulta: {request.GET}")
        # En una aplicación real, probablemente redirigirías a una URL específica en tu aplicación Flutter
        # Por ahora, solo una respuesta simple.
        return HttpResponse(f"<html><body><h1>¡Pago {status_type.capitalize()}!</h1><p>Revisa tu aplicación para conocer el estado.</p></body></html>", status=status.HTTP_200_OK)