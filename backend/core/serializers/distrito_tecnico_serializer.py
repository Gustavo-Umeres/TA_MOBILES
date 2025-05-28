from rest_framework import serializers
from core.models import DistritoTecnico

class DistritoTecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistritoTecnico
        fields = '__all__'
