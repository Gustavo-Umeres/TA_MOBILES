from rest_framework import serializers
from core.models import FotoSolicitud

class FotoSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoSolicitud
        fields = '__all__'
