from rest_framework import viewsets, status
from rest_framework.response import Response
from core.models import Usuario
from core.serializers.usuario_serializer import UsuarioSerializer
from core.services.usuario_service import crear_usuario

class UsuarioViewSet(viewsets.ViewSet):
    def list(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(pk=pk)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

    def create(self, request):
        try:
            usuario = crear_usuario(request.data)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
