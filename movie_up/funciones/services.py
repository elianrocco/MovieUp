import copy
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.http import Http404
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from peliculas.models import Pelicula
from salas.models import Sala
from salas.services import validar_distribucion

from .models import Funcion


MAX_PRICE = Decimal('99999999.99')


def list_funciones():
    return Funcion.objects.select_related('pelicula', 'sala').order_by('inicio')


def get_funcion(pk):
    try:
        return Funcion.objects.select_related('pelicula', 'sala').get(pk=pk)
    except Funcion.DoesNotExist as exc:
        raise Http404('Función no encontrada') from exc


def _required_text(data, field, label, max_length):
    value = data.get(field)
    if not isinstance(value, str):
        raise ValueError(f'{label} es obligatorio y debe ser texto.')

    value = value.strip()
    if not value:
        raise ValueError(f'{label} es obligatorio.')
    if len(value) > max_length:
        raise ValueError(f'{label} no puede superar los {max_length} caracteres.')
    return value


def _required_related(data, field, model, label):
    value = data.get(field)
    if isinstance(value, model):
        if value.pk is None:
            raise ValueError(f'La selección de {label} no es válida.')
        return value
    if value is None or value == '' or isinstance(value, bool):
        raise ValueError(f'Debe seleccionar {label}.')

    pk = _parse_pk(value, label)

    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist as exc:
        raise ValueError(f'La selección de {label} ya no existe.') from exc


def _parse_pk(value, label):
    if isinstance(value, int) and not isinstance(value, bool):
        pk = value
    elif isinstance(value, str) and value.strip().isdecimal():
        pk = int(value.strip())
    else:
        raise ValueError(f'La selección de {label} no es válida.')
    if pk < 1:
        raise ValueError(f'La selección de {label} no es válida.')
    return pk


def _optional_related(data, field, model, label, current):
    if field not in data or data[field] is None or data[field] == '':
        return current
    return _required_related(data, field, model, label)


def _required_boolean(data, field, label):
    if field not in data:
        raise ValueError(f'{label} es obligatorio.')
    return _parse_boolean(data[field], label)


def _parse_boolean(value, label):
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {'true', '1', 'on'}:
            return True
        if normalized in {'false', '0', 'off'}:
            return False
    raise ValueError(f'{label} debe ser verdadero o falso.')


def _optional_boolean(data, field, label):
    if field not in data or data[field] is None or data[field] == '':
        return None
    return _parse_boolean(data[field], label)


def _required_start(value):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        parsed = parse_datetime(value.strip())
    else:
        parsed = None

    if parsed is None:
        raise ValueError('El inicio es obligatorio y debe ser una fecha y hora válida.')

    if timezone.is_naive(parsed):
        try:
            parsed = timezone.make_aware(parsed, timezone.get_default_timezone())
        except (OverflowError, ValueError) as exc:
            raise ValueError('El inicio no corresponde a una hora local válida.') from exc
    return parsed


def _optional_start(data, field, current):
    if field not in data or data[field] is None or data[field] == '':
        return current, False

    start = _required_start(data[field])
    changed = start != current
    if changed:
        _validate_start_not_past(start)
    return start, changed


def _validate_start_not_past(start):
    if start < timezone.now():
        raise ValueError('El inicio no puede ser anterior al momento actual.')


def _required_price(value):
    if value is None or value == '':
        raise ValueError('El precio de entrada es obligatorio.')
    try:
        price = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError('El precio de entrada debe ser un número válido.') from exc

    if not price.is_finite():
        raise ValueError('El precio de entrada debe ser un número válido.')
    if price < 0:
        raise ValueError('El precio de entrada no puede ser negativo.')
    if price.as_tuple().exponent < -2:
        raise ValueError('El precio de entrada admite como máximo dos decimales.')
    if price > MAX_PRICE:
        raise ValueError('El precio de entrada excede el máximo permitido.')
    return price


def _optional_price(data, field):
    if field not in data or data[field] is None or data[field] == '':
        return None
    return _required_price(data[field])


def _optional_text(data, field, label, max_length):
    if field not in data or data[field] is None or data[field] == '':
        return None
    value = data[field]
    if not isinstance(value, str):
        raise ValueError(f'{label} debe ser texto.')
    value = value.strip()
    if not value:
        return None
    if len(value) > max_length:
        raise ValueError(f'{label} no puede superar los {max_length} caracteres.')
    return value


def _lock_salas(sala_ids):
    requested_ids = sorted(set(sala_ids))
    locked_salas = list(
        Sala.objects.select_for_update().filter(pk__in=requested_ids).order_by('pk')
    )
    if len(locked_salas) != len(requested_ids):
        raise ValueError('La sala seleccionada ya no existe.')
    return {sala.pk: sala for sala in locked_salas}


def _distribution_snapshot(sala):
    normalized = validar_distribucion(sala.distribucion)
    snapshot = copy.deepcopy(sala.distribucion)
    available = sum(row.count('A') for row in normalized['filas'])
    return snapshot, available


def _ensure_no_overlap(sala_id, start, end, exclude_pk=None):
    conflicts = Funcion.objects.filter(
        sala_id=sala_id,
        inicio__lt=end,
        fin__gt=start,
    )
    if exclude_pk is not None:
        conflicts = conflicts.exclude(pk=exclude_pk)
    if conflicts.exists():
        raise ValueError('La sala ya tiene otra función en ese horario.')


@transaction.atomic
def create_funcion(data):
    pelicula = _required_related(data, 'pelicula', Pelicula, 'una película')
    sala_value = data.get('sala')
    if isinstance(sala_value, Sala):
        sala_id = sala_value.pk
        if sala_id is None:
            raise ValueError('La selección de la sala no es válida.')
    else:
        if sala_value is None or sala_value == '' or isinstance(sala_value, bool):
            raise ValueError('Debe seleccionar una sala.')
        sala_id = _parse_pk(sala_value, 'una sala')

    start = _required_start(data.get('inicio'))
    idioma = _required_text(data, 'idioma', 'El idioma', 45)
    subtitulada = _required_boolean(data, 'subtitulada', 'Subtitulada')
    funcion_activa = _required_boolean(data, 'funcion_activa', 'Función activa')
    price = _required_price(data.get('precio_entrada'))

    sala = _lock_salas([sala_id])[sala_id]
    _validate_start_not_past(start)
    end = start + timedelta(minutes=pelicula.duracion_minutos)
    if funcion_activa and end <= timezone.now():
        raise ValueError('No se puede crear activa una función cuyo fin ya pasó.')

    distribution, availability = _distribution_snapshot(sala)
    _ensure_no_overlap(sala.pk, start, end)

    funcion = Funcion(
        funcion_activa=funcion_activa,
        inicio=start,
        fin=end,
        idioma=idioma,
        subtitulada=subtitulada,
        distribucion=distribution,
        disponibilidad=availability,
        precio_entrada=price,
        pelicula=pelicula,
        sala=sala,
        entradas_compradas=0,
    )
    funcion.save()
    return funcion


@transaction.atomic
def update_funcion(pk, data):
    try:
        funcion = Funcion.objects.select_for_update().get(pk=pk)
    except Funcion.DoesNotExist as exc:
        raise Http404('Función no encontrada') from exc

    if funcion.entradas_compradas > 0:
        raise ValueError('No se puede actualizar una función con entradas compradas.')

    pelicula_actual = Pelicula.objects.get(pk=funcion.pelicula_id)
    sala_actual = Sala.objects.get(pk=funcion.sala_id)
    pelicula = _optional_related(
        data, 'pelicula', Pelicula, 'una película', pelicula_actual
    )
    sala_seleccionada = _optional_related(
        data, 'sala', Sala, 'una sala', sala_actual
    )
    start, start_changed = _optional_start(data, 'inicio', funcion.inicio)
    movie_changed = pelicula.pk != funcion.pelicula_id
    room_changed = sala_seleccionada.pk != funcion.sala_id
    end = (
        start + timedelta(minutes=pelicula.duracion_minutos)
        if start_changed or movie_changed
        else funcion.fin
    )

    idioma = _optional_text(data, 'idioma', 'El idioma', 45)
    subtitulada = _optional_boolean(data, 'subtitulada', 'Subtitulada')
    funcion_activa = _optional_boolean(data, 'funcion_activa', 'Función activa')
    price = _optional_price(data, 'precio_entrada')

    if (
        funcion_activa is True
        and not funcion.funcion_activa
        and end <= timezone.now()
    ):
        raise ValueError('No se puede activar una función cuyo fin ya pasó.')

    locked_salas = _lock_salas([funcion.sala_id, sala_seleccionada.pk])
    sala = locked_salas[sala_seleccionada.pk]

    if start_changed or movie_changed or room_changed:
        _ensure_no_overlap(sala.pk, start, end, exclude_pk=funcion.pk)

    if room_changed:
        distribution, availability = _distribution_snapshot(sala)
        funcion.distribucion = distribution
        funcion.disponibilidad = availability

    funcion.pelicula = pelicula
    funcion.sala = sala
    funcion.inicio = start
    funcion.fin = end
    if idioma is not None:
        funcion.idioma = idioma
    if subtitulada is not None:
        funcion.subtitulada = subtitulada
    if funcion_activa is not None:
        funcion.funcion_activa = funcion_activa
    if price is not None:
        funcion.precio_entrada = price

    funcion.save()
    return funcion


@transaction.atomic
def delete_funcion(pk):
    try:
        funcion = Funcion.objects.select_for_update().get(pk=pk)
    except Funcion.DoesNotExist as exc:
        raise Http404('Función no encontrada') from exc

    if funcion.entradas_compradas > 0:
        raise ValueError('No se puede eliminar una función con entradas compradas.')

    funcion.delete()
