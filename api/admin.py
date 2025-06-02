from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Categoria, Tecnico, Tecnico_Categorias, FotoTrabajos,
    Solicitud, FotoSolicitud, Distritos, DistritosTecnicos
)

# --- INLINES para modelos ManyToMany con 'through' ---
class TecnicoCategoriasInline(admin.TabularInline):
    model = Tecnico_Categorias
    extra = 1

class DistritosTecnicosInline(admin.TabularInline):
    model = DistritosTecnicos
    extra = 1

# --- Personaliza la administración del modelo Usuario ---
# La forma más simple de añadir campos al UserAdmin es modificar directamente los fieldsets base.
# Esto es más robusto que intentar concatenar o modificar tuplas directamente.
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'tipo', 'estado',
        'is_staff', 'is_active', 'creado_en'
    )
    search_fields = ('username', 'email', 'dni', 'telefono')
    list_filter = ('tipo', 'estado', 'is_staff', 'is_active')
    readonly_fields = ('creado_en', 'last_login', 'date_joined')

    # Modificamos los fieldsets de la clase base UserAdmin.
    # Creamos una copia mutable, añadimos nuestros campos y luego la convertimos de nuevo a tupla.
    
    # Fieldsets para ver/editar usuarios existentes
    fieldsets = list(UserAdmin.fieldsets) # Convertir a lista para modificar
    fieldsets[1] = ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'dni', 'telefono', 'tipo', 'estado')})
    fieldsets = tuple(fieldsets) # Volver a convertir a tupla

    # Fieldsets para añadir nuevos usuarios (incluyendo campos personalizados para la creación)
    add_fieldsets = list(UserAdmin.add_fieldsets) # Convertir a lista para modificar
    add_fieldsets.append(
        (('Información Personal (Adición)', {'fields': ('first_name', 'last_name', 'dni', 'telefono', 'tipo', 'estado')}),)
    )
    add_fieldsets = tuple(add_fieldsets) # Volver a convertir a tupla


# Registra tus modelos en el panel de administración
admin.site.register(Usuario, CustomUserAdmin)


@admin.register(Tecnico)
class TecnicoAdmin(admin.ModelAdmin):
    list_display = (
        'usuario_username', 'calificacion', 'suscripcion_activa',
        'fecha_inicio_suscripcion', 'fecha_fin_suscripcion',
        'mercadopago_preference_id', 'mercadopago_collector_id'
    )
    search_fields = ('usuario__username', 'usuario__email', 'usuario__dni')
    list_filter = ('suscripcion_activa', 'calificacion')
    
    inlines = [TecnicoCategoriasInline, DistritosTecnicosInline] 

    def usuario_username(self, obj):
        return obj.usuario.username
    usuario_username.short_description = 'Usuario'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Tecnico_Categorias)
class TecnicoCategoriasAdmin(admin.ModelAdmin):
    list_display = ('tecnico_username', 'categoria_nombre')
    search_fields = ('tecnico__usuario__username', 'categoria__nombre')
    list_filter = ('categoria',)

    def tecnico_username(self, obj):
        return obj.tecnico.usuario.username
    tecnico_username.short_description = 'Técnico'

    def categoria_nombre(self, obj):
        return obj.categoria.nombre
    categoria_nombre.short_description = 'Categoría'


@admin.register(FotoTrabajos)
class FotoTrabajosAdmin(admin.ModelAdmin):
    list_display = ('tecnico_username', 'categoria_nombre', 'url_foto', 'subido_en')
    search_fields = ('tecnico__usuario__username', 'categoria__nombre')
    list_filter = ('categoria', 'subido_en')
    readonly_fields = ('subido_en',)

    def tecnico_username(self, obj):
        return obj.tecnico.usuario.username
    tecnico_username.short_description = 'Técnico'

    def categoria_nombre(self, obj):
        return obj.categoria.nombre
    categoria_nombre.short_description = 'Categoría'


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente_username', 'tecnico_username', 'categoria_nombre',
        'estado', 'calificacion', 'creado_en', 'actualizado_en'
    )
    search_fields = (
        'cliente__username', 'cliente__email', 'tecnico__usuario__username',
        'categoria__nombre', 'direccion'
    )
    list_filter = ('estado', 'categoria', 'creado_en', 'actualizado_en')
    readonly_fields = ('creado_en', 'actualizado_en')

    def cliente_username(self, obj):
        return obj.cliente.username
    cliente_username.short_description = 'Cliente'

    def tecnico_username(self, obj):
        return obj.tecnico.usuario.username if obj.tecnico else 'N/A'
    tecnico_username.short_description = 'Técnico Asignado'

    def categoria_nombre(self, obj):
        return obj.categoria.nombre
    categoria_nombre.short_description = 'Categoría de Solicitud'


@admin.register(FotoSolicitud)
class FotoSolicitudAdmin(admin.ModelAdmin):
    list_display = ('solicitud_id', 'url_foto', 'subido_en')
    search_fields = ('solicitud__id',)
    readonly_fields = ('subido_en',)

    def solicitud_id(self, obj):
        return obj.solicitud.id
    solicitud_id.short_description = 'ID Solicitud'


@admin.register(Distritos)
class DistritosAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(DistritosTecnicos)
class DistritosTecnicosAdmin(admin.ModelAdmin):
    list_display = ('tecnico_username', 'distrito_nombre')
    search_fields = ('tecnico__usuario__username', 'distrito__nombre')
    list_filter = ('distrito',)

    def tecnico_username(self, obj):
        return obj.tecnico.usuario.username
    tecnico_username.short_description = 'Técnico'

    def distrito_nombre(self, obj):
        return obj.distrito.nombre
    distrito_nombre.short_description = 'Distrito'