from django.db import models

class Usuario(models.Model):
    TIPO_USUARIO = [
        ('cliente', 'Cliente'),
        ('tecnico', 'Técnico'),
        ('administrador', 'Administrador'),
    ]

    ESTADO_USUARIO = [
        ('activo', 'Activo'),
        ('desactivado', 'Desactivado'),
    ]

    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    usuario = models.CharField(max_length=150, unique=True)
    contraseña = models.CharField(max_length=255)
    dni = models.CharField(max_length=8, unique=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO)
    estado = models.CharField(max_length=20, choices=ESTADO_USUARIO)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'
