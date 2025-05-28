from django.db import models
from backend.core.models.usuario_model import Usuario
from core.models.categoria_model import Categoria

class Tecnico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.usuario)
