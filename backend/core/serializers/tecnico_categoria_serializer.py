from rest_framework import serializers
from core.models import TecnicoCategoria

class TecnicoCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TecnicoCategoria
        fields = '__all__'
