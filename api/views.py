from django.shortcuts import render

# Create your views here.
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
