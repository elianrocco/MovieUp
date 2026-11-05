from datetime import timedelta

from django.http import Http404
from django.test import TestCase
from django.utils import timezone

from cuentas.models import Cuenta
from entradas.models import Entrada
from funciones.models import Funcion
from peliculas.models import Pelicula
from salas.models import Sala

from .services import (
    barrer_funciones_vencidas,
    listar_funciones_vendibles,
    obtener_pelicula,
    preparar_compra,
)


class CompraDataMixin:
    def setUp(self):
        self.cuenta = Cuenta.objects.create_user('customer@example.com', 'Customer')
        self.pelicula = self.create_pelicula('Película base')
        self.sala = self.create_sala('Sala base')

    def create_pelicula(self, title='Película base'):
        return Pelicula.objects.create(
            titulo=title,
            imagen_portada='imgs/test.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Descripción de prueba',
            clasificacion='ATP',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )

    def create_sala(self, name='Sala base'):
        return Sala.objects.create(
            nombre=name,
            tipo_sala='2D',
            tipo_sonido='Dolby',
            distribucion={'version': 4, 'filas': ['AA']},
            capacidad=2,
        )

    def create_funcion(self, start=None, activa=True, pelicula=None, sala=None):
        if start is None:
            start = timezone.now() + timedelta(days=3)
        return Funcion.objects.create(
            funcion_activa=activa,
            inicio=start,
            fin=start + timedelta(minutes=100),
            idioma='Español',
            subtitulada=False,
            distribucion={'version': 4, 'filas': ['AA']},
            disponibilidad=2,
            precio_entrada='1500.00',
            pelicula=pelicula or self.pelicula,
            sala=sala or self.sala,
            entradas_compradas=0,
        )

    def create_entry(self, funcion, seat_number=1, row='A'):
        return Entrada.objects.create(
            funcion=funcion,
            cuenta=self.cuenta,
            codigo=f'CODE{funcion.pk:04d}{seat_number:04d}',
            l_fila=row,
            n_asiento=seat_number,
        )

    def expire(self, funcion, seconds=1):
        funcion.fin = timezone.now() - timedelta(seconds=seconds)
        funcion.save(update_fields=['fin'])
        return funcion


class ObtenerPeliculaTests(CompraDataMixin, TestCase):
    def test_returns_existing_movie(self):
        self.assertEqual(obtener_pelicula(self.pelicula.pk), self.pelicula)

    def test_missing_movie_raises_404(self):
        with self.assertRaises(Http404):
            obtener_pelicula(999999)


