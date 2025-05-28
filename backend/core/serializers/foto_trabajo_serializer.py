from rest_framework import serializers
from core.models import FotoTrabajo

class FotoTrabajoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoTrabajo
        fields = '__all__'
