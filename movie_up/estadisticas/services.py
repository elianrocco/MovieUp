from datetime import datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

from funciones.models import Funcion
from peliculas.models import Pelicula


PERIODOS = ('semanal', 'mensual', 'anual')
RECAUDACION_POR_PASO = Decimal('2000')
PASO_VH_POR_2000 = Decimal('2')
ALTURA_MAXIMA_VH = Decimal('30')


def _zona_local():
    return ZoneInfo(settings.TIME_ZONE)


def _ahora_local(ahora=None):
    zona = _zona_local()
    ahora = ahora or timezone.now()
    if timezone.is_naive(ahora):
        ahora = timezone.make_aware(ahora, zona)
    return timezone.localtime(ahora, zona)


def _inicio_del_dia(fecha):
    return timezone.make_aware(datetime.combine(fecha, time.min), _zona_local())


def _rango_periodo(modo, ahora=None):
    """Return the local-calendar [start, end) range for a period."""
    local_now = _ahora_local(ahora)
    today = local_now.date()

    if modo == 'semanal':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=7)
    elif modo == 'mensual':
        start_date = today.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
    elif modo == 'anual':
        start_date = today.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1)
    else:
        raise ValueError(f"Periodo desconocido: {modo}")

    return _inicio_del_dia(start_date), _inicio_del_dia(end_date)


def _rangos_periodo(ahora=None):
    return {modo: _rango_periodo(modo, ahora) for modo in PERIODOS}


def _rango_consulta(rangos):
    """Cover the calendar year and the full current week with one query."""
    inicio_anual, fin_anual = rangos['anual']
    inicio_semanal, fin_semanal = rangos['semanal']
    return min(inicio_anual, inicio_semanal), max(fin_anual, fin_semanal)


def _funciones_en_periodo(funciones, rango):
    inicio, fin = rango
    return [funcion for funcion in funciones if inicio <= funcion.inicio < fin]


def altura_barra(recaudacion):
    recaudacion = Decimal(str(recaudacion))
    altura = (recaudacion / RECAUDACION_POR_PASO) * PASO_VH_POR_2000
    return min(ALTURA_MAXIMA_VH, max(Decimal('0'), altura))


def build_estadisticas(ahora=None):
    """Build weekly, monthly, and annual statistics from one functions query."""
    rangos = _rangos_periodo(ahora)
    inicio_consulta, fin_consulta = _rango_consulta(rangos)
    peliculas = list(Pelicula.objects.order_by('pk'))
    funciones = list(
        Funcion.objects.select_related('pelicula')
        .filter(inicio__gte=inicio_consulta, inicio__lt=fin_consulta)
        .order_by('pk')
    )
    generos_registrados = sorted({pelicula.genero for pelicula in peliculas})

    resultado = {}
    for modo, rango in rangos.items():
        funciones_periodo = _funciones_en_periodo(funciones, rango)
        por_pelicula = {
            pelicula.pk: {
                'titulo': pelicula.titulo,
                'genero': pelicula.genero,
                'entradas': 0,
                'recaudacion': Decimal('0.00'),
                'es_lider': False,
            }
            for pelicula in peliculas
        }
        por_genero = {
            genero: Decimal('0.00') for genero in generos_registrados
        }

        for funcion in funciones_periodo:
            recaudacion_funcion = funcion.precio_entrada * funcion.entradas_compradas
            pelicula = por_pelicula[funcion.pelicula_id]
            pelicula['entradas'] += funcion.entradas_compradas
            pelicula['recaudacion'] += recaudacion_funcion
            por_genero[funcion.pelicula.genero] += recaudacion_funcion

        peliculas_periodo = sorted(
            por_pelicula.values(),
            key=lambda pelicula: (-pelicula['recaudacion'], pelicula['titulo'].casefold()),
        )
        if peliculas_periodo:
            peliculas_periodo[0]['es_lider'] = True

        resultado[modo] = {
            'generos': [
                {
                    'genero': genero,
                    'recaudacion': por_genero[genero],
                    'altura_vh': altura_barra(por_genero[genero]),
                }
                for genero in generos_registrados
            ],
            'peliculas': peliculas_periodo,
        }

    return resultado
