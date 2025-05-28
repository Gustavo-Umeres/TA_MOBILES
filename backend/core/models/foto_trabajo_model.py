from django.db import models
from core.models.tecnico_model import Tecnico
from core.models.categoria_model import Categoria

class FotoTrabajo(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    url_foto = models.TextField()
    subido_en = models.DateTimeField(auto_now_add=True)