class BarrerFuncionesVencidasTests(CompraDataMixin, TestCase):
    def test_expired_active_function_with_entries_is_cleaned(self):
        funcion = self.expire(self.create_funcion())
        entry = self.create_entry(funcion)
        funcion.refresh_from_db()
        before = (
            funcion.distribucion,
            funcion.disponibilidad,
            funcion.entradas_compradas,
        )

        barradas = barrer_funciones_vencidas(self.pelicula.pk)

        self.assertEqual(barradas, 1)
        self.assertFalse(Entrada.objects.filter(pk=entry.pk).exists())
        funcion.refresh_from_db()
        self.assertFalse(funcion.funcion_activa)
        self.assertEqual(
            (
                funcion.distribucion,
                funcion.disponibilidad,
                funcion.entradas_compradas,
            ),
            before,
        )
        self.assertEqual(list(listar_funciones_vendibles(self.pelicula.pk)), [])

    def test_expired_active_function_without_entries_is_deactivated(self):
        funcion = self.expire(self.create_funcion())

        barradas = barrer_funciones_vencidas(self.pelicula.pk)

        self.assertEqual(barradas, 1)
        funcion.refresh_from_db()
        self.assertFalse(funcion.funcion_activa)

    def test_expired_inactive_function_stays_inactive_without_errors(self):
        funcion = self.expire(self.create_funcion(activa=False))

        barradas = barrer_funciones_vencidas(self.pelicula.pk)

        self.assertEqual(barradas, 1)
        funcion.refresh_from_db()
        self.assertFalse(funcion.funcion_activa)

    def test_future_function_is_untouched(self):
        funcion = self.create_funcion()

        barradas = barrer_funciones_vencidas(self.pelicula.pk)

        self.assertEqual(barradas, 0)
        funcion.refresh_from_db()
        self.assertTrue(funcion.funcion_activa)

    def test_only_selected_movie_is_swept(self):
        other_pelicula = self.create_pelicula('Otra película')
        other_funcion = self.expire(self.create_funcion(pelicula=other_pelicula))
        other_entry = self.create_entry(other_funcion)
        funcion = self.expire(self.create_funcion())

        barrer_funciones_vencidas(self.pelicula.pk)

        other_funcion.refresh_from_db()
        self.assertTrue(other_funcion.funcion_activa)
        self.assertTrue(Entrada.objects.filter(pk=other_entry.pk).exists())
        funcion.refresh_from_db()
        self.assertFalse(funcion.funcion_activa)

    def test_sweep_is_idempotent(self):
        funcion = self.expire(self.create_funcion())
        self.create_entry(funcion)

        self.assertEqual(barrer_funciones_vencidas(self.pelicula.pk), 1)
        self.assertEqual(barrer_funciones_vencidas(self.pelicula.pk), 1)
        funcion.refresh_from_db()
        self.assertFalse(funcion.funcion_activa)

    def test_sweep_keeps_other_function_fields(self):
        funcion = self.create_funcion()
        funcion.distribucion = {'version': 4, 'filas': ['RA']}
        funcion.disponibilidad = 1
        funcion.entradas_compradas = 3
        funcion.save(update_fields=['distribucion', 'disponibilidad', 'entradas_compradas'])
        funcion = self.expire(funcion)
        funcion.refresh_from_db()
        inicio = funcion.inicio
        precio = funcion.precio_entrada

        barrer_funciones_vencidas(self.pelicula.pk)

        funcion.refresh_from_db()
        self.assertEqual(funcion.inicio, inicio)
        self.assertEqual(funcion.precio_entrada, precio)
        self.assertEqual(funcion.distribucion, {'version': 4, 'filas': ['RA']})
        self.assertEqual(funcion.disponibilidad, 1)
        self.assertEqual(funcion.entradas_compradas, 3)


class ListarFuncionesVendiblesTests(CompraDataMixin, TestCase):
    def test_lists_active_future_functions_in_start_order(self):
        sooner = self.create_funcion(start=timezone.now() + timedelta(days=1))
        later = self.create_funcion(start=timezone.now() + timedelta(days=2))

        funciones = list(listar_funciones_vendibles(self.pelicula.pk))

        self.assertEqual(funciones, [sooner, later])

    def test_excludes_inactive_and_expired_functions(self):
        inactive = self.create_funcion(activa=False)
        expired = self.expire(self.create_funcion())
        active = self.create_funcion()

        funciones = list(listar_funciones_vendibles(self.pelicula.pk))

        self.assertEqual(funciones, [active])
        self.assertNotIn(inactive, funciones)
        self.assertNotIn(expired, funciones)

    def test_queryset_includes_related_sala(self):
        funcion = self.create_funcion()

        funciones = list(listar_funciones_vendibles(self.pelicula.pk))

        self.assertEqual(funciones[0].sala.tipo_sala, '2D')
        self.assertEqual(funciones[0].sala.tipo_sonido, 'Dolby')


class PrepararCompraTests(CompraDataMixin, TestCase):
    def test_returns_movie_and_swept_list(self):
        expired = self.expire(self.create_funcion())
        self.create_entry(expired)
        active = self.create_funcion()

        pelicula, funciones = preparar_compra(self.pelicula.pk)

        self.assertEqual(pelicula, self.pelicula)
        self.assertEqual(list(funciones), [active])
        self.assertFalse(Entrada.objects.filter(funcion=expired).exists())

    def test_missing_movie_raises_404(self):
        with self.assertRaises(Http404):
            preparar_compra(999999)
