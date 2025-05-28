from rest_framework import serializers
from core.models import Tecnico, Usuario

class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tecnico
        fields = '__all__'
