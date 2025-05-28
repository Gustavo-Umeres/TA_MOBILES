from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.serializers.user_serializer import UsuarioSerializer
from core.services import user_service

class UsuarioListView(APIView):
    def get(self, request):
        usuarios = user_service.listar_usuarios()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
