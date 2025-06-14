from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import (
    Usuario, Categoria, Tecnico, Tecnico_Categorias, FotoTrabajos,
    Solicitud, FotoSolicitud, Distritos, DistritosTecnicos
)
from django.contrib.auth import get_user_model

User = get_user_model()

## Serializadores Base y de Relaciones
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class DistritosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distritos
        fields = ['id', 'nombre']

class FotoTrabajosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoTrabajos
        fields = ['id', 'tecnico', 'categoria', 'url_foto', 'subido_en']
        read_only_fields = ['subido_en']

class FotoSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoSolicitud
        fields = ['id', 'solicitud', 'url_foto', 'subido_en']
        read_only_fields = ['subido_en']

class Tecnico_CategoriasSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    tecnico_username = serializers.CharField(source='tecnico.usuario.username', read_only=True)

    class Meta:
        model = Tecnico_Categorias
        fields = ['tecnico', 'categoria', 'categoria_nombre', 'tecnico_username']
        validators = [
            UniqueTogetherValidator(
                queryset=Tecnico_Categorias.objects.all(),
                fields=['tecnico', 'categoria'],
                message="Este técnico ya está asociado a esta categoría."
            )
        ]

class DistritosTecnicosSerializer(serializers.ModelSerializer):
    distrito_nombre = serializers.CharField(source='distrito.nombre', read_only=True)
    tecnico_username = serializers.CharField(source='tecnico.usuario.username', read_only=True)

    class Meta:
        model = DistritosTecnicos
        fields = ['tecnico', 'distrito', 'distrito_nombre', 'tecnico_username']
        validators = [
            UniqueTogetherValidator(
                queryset=DistritosTecnicos.objects.all(),
                fields=['tecnico', 'distrito'],
                message="Este técnico ya está asociado a este distrito."
            )
        ]

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True ,required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True ,required=False, style={'input_type': 'password'})
    # id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'dni', 'correo',
            'telefono', 'tipo', 'estado', 'creado_en', 'password', 'password_confirm'
        ]
        read_only_fields = ['creado_en', 'estado']
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'dni': {'required': True},
            'correo': {'required': True},
            'tipo': {'required': True}
        }

    def validate(self, data):
        if self.instance is None:
            password = data.get('password')
            password_confirm = data.get('password_confirm')

            if password != password_confirm:
                raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
            if not password:
                raise serializers.ValidationError({"password": "La contraseña es requerida."})
            if len(password) < 8:
                raise serializers.ValidationError({"password": "La contraseña debe tener al menos 8 caracteres."})

        data.pop('password_confirm', None)
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            if not password:
                raise serializers.ValidationError({"password": "La nueva contraseña no puede estar vacía."})
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'correo', 'first_name', 'last_name', 
            'dni', 'telefono', 'tipo', 'estado', 'creado_en',
            'is_staff', 'is_superuser'
        )
        read_only_fields = fields

class TecnicoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(tipo='tecnico'),
        write_only=True,
        source='usuario',
        required=True
    )

    categorias = CategoriaSerializer(many=True, read_only=True)
    distritos = DistritosSerializer(many=True, read_only=True)
    fotos_trabajos = FotoTrabajosSerializer(many=True, read_only=True)

    class Meta:
        model = Tecnico
        fields = [
            'usuario', 'usuario_id', 'calificacion', 'fecha_vencimiento',
            'suscripcion_activa', 'fecha_inicio_suscripcion', 'fecha_fin_suscripcion',
            'mercadopago_preference_id', 'mercadopago_collector_id',
            'foto_perfil', 'descripcion', # <--- Added new fields here
            'categorias', 'distritos', 'fotos_trabajos'
        ]
        read_only_fields = ['calificacion', 'suscripcion_activa', 'fecha_inicio_suscripcion', 'fecha_fin_suscripcion', 'mercadopago_preference_id', 'mercadopago_collector_id']

    def create(self, validated_data):
        return Tecnico.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('usuario_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class SolicitudSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    tecnico = TecnicoSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    fotos_solicitud = FotoSolicitudSerializer(many=True, read_only=True)

    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(tipo='cliente'),
        write_only=True,
        source='cliente',
        required=True
    )
    tecnico_id = serializers.PrimaryKeyRelatedField(
        queryset=Tecnico.objects.all(),
        write_only=True,
        source='tecnico',
        required=False,
        allow_null=True
    )
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        write_only=True,
        source='categoria',
        required=True
    )

    class Meta:
        model = Solicitud
        fields = [
            'id', 'cliente', 'cliente_id', 'tecnico', 'tecnico_id', 'categoria', 'categoria_id',
            'direccion', 'titulo', 'descripcion', 'estado', 'calificacion', 'creado_en', 'actualizado_en', 'fotos_solicitud' # <--- Added new fields here
        ]
        read_only_fields = ['creado_en', 'actualizado_en', 'calificacion']

    def validate_estado(self, value):
        if self.instance and self.instance.estado == 'cancelado' and value != 'cancelado':
            raise serializers.ValidationError("Una solicitud cancelada no puede cambiar a otro estado.")
        return value

    def create(self, validated_data):
        return Solicitud.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('cliente_id', None)
        validated_data.pop('categoria_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class MercadoPagoPreferenceSerializer(serializers.Serializer):
    return_url_success = serializers.URLField(required=False)
    return_url_pending = serializers.URLField(required=False)
    return_url_failure = serializers.URLField(required=False)