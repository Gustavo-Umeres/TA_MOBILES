from core.models import Tecnico, TecnicoCategoria, Categoria, Usuario

def asignar_categorias_a_tecnico(tecnico_id, lista_categorias_ids):
    for categoria_id in lista_categorias_ids:
        TecnicoCategoria.objects.get_or_create(
            tecnico_id=tecnico_id,
            categoria_id=categoria_id
        )

def obtener_tecnicos_por_categoria(categoria_id):
    return Tecnico.objects.filter(
        tecnicocategoria__categoria_id=categoria_id,
        usuario__estado="activo"
    )
