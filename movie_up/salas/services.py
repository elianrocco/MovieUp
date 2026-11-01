import json

from django.http import Http404

from .models import Sala


ALLOWED_CELLS = frozenset({'P', 'A', 'R'})
MAX_DISTRIBUTION_SIZE = 100


def _parse_distribution(distribucion):
    if isinstance(distribucion, str):
        try:
            distribucion = json.loads(distribucion)
        except json.JSONDecodeError as exc:
            raise ValueError('La distribución debe contener JSON válido.') from exc

    if not isinstance(distribucion, dict):
        raise ValueError('La distribución debe ser un objeto JSON.')

    return distribucion


def validar_distribucion(distribucion):
    """Valida y normaliza una distribución, ignorando la versión del cliente."""
    data = _parse_distribution(distribucion)
    filas = data.get('filas')

    if not isinstance(filas, list) or not filas:
        raise ValueError('La distribución debe contener al menos una fila.')
    if len(filas) > MAX_DISTRIBUTION_SIZE:
        raise ValueError('La distribución no puede superar las 100 filas.')

    filas_normalizadas = []
    for indice, fila in enumerate(filas, start=1):
        if not isinstance(fila, str):
            raise ValueError(f'La fila {indice} debe ser una cadena de caracteres.')

        fila_normalizada = ''.join(fila.split()).upper()
        if not fila_normalizada:
            raise ValueError(f'La fila {indice} no puede estar vacía.')
        filas_normalizadas.append(fila_normalizada)

    ancho = len(filas_normalizadas[0])
    if ancho > MAX_DISTRIBUTION_SIZE:
        raise ValueError('La distribución no puede superar las 100 columnas.')
    if any(len(fila) != ancho for fila in filas_normalizadas):
        raise ValueError('Todas las filas deben tener la misma cantidad de celdas.')

    caracteres_invalidos = {
        caracter
        for fila in filas_normalizadas
        for caracter in fila
        if caracter not in ALLOWED_CELLS
    }
    if caracteres_invalidos:
        invalidos = ', '.join(sorted(caracteres_invalidos))
        raise ValueError(
            f'La distribución contiene caracteres no permitidos: {invalidos}. '
            'Solo se admiten P, A y R.'
        )

    if not any(caracter in {'A', 'R'} for fila in filas_normalizadas for caracter in fila):
        raise ValueError('La sala debe tener al menos una butaca Asiento o Reservado.')

    return {'version': 1, 'filas': filas_normalizadas}


def calcular_capacidad(distribucion):
    """Cuenta las celdas Asiento y Reservado, ignorando Pasillo."""
    data = _parse_distribution(distribucion)
    filas = data.get('filas')
    if not isinstance(filas, list) or any(not isinstance(fila, str) for fila in filas):
        raise ValueError('La distribución debe contener una lista de filas de texto.')

    return sum(
        caracter in {'A', 'R'}
        for fila in filas
        for caracter in ''.join(fila.split()).upper()
    )


def versionar_distribucion(distribucion, distribucion_anterior=None):
    """Asigna la versión inicial o incrementa solo ante cambios reales de filas."""
    nueva = validar_distribucion(distribucion)
    if distribucion_anterior is None:
        return nueva

    anterior = validar_distribucion(distribucion_anterior)
    version_anterior = distribucion_anterior.get('version', 1)
    if type(version_anterior) is not int or version_anterior < 1:
        raise ValueError('La versión almacenada debe ser un entero positivo.')

    nueva['version'] = (
        version_anterior if nueva['filas'] == anterior['filas'] else version_anterior + 1
    )
    return nueva


def list_salas():
    return Sala.objects.all().order_by('nombre')


def get_sala(pk):
    try:
        return Sala.objects.get(pk=pk)
    except Sala.DoesNotExist as exc:
        raise Http404('Sala no encontrada') from exc


def _required_text(data, field, label):
    value = data.get(field)
    if not isinstance(value, str):
        raise ValueError(f'{label} es obligatorio y debe ser texto.')

    value = value.strip()
    if not value:
        raise ValueError(f'{label} es obligatorio.')
    if len(value) > 45:
        raise ValueError(f'{label} no puede superar los 45 caracteres.')
    return value


def _optional_text_update(sala, data, field, label):
    if field not in data or data[field] is None or data[field] == '':
        return
    value = data[field]
    if not isinstance(value, str):
        raise ValueError(f'{label} debe ser texto.')

    value = value.strip()
    if not value:
        return
    if len(value) > 45:
        raise ValueError(f'{label} no puede superar los 45 caracteres.')
    setattr(sala, field, value)


def _validate_unique_name(nombre, exclude_pk=None):
    salas = Sala.objects.filter(nombre=nombre)
    if exclude_pk is not None:
        salas = salas.exclude(pk=exclude_pk)
    if salas.exists():
        raise ValueError(f'Ya existe una sala con el nombre "{nombre}".')


def create_sala(data):
    nombre = _required_text(data, 'nombre', 'El nombre')
    tipo_sala = _required_text(data, 'tipo_sala', 'El tipo de sala')
    tipo_sonido = _required_text(data, 'tipo_sonido', 'El tipo de sonido')
    _validate_unique_name(nombre)

    distribucion = versionar_distribucion(data.get('distribucion'))
    sala = Sala(
        nombre=nombre,
        tipo_sala=tipo_sala,
        tipo_sonido=tipo_sonido,
        distribucion=distribucion,
        capacidad=calcular_capacidad(distribucion),
    )
    sala.save()
    return sala


def update_sala(pk, data):
    sala = get_sala(pk)

    # TODO: Cuando exista la app 'funciones', descomentar la validación de
    # funciones activas antes de permitir actualizar una sala.
    # from funciones.models import Funcion
    # if Funcion.objects.filter(sala=sala, funcion_activa=True).exists():
    #     raise ValueError('No se puede actualizar: la sala tiene funciones activas.')

    _optional_text_update(sala, data, 'nombre', 'El nombre')
    _optional_text_update(sala, data, 'tipo_sala', 'El tipo de sala')
    _optional_text_update(sala, data, 'tipo_sonido', 'El tipo de sonido')
    _validate_unique_name(sala.nombre, exclude_pk=sala.pk)

    if data.get('distribucion') not in (None, ''):
        sala.distribucion = versionar_distribucion(
            data['distribucion'], distribucion_anterior=sala.distribucion
        )

    sala.capacidad = calcular_capacidad(sala.distribucion)
    sala.save()
    return sala


def delete_sala(pk):
    sala = get_sala(pk)

    # TODO: Cuando exista la app 'funciones', descomentar la validación de
    # funciones activas antes de permitir eliminar una sala.
    # from funciones.models import Funcion
    # if Funcion.objects.filter(sala=sala, funcion_activa=True).exists():
    #     raise ValueError('No se puede eliminar: la sala tiene funciones activas.')

    sala.delete()
