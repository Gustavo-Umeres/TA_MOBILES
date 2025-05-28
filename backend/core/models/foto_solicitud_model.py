from django.db import models
from core.models.solicitud_model import Solicitud

class FotoSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    url_foto = models.TextField()
    subido_en = models.DateTimeField(auto_now_add=True)
