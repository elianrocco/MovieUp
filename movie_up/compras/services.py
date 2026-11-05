from django.db import transaction
from django.http import Http404
from django.utils import timezone

from entradas.services import eliminar_entradas_por_finalizacion
from funciones.models import Funcion
from peliculas.models import Pelicula


def obtener_pelicula(pelicula_id):
    try:
        return Pelicula.objects.get(pk=pelicula_id)
    except Pelicula.DoesNotExist as exc:
        raise Http404('Película no encontrada') from exc


@transaction.atomic
def barrer_funciones_vencidas(pelicula_id):
    funciones = list(
        Funcion.objects.select_for_update()
        .filter(pelicula_id=pelicula_id, fin__lte=timezone.now())
        .order_by('pk')
    )
    for funcion in funciones:
        eliminar_entradas_por_finalizacion(funcion.pk)
        if funcion.funcion_activa:
            funcion.funcion_activa = False
            funcion.save(update_fields=['funcion_activa'])
    return len(funciones)


def listar_funciones_vendibles(pelicula_id):
    return (
        Funcion.objects
        .filter(pelicula_id=pelicula_id, funcion_activa=True, fin__gt=timezone.now())
        .select_related('sala')
        .order_by('inicio')
    )


def preparar_compra(pelicula_id):
    pelicula = obtener_pelicula(pelicula_id)
    barrer_funciones_vencidas(pelicula_id)
    return pelicula, listar_funciones_vendibles(pelicula_id)
