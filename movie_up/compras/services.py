from django.db import transaction
from django.http import Http404
from django.utils import timezone

from entradas.services import (
    crear_entrada,
    eliminar_entradas_por_finalizacion,
    etiqueta_fila,
)
from funciones.models import Funcion
from peliculas.models import Pelicula
from salas.services import validar_distribucion

CELL_TITLES = {'P': 'Pasillo', 'A': 'Asiento', 'R': 'Reservado'}


def obtener_pelicula(pelicula_id):
    try:
        return Pelicula.objects.get(pk=pelicula_id)
    except Pelicula.DoesNotExist as exc:
        raise Http404('Película no encontrada') from exc


def obtener_funcion_vendible(pelicula_id, funcion_id):
    try:
        funcion = Funcion.objects.select_related('pelicula', 'sala').get(
            pk=funcion_id,
            pelicula_id=pelicula_id,
        )
    except Funcion.DoesNotExist as exc:
        raise Http404('Función no encontrada') from exc

    if not funcion.funcion_activa or funcion.fin <= timezone.now():
        raise Http404('Función no disponible')

    return funcion


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


def construir_cuadricula(funcion):
    distribucion = validar_distribucion(funcion.distribucion)
    filas_normalizadas = distribucion['filas']

    filas = []
    for indice_fila, celdas in enumerate(filas_normalizadas):
        etiqueta = etiqueta_fila(indice_fila + 1)
        ordinal = 0
        celdas_render = []
        for celda in celdas:
            if celda in {'A', 'R'}:
                ordinal += 1
            asiento = ordinal if celda == 'A' else None
            titulo = (
                f'Fila {etiqueta}, asiento {asiento}'
                if asiento is not None
                else CELL_TITLES[celda]
            )
            celdas_render.append({'tipo': celda, 'asiento': asiento, 'titulo': titulo})
        filas.append({'etiqueta': etiqueta, 'celdas': celdas_render})

    return {
        'filas': filas,
        'ancho': len(filas_normalizadas[0]),
        'marca': ','.join(filas_normalizadas),
    }


def _parsear_celdas(celdas):
    pares = []
    for celda in celdas:
        partes = str(celda).split(':')
        if len(partes) != 2:
            raise ValueError('La selección de asientos no es válida.')

        fila = partes[0].strip().upper()
        numero = partes[1].strip()
        if not fila or not numero.isdecimal():
            raise ValueError('La selección de asientos no es válida.')

        pares.append((fila, int(numero)))

    if not pares:
        raise ValueError('Debe seleccionar al menos un asiento.')
    if len(set(pares)) != len(pares):
        raise ValueError('Hay asientos repetidos en la selección.')

    return pares


@transaction.atomic
def confirmar_compra(funcion_id, cuenta_id, celdas, marca_distribucion):
    pares = _parsear_celdas(celdas)

    try:
        funcion = Funcion.objects.select_for_update().get(pk=funcion_id)
    except Funcion.DoesNotExist as exc:
        raise ValueError('La función seleccionada ya no existe.') from exc

    if not funcion.funcion_activa or funcion.fin <= timezone.now():
        raise ValueError('La función seleccionada ya no está disponible.')

    filas = validar_distribucion(funcion.distribucion)['filas']
    if marca_distribucion != ','.join(filas):
        raise ValueError('La distribución de la función cambió. Volvé a cargar la página.')

    if funcion.disponibilidad < len(pares):
        raise ValueError('No hay suficientes entradas disponibles.')

    entradas = []
    for fila, asiento in pares:
        entradas.append(crear_entrada(funcion.pk, cuenta_id, asiento, fila))
    return entradas
