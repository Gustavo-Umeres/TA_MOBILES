# api/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator # Para validaciones de campos únicos combinados
from .models import (
    Usuario, Categoria, Tecnico, Tecnico_Categorias, FotoTrabajos,
    Solicitud, FotoSolicitud, Distritos, DistritosTecnicos
)

## Serializadores Base y de Relaciones Estos serializadores son para los modelos más simples o para ser usados como anidados de solo lectura.

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre'] # Explícita los campos para mayor control

class DistritosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distritos
        fields = ['id', 'nombre'] # Explícita los campos

class FotoTrabajosSerializer(serializers.ModelSerializer):
    # En caso de que necesites subir archivos directamente, el campo se manejará automáticamente
    # por CloudinaryField en el modelo. Aquí solo mostramos la URL.
    class Meta:
        model = FotoTrabajos
        fields = ['id', 'tecnico', 'categoria', 'url_foto', 'subido_en']
        read_only_fields = ['subido_en'] # Se establece automáticamente al crear

class FotoSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoSolicitud
        fields = ['id', 'solicitud', 'url_foto', 'subido_en']
        read_only_fields = ['subido_en']

class Tecnico_CategoriasSerializer(serializers.ModelSerializer):
    # Opcional: mostrar el nombre de la categoría y el nombre del técnico
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
    # 'password' es solo de escritura para no exponerla en las respuestas GET
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    # Campo para confirmar contraseña al crear
    password_confirm = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'dni', 'correo',
            'telefono', 'tipo', 'estado', 'creado_en', 'password', 'password_confirm'
        ]
        read_only_fields = ['creado_en', 'estado'] # 'estado' debería ser manejado por lógica de negocio o admin
        extra_kwargs = {
            'username': {'required': True}, # Aseguramos que username sea requerido
            'first_name': {'required': True},
            'last_name': {'required': True},
            'dni': {'required': True},
            'correo': {'required': True},
            'tipo': {'required': True}
        }

    def validate(self, data):
        # Validación para la creación de usuario
        if self.instance is None: # Solo aplica en la creación (POST)
            password = data.get('password')
            password_confirm = data.get('password_confirm')

            if password != password_confirm:
                raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
            if not password:
                raise serializers.ValidationError({"password": "La contraseña es requerida."})
            if len(password) < 8: # Mínimo de 8 caracteres, puedes agregar más reglas de complejidad
                raise serializers.ValidationError({"password": "La contraseña debe tener al menos 8 caracteres."})

        # Remueve password_confirm para que no se intente guardar en el modelo
        data.pop('password_confirm', None)
        return data

    def create(self, validated_data):
        password = validated_data.pop('password') # Ya validamos que existe y coincida
        user = Usuario.objects.create(**validated_data)
        user.set_password(password) # Hashea la contraseña
        user.save()
        return user

    def update(self, instance, validated_data):
        # Maneja la actualización de la contraseña si se proporciona
        password = validated_data.pop('password', None)
        if password is not None:
            # Validar que la nueva contraseña no esté vacía si se intenta cambiar
            if not password:
                raise serializers.ValidationError({"password": "La nueva contraseña no puede estar vacía."})
            instance.set_password(password)

        # Actualiza el resto de los campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class TecnicoSerializer(serializers.ModelSerializer):
    # Para mostrar los detalles del usuario al leer
    usuario = UsuarioSerializer(read_only=True)
    # Para la creación, espera el ID del usuario ya existente y validado
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(tipo='tecnico'), # Asegura que solo se asocie a usuarios de tipo técnico
        write_only=True, # Campo solo para escritura
        source='usuario', # Mapea a la relación 'usuario' en el modelo Tecnico
        required=True
    )

    # Serializadores anidados para lectura
    categorias = CategoriaSerializer(many=True, read_only=True)
    distritos = DistritosSerializer(many=True, read_only=True)
    fotos_trabajos = FotoTrabajosSerializer(many=True, read_only=True)

    class Meta:
        model = Tecnico
        fields = [
            'usuario', 'usuario_id', 'calificacion', 'fecha_vencimiento',
            'categorias', 'distritos', 'fotos_trabajos'
        ]
        read_only_fields = ['calificacion'] # La calificación se calculará, no se establecerá directamente

    def create(self, validated_data):
        # Al crear un Técnico, esperamos que el usuario_id ya venga en validated_data
        # y que sea un Usuario con tipo='tecnico'
        return Tecnico.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # No se espera que el usuario_id cambie en una actualización de Técnico
        validated_data.pop('usuario_id', None) # Eliminar si se envía para evitar errores

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class SolicitudSerializer(serializers.ModelSerializer):
    # Serializadores anidados para lectura
    cliente = UsuarioSerializer(read_only=True)
    tecnico = TecnicoSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    fotos_solicitud = FotoSolicitudSerializer(many=True, read_only=True)

    # Campos para escritura (IDs)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(tipo='cliente'),
        write_only=True,
        source='cliente',
        required=True
    )
    tecnico_id = serializers.PrimaryKeyRelatedField(
        queryset=Tecnico.objects.all(), # Puede ser null
        write_only=True,
        source='tecnico',
        required=False, # Puede ser nulo al crear (pendiente de asignación)
        allow_null=True # Permite que el valor sea null si no se proporciona
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
            'direccion', 'estado', 'calificacion', 'creado_en', 'actualizado_en', 'fotos_solicitud'
        ]
        read_only_fields = ['creado_en', 'actualizado_en', 'calificacion'] # Calificación se asigna después

    def validate_estado(self, value):
        # Puedes añadir lógica de validación para el cambio de estados aquí.
        # Por ejemplo, una solicitud cancelada no puede ser aceptada.
        # Esto requiere self.instance para obtener el estado actual
        if self.instance and self.instance.estado == 'cancelado' and value != 'cancelado':
            raise serializers.ValidationError("Una solicitud cancelada no puede cambiar a otro estado.")
        return value

    def create(self, validated_data):
        # Los campos con source ya mapean automáticamente a la relación
        return Solicitud.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Previene que cliente_id o categoria_id sean actualizados después de la creación
        validated_data.pop('cliente_id', None)
        validated_data.pop('categoria_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MercadoPagoPreferenceSerializer(serializers.Serializer):
    # This serializer is for validating the data coming from the frontend
    # It doesn't map directly to a model
    return_url_success = serializers.URLField(required=False)
    return_url_pending = serializers.URLField(required=False)
    return_url_failure = serializers.URLField(required=False)

    # You might want to include amount or other details if not fixed
    # For a fixed subscription, these can be hardcoded in the view