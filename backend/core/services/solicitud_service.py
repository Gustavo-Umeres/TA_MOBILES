from core.models import Solicitud
from django.utils import timezone

def crear_solicitud(cliente_id, categoria_id, direccion):
    solicitud = Solicitud.objects.create(
        cliente_id=cliente_id,
        categoria_id=categoria_id,
        direccion=direccion,
        estado="pendiente"
    )
    return solicitud

def actualizar_estado_solicitud(solicitud_id, nuevo_estado):
    solicitud = Solicitud.objects.get(id=solicitud_id)
    solicitud.estado = nuevo_estado
    solicitud.actualizado_en = timezone.now()
    solicitud.save()
    return solicitud
