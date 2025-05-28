from rest_framework import viewsets, status
from rest_framework.response import Response
from core.models import Tecnico
from core.serializers.tecnico_serializer import TecnicoSerializer
from core.services.tecnico_service import obtener_tecnicos_por_categoria

class TecnicoViewSet(viewsets.ViewSet):
    def list(self, request):
        tecnicos = Tecnico.objects.all()
        serializer = TecnicoSerializer(tecnicos, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            tecnico = Tecnico.objects.get(pk=pk)
            serializer = TecnicoSerializer(tecnico)
            return Response(serializer.data)
        except Tecnico.DoesNotExist:
            return Response({"error": "Técnico no encontrado"}, status=404)

    def get_by_categoria(self, request, categoria_id=None):
        tecnicos = obtener_tecnicos_por_categoria(categoria_id)
        serializer = TecnicoSerializer(tecnicos, many=True)
        return Response(serializer.data)
