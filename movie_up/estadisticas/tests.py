from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase, TestCase
from django.template.loader import render_to_string

from funciones.models import Funcion
from peliculas.models import Pelicula
from salas.models import Sala

from .services import (
    _funciones_en_periodo,
    _rango_consulta,
    _rangos_periodo,
    altura_barra,
    build_estadisticas,
)


class PeriodRangeTests(SimpleTestCase):
    timezone = ZoneInfo('America/Argentina/Buenos_Aires')

    def local_datetime(self, year, month, day, hour=12):
        return datetime(year, month, day, hour, tzinfo=self.timezone)

    def test_ranges_use_complete_local_calendar_week_month_and_year(self):
        now = self.local_datetime(2026, 4, 15, 17)

        ranges = _rangos_periodo(now)

        self.assertEqual(
            ranges['semanal'],
            (
                self.local_datetime(2026, 4, 13, 0),
                self.local_datetime(2026, 4, 20, 0),
            ),
        )
        self.assertEqual(
            ranges['mensual'],
            (
                self.local_datetime(2026, 4, 1, 0),
                self.local_datetime(2026, 5, 1, 0),
            ),
        )
        self.assertEqual(
            ranges['anual'],
            (
                self.local_datetime(2026, 1, 1, 0),
                self.local_datetime(2027, 1, 1, 0),
            ),
        )

    def test_query_range_includes_full_week_across_year_boundary(self):
        ranges = _rangos_periodo(self.local_datetime(2026, 1, 3))

        self.assertEqual(
            _rango_consulta(ranges),
            (
                self.local_datetime(2025, 12, 29, 0),
                self.local_datetime(2027, 1, 1, 0),
            ),
        )

    def test_december_month_ends_at_next_year(self):
        ranges = _rangos_periodo(self.local_datetime(2026, 12, 20))

        self.assertEqual(
            ranges['mensual'],
            (
                self.local_datetime(2026, 12, 1, 0),
                self.local_datetime(2027, 1, 1, 0),
            ),
        )

    def test_period_filter_includes_start_excludes_end(self):
        start = self.local_datetime(2026, 4, 13, 0)
        end = self.local_datetime(2026, 4, 20, 0)
        functions = [
            SimpleNamespace(inicio=self.local_datetime(2026, 4, 12, 23)),
            SimpleNamespace(inicio=start),
            SimpleNamespace(inicio=self.local_datetime(2026, 4, 19, 23)),
            SimpleNamespace(inicio=end),
        ]

        self.assertEqual(_funciones_en_periodo(functions, (start, end)), functions[1:3])

    def test_bar_height_scales_with_revenue_and_is_capped_at_thirty_vh(self):
        self.assertEqual(altura_barra(Decimal('2000.00')), Decimal('2'))
        self.assertEqual(altura_barra(Decimal('4000.00')), Decimal('4'))
        self.assertEqual(altura_barra(Decimal('30000.00')), Decimal('30'))
        self.assertEqual(altura_barra(Decimal('100000.00')), Decimal('30'))
        self.assertEqual(altura_barra(Decimal('0.00')), Decimal('0'))
        self.assertEqual(altura_barra(Decimal('-2000.00')), Decimal('0'))


