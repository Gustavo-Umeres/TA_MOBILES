# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

class Usuario(AbstractUser):
    # Django's AbstractUser already includes username, first_name, last_name, email, password
    # We'll add custom fields from your schema
    tipo_choices = (
        ('cliente', 'Cliente'),
        ('tecnico', 'Técnico'),
        ('administrador', 'Administrador'),
    )
    estado_choices = (
        ('activo', 'Activo'),
        ('desactivado', 'Desactivado'),
    )

    dni = models.CharField(max_length=8, unique=True, null=True, blank=True)
    correo = models.EmailField(unique=True) # Overrides AbstractUser's email to ensure unique
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, default='cliente')
    estado = models.CharField(max_length=20, choices=estado_choices, default='activo')
    creado_en = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'dni', 'tipo','correo'] # Fields required when creating a superuser

    def __str__(self):
        return self.username

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, null=False, blank=False)

    def __str__(self):
        return self.nombre

class Tecnico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, limit_choices_to={'tipo': 'tecnico'})
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    fecha_vencimiento = models.DateField(null=True, blank=True) # This was already here, good for expiration
    
    # New fields for subscription management
    suscripcion_activa = models.BooleanField(default=False)
    fecha_inicio_suscripcion = models.DateField(null=True, blank=True)
    fecha_fin_suscripcion = models.DateField(null=True, blank=True)
    mercadopago_preference_id = models.CharField(max_length=255, blank=True, null=True,
                                                help_text="ID de la preferencia de pago de Mercado Pago")
    mercadopago_collector_id = models.CharField(max_length=255, blank=True, null=True,
                                                help_text="ID del pagador en Mercado Pago")

    categorias = models.ManyToManyField(Categoria, through='Tecnico_Categorias')
    distritos = models.ManyToManyField('Distritos', through='DistritosTecnicos')

    def __str__(self):
        return f"Técnico: {self.usuario.username}"

    # Add a method to easily check subscription status
    def is_subscription_active(self):
        from datetime import date
        return self.suscripcion_activa and self.fecha_fin_suscripcion and self.fecha_fin_suscripcion >= date.today()


class Tecnico_Categorias(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tecnico', 'categoria')

    def __str__(self):
        return f"{self.tecnico.usuario.username} - {self.categoria.nombre}"

class FotoTrabajos(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE, related_name='fotos_trabajos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    url_foto = CloudinaryField('image') # Use CloudinaryField
    subido_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.tecnico.usuario.username} - {self.categoria.nombre}"

class Solicitud(models.Model):
    estado_choices = (
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_cliente', limit_choices_to={'tipo': 'cliente'})
    tecnico = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_tecnico')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    direccion = models.TextField()
    estado = models.CharField(max_length=20, choices=estado_choices, default='pendiente')
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitud #{self.id} de {self.cliente.username} ({self.get_estado_display()})"

class FotoSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='fotos_solicitud')
    url_foto = CloudinaryField('image') # Use CloudinaryField
    subido_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto para Solicitud #{self.solicitud.id}"
    
    
class Distritos(models.Model):
    nombre = models.CharField(max_length=100, unique=True, null=False, blank=False)

    def __str__(self):
        return self.nombre

class DistritosTecnicos(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    distrito = models.ForeignKey(Distritos, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tecnico', 'distrito')

    def __str__(self):
        return f"{self.tecnico.usuario.username} - {self.distrito.nombre}"