import copy
import secrets
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.http import Http404
from django.utils import timezone

from cuentas.models import Cuenta
from funciones.models import Funcion
from salas.services import validar_distribucion

from .models import Entrada


CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
CODE_LENGTH = 12
LIMITE_REEMBOLSO = timedelta(hours=24)
MOTIVOS_ELIMINACION = frozenset({'reembolso', 'finalizacion'})


def etiqueta_fila(numero_fila):
    """Return the 1-based row number as a bijective base-26 label."""
    if isinstance(numero_fila, bool) or not isinstance(numero_fila, int) or numero_fila < 1:
        raise ValueError('El número de fila debe ser un entero positivo.')

    etiqueta = ''
    while numero_fila:
        numero_fila, resto = divmod(numero_fila - 1, 26)
        etiqueta = chr(ord('A') + resto) + etiqueta
    return etiqueta


def _indice_fila(etiqueta):
    if not isinstance(etiqueta, str):
        raise ValueError('La etiqueta de fila debe ser texto.')

    etiqueta = etiqueta.strip().upper()
    if not etiqueta or len(etiqueta) > 4 or any(not 'A' <= letra <= 'Z' for letra in etiqueta):
        raise ValueError('La etiqueta de fila no es válida.')

    numero_fila = 0
    for letra in etiqueta:
        numero_fila = numero_fila * 26 + ord(letra) - ord('A') + 1
    return numero_fila - 1


def _entero_positivo(value, label):
    if isinstance(value, bool):
        raise ValueError(f'{label} debe ser un entero positivo.')
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.strip().isdecimal():
        parsed = int(value.strip())
    else:
        raise ValueError(f'{label} debe ser un entero positivo.')

    if parsed < 1:
        raise ValueError(f'{label} debe ser un entero positivo.')
    return parsed


def _generar_codigo():
    return ''.join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


def _normalizar_distribucion(distribucion):
    if not isinstance(distribucion, dict):
        raise ValueError('La distribución de la función no es válida.')

    resultado = copy.deepcopy(distribucion)
    try:
        resultado['filas'] = validar_distribucion(resultado)['filas']
    except (TypeError, ValueError) as exc:
        raise ValueError('La distribución de la función no es válida.') from exc
    return resultado


def _posicion_asiento(fila_celdas, numero_asiento):
    ordinal = 0
    for indice_celda, celda in enumerate(fila_celdas):
        if celda in {'A', 'R'}:
            ordinal += 1
            if ordinal == numero_asiento:
                return indice_celda
    raise ValueError('El número de asiento no existe en la fila seleccionada.')


@transaction.atomic
def crear_entrada(funcion_id, cuenta_id, n_asiento, l_fila):
    funcion_pk = _entero_positivo(funcion_id, 'El identificador de la función')
    cuenta_pk = _entero_positivo(cuenta_id, 'El identificador de la cuenta')
    numero_asiento = _entero_positivo(n_asiento, 'El número de asiento')
    fila = l_fila.strip().upper() if isinstance(l_fila, str) else l_fila
    indice_fila = _indice_fila(fila)

    try:
        funcion = Funcion.objects.select_for_update().get(pk=funcion_pk)
    except Funcion.DoesNotExist as exc:
        raise ValueError('La función seleccionada no existe.') from exc

    try:
        cuenta = Cuenta.objects.get(pk=cuenta_pk)
    except Cuenta.DoesNotExist as exc:
        raise ValueError('La cuenta seleccionada no existe.') from exc

    if funcion.fin <= timezone.now():
        raise ValueError('No se pueden crear entradas para una función finalizada.')

    distribucion = _normalizar_distribucion(funcion.distribucion)
    filas_normalizadas = distribucion['filas']

    if indice_fila >= len(filas_normalizadas):
        raise ValueError('La fila seleccionada no existe en la función.')

    fila_celdas = list(filas_normalizadas[indice_fila])
    posicion = _posicion_asiento(fila_celdas, numero_asiento)
    if fila_celdas[posicion] == 'R':
        raise ValueError('El asiento seleccionado ya está reservado.')

    fila_celdas[posicion] = 'R'
    distribucion['filas'][indice_fila] = ''.join(fila_celdas)
    funcion.distribucion = distribucion
    funcion.disponibilidad -= 1
    funcion.entradas_compradas += 1

    try:
        with transaction.atomic():
            entrada = Entrada.objects.create(
                funcion=funcion,
                cuenta=cuenta,
                codigo=_generar_codigo(),
                l_fila=fila,
                n_asiento=numero_asiento,
            )
    except IntegrityError as exc:
        raise ValueError(
            'No se pudo crear la entrada porque el código o el asiento ya están registrados.'
        ) from exc

    funcion.save(update_fields=['distribucion', 'disponibilidad', 'entradas_compradas'])
    return entrada


