from django.db import models
from backend.core.models.usuario_model import Usuario
from core.models.tecnico_model import Tecnico
from core.models.categoria_model import Categoria

class Solicitud(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_cliente')
    tecnico = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    direccion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