class StatisticsAggregationTests(TestCase):
    timezone = ZoneInfo('America/Argentina/Buenos_Aires')

    def setUp(self):
        self.ahora = datetime(2026, 4, 15, 12, tzinfo=self.timezone)
        self.sala = Sala.objects.create(
            nombre='Estadísticas sala',
            distribucion={'version': 1, 'filas': ['AAA']},
            tipo_sala='2D',
            tipo_sonido='Dolby',
            capacidad=3,
        )

    def create_movie(self, title, genre):
        return Pelicula.objects.create(
            titulo=title,
            imagen_portada='imgs/test.jpg',
            genero=genre,
            duracion_minutos=100,
            descripcion='Test movie',
            clasificacion='ATP',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )

    def create_function(self, movie, *, start=None, tickets=0, price='100.00', active=True):
        start = start or self.ahora
        return Funcion.objects.create(
            funcion_activa=active,
            inicio=start,
            fin=start + timedelta(minutes=100),
            idioma='Español',
            subtitulada=False,
            distribucion={'version': 1, 'filas': ['AAA']},
            disponibilidad=3,
            precio_entrada=price,
            pelicula=movie,
            sala=self.sala,
            entradas_compradas=tickets,
        )

    def test_period_totals_include_inactive_functions_and_exclude_out_of_period(self):
        drama = self.create_movie('Drama A', 'Drama')
        comedy = self.create_movie('Comedy A', 'Comedia')
        self.create_movie('Documentary A', 'Documental')
        self.create_function(drama, tickets=2, price='100.00')
        self.create_function(drama, tickets=3, price='50.00', active=False)
        self.create_function(comedy, tickets=2, price='200.00')
        self.create_function(
            comedy,
            start=datetime(2026, 4, 25, 12, tzinfo=self.timezone),
            tickets=4,
            price='100.00',
        )
        self.create_function(
            drama,
            start=datetime(2025, 12, 30, 12, tzinfo=self.timezone),
            tickets=20,
            price='100.00',
        )

        stats = build_estadisticas(self.ahora)

        weekly_genres = {item['genero']: item['recaudacion'] for item in stats['semanal']['generos']}
        self.assertEqual(weekly_genres, {
            'Comedia': Decimal('400.00'),
            'Documental': Decimal('0.00'),
            'Drama': Decimal('350.00'),
        })
        weekly_movies = stats['semanal']['peliculas']
        self.assertEqual(
            [(movie['titulo'], movie['entradas'], movie['recaudacion']) for movie in weekly_movies],
            [
                ('Comedy A', 2, Decimal('400.00')),
                ('Drama A', 5, Decimal('350.00')),
                ('Documentary A', 0, Decimal('0.00')),
            ],
        )
        self.assertTrue(weekly_movies[0]['es_lider'])
        self.assertFalse(any(movie['es_lider'] for movie in weekly_movies[1:]))

        monthly_movies = {movie['titulo']: movie for movie in stats['mensual']['peliculas']}
        self.assertEqual(monthly_movies['Comedy A']['entradas'], 6)
        self.assertEqual(monthly_movies['Comedy A']['recaudacion'], Decimal('800.00'))
        self.assertEqual(monthly_movies['Drama A']['recaudacion'], Decimal('350.00'))

    def test_build_estadisticas_queries_functions_once_for_all_periods(self):
        movie = self.create_movie('Query Count', 'Drama')
        self.create_function(movie, tickets=1)

        with self.assertNumQueries(2):
            stats = build_estadisticas(self.ahora)

        self.assertEqual(set(stats), {'semanal', 'mensual', 'anual'})

    def test_empty_movies_returns_empty_lists_and_no_leader(self):
        stats = build_estadisticas(self.ahora)

        for period in stats.values():
            self.assertEqual(period['generos'], [])
            self.assertEqual(period['peliculas'], [])

    def test_chart_renders_totals_above_gold_bars_and_genres_below_baseline(self):
        self.create_movie('Drama Movie', 'Drama')
        comedy = self.create_movie('Comedy Movie', 'Comedia')
        self.create_function(comedy, tickets=2, price='200.00')

        html = render_to_string(
            'estadisticas/_panel.html',
            {'estadisticas': build_estadisticas(self.ahora)},
        )
        weekly = html.split('data-stats-period="semanal"', 1)[1].split(
            'data-stats-period="mensual"', 1
        )[0]

        self.assertEqual(weekly.count('class="stats-chart__column"'), 2)
        self.assertEqual(weekly.count('class="stats-chart__bar stats-chart__bar--gold"'), 2)
        self.assertIn('$400.00', weekly)
        self.assertLess(
            weekly.index('$400.00'),
            weekly.index('class="stats-chart__bar stats-chart__bar--gold"'),
        )
        self.assertLess(
            weekly.index('class="stats-chart__bar stats-chart__bar--gold"'),
            weekly.index('class="stats-chart__labels"'),
        )
        self.assertGreater(weekly.index('class="stats-chart__labels"'), 0)
        self.assertIn('title="Comedia"', weekly)
        self.assertRegex(weekly, r'height: 0\.40*vh')
