from core.models import Usuario
from django.core.exceptions import ValidationError
from django.db import IntegrityError

def crear_usuario(data):
    try:
        usuario = Usuario.objects.create(**data)
        return usuario
    except IntegrityError as e:
        raise ValidationError("Usuario duplicado o datos inválidos.")