@transaction.atomic
def eliminar_entrada(entrada_id, motivo):
    if not isinstance(motivo, str) or motivo not in MOTIVOS_ELIMINACION:
        raise ValueError('El motivo de eliminación no es válido.')

    entrada_pk = _entero_positivo(entrada_id, 'El identificador de la entrada')
    try:
        entrada = Entrada.objects.select_for_update().get(pk=entrada_pk)
    except Entrada.DoesNotExist as exc:
        raise Http404('Entrada no encontrada') from exc

    if motivo == 'reembolso':
        if not entrada.activa:
            raise ValueError('No se puede reembolsar una entrada ya validada.')

        funcion = Funcion.objects.select_for_update().get(pk=entrada.funcion_id)
        if funcion.inicio - timezone.now() < LIMITE_REEMBOLSO:
            raise ValueError(
                'El reembolso solo está permitido con al menos 24 horas de anticipación.'
            )
        if funcion.entradas_compradas < 1:
            raise ValueError('Los datos de entradas compradas de la función no son válidos.')

        distribucion = _normalizar_distribucion(funcion.distribucion)
        indice_fila = _indice_fila(entrada.l_fila)
        if indice_fila >= len(distribucion['filas']):
            raise ValueError('La fila de la entrada ya no existe en la función.')

        fila_celdas = list(distribucion['filas'][indice_fila])
        posicion = _posicion_asiento(fila_celdas, entrada.n_asiento)
        if fila_celdas[posicion] != 'R':
            raise ValueError('El asiento de la entrada no figura como reservado.')

        fila_celdas[posicion] = 'A'
        distribucion['filas'][indice_fila] = ''.join(fila_celdas)
        funcion.distribucion = distribucion
        funcion.disponibilidad += 1
        funcion.entradas_compradas -= 1
        funcion.save(update_fields=['distribucion', 'disponibilidad', 'entradas_compradas'])

    entrada.delete()


def listar_entradas(cuenta_id):
    cuenta_pk = _entero_positivo(cuenta_id, 'El identificador de la cuenta')
    return (
        Entrada.objects.filter(cuenta_id=cuenta_pk)
        .select_related('funcion__pelicula', 'funcion__sala')
        .order_by('funcion__inicio', 'l_fila', 'n_asiento')
    )


def obtener_entrada(entrada_id, cuenta_id):
    try:
        entrada_pk = _entero_positivo(entrada_id, 'El identificador de la entrada')
        cuenta_pk = _entero_positivo(cuenta_id, 'El identificador de la cuenta')
    except ValueError as exc:
        raise Http404('Entrada no encontrada') from exc

    try:
        return (
            Entrada.objects.select_related('funcion__pelicula', 'funcion__sala')
            .get(pk=entrada_pk, cuenta_id=cuenta_pk)
        )
    except Entrada.DoesNotExist as exc:
        raise Http404('Entrada no encontrada') from exc


@transaction.atomic
def validar_entrada(codigo):
    if not isinstance(codigo, str) or not codigo.strip():
        return None

    codigo_normalizado = codigo.strip().upper()
    actualizadas = Entrada.objects.filter(
        codigo=codigo_normalizado,
        activa=True,
    ).update(activa=False)
    if actualizadas != 1:
        return None

    return (
        Entrada.objects.select_related('funcion__pelicula', 'funcion__sala')
        .get(codigo=codigo_normalizado)
    )
