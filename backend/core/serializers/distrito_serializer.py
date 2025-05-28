from rest_framework import serializers
from core.models import Distrito

class DistritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distrito
        fields = '__all__'
