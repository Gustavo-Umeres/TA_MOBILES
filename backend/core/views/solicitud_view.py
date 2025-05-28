from rest_framework import viewsets, status
from rest_framework.response import Response
from core.models import Solicitud
from core.serializers.solicitud_serializer import SolicitudSerializer
from core.services.solicitud_service import crear_solicitud, actualizar_estado_solicitud

class SolicitudViewSet(viewsets.ViewSet):
    def list(self, request):
        solicitudes = Solicitud.objects.all()
        serializer = SolicitudSerializer(solicitudes, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            solicitud = Solicitud.objects.get(pk=pk)
            serializer = SolicitudSerializer(solicitud)
            return Response(serializer.data)
        except Solicitud.DoesNotExist:
            return Response({"error": "Solicitud no encontrada"}, status=404)

    def create(self, request):
        try:
            data = request.data
            solicitud = crear_solicitud(
                cliente_id=data["cliente_id"],
                categoria_id=data["categoria_id"],
                direccion=data["direccion"]
            )
            serializer = SolicitudSerializer(solicitud)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def update_estado(self, request, pk=None):
        try:
            nuevo_estado = request.data.get("estado")
            solicitud = actualizar_estado_solicitud(pk, nuevo_estado)
            serializer = SolicitudSerializer(solicitud)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
