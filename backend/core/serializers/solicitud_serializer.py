from rest_framework import serializers
from core.models import Solicitud

class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = '__all__'
