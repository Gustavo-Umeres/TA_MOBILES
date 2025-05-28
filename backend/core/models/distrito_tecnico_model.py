from django.db import models
from core.models.tecnico_model import Tecnico
from core.models.distrito_model import Distrito

class DistritoTecnico(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    distrito = models.ForeignKey(Distrito, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tecnico', 'distrito')
