from django.db import models
from core.models.tecnico_model import Tecnico
from core.models.categoria_model import Categoria

class TecnicoCategoria(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tecnico', 'categoria')
