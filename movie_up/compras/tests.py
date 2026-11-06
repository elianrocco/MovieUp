from datetime import timedelta
from urllib.parse import urlencode

from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Cuenta
from entradas.models import Entrada
from entradas.services import crear_entrada
from funciones.models import Funcion
from peliculas.models import Pelicula
from salas.models import Sala

from .services import (
    barrer_funciones_vencidas,
    confirmar_compra,
    listar_funciones_vendibles,
    obtener_funcion_vendible,
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


class ObtenerFuncionVendibleTests(CompraDataMixin, TestCase):
    def test_returns_active_future_function_of_the_movie(self):
        funcion = self.create_funcion()

        resultado = obtener_funcion_vendible(self.pelicula.pk, funcion.pk)

        self.assertEqual(resultado, funcion)
        self.assertEqual(resultado.pelicula, self.pelicula)
        self.assertEqual(resultado.sala, self.sala)

    def test_missing_movie_raises_404(self):
        funcion = self.create_funcion()

        with self.assertRaises(Http404):
            obtener_funcion_vendible(999999, funcion.pk)

    def test_missing_function_raises_404(self):
        with self.assertRaises(Http404):
            obtener_funcion_vendible(self.pelicula.pk, 999999)

    def test_function_of_another_movie_raises_404(self):
        otra_pelicula = self.create_pelicula('Otra película')
        funcion = self.create_funcion(pelicula=otra_pelicula)

        with self.assertRaises(Http404):
            obtener_funcion_vendible(self.pelicula.pk, funcion.pk)

    def test_inactive_function_raises_404(self):
        funcion = self.create_funcion(activa=False)

        with self.assertRaises(Http404):
            obtener_funcion_vendible(self.pelicula.pk, funcion.pk)

    def test_expired_function_raises_404(self):
        funcion = self.expire(self.create_funcion())

        with self.assertRaises(Http404):
            obtener_funcion_vendible(self.pelicula.pk, funcion.pk)


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


class ConfirmarCompraTests(CompraDataMixin, TestCase):
    def assert_funcion_unchanged(self, funcion, filas, disponibilidad, compradas):
        funcion.refresh_from_db()
        self.assertEqual(funcion.distribucion['filas'], filas)
        self.assertEqual(funcion.disponibilidad, disponibilidad)
        self.assertEqual(funcion.entradas_compradas, compradas)

    def test_creates_one_entry_per_selected_seat(self):
        funcion = self.create_funcion()

        entradas = confirmar_compra(funcion.pk, self.cuenta.pk, ['A:1', 'A:2'], 'AA')

        self.assertEqual(len(entradas), 2)
        self.assert_funcion_unchanged(funcion, ['RR'], 0, 2)
        registradas = Entrada.objects.filter(funcion=funcion).order_by('n_asiento')
        self.assertEqual(
            [(e.l_fila, e.n_asiento, e.cuenta_id) for e in registradas],
            [('A', 1, self.cuenta.pk), ('A', 2, self.cuenta.pk)],
        )

    def test_empty_selection_is_rejected(self):
        funcion = self.create_funcion()

        with self.assertRaisesMessage(ValueError, 'al menos un asiento'):
            confirmar_compra(funcion.pk, self.cuenta.pk, [], 'AA')

        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())
        self.assert_funcion_unchanged(funcion, ['AA'], 2, 0)

    def test_malformed_cells_are_rejected(self):
        funcion = self.create_funcion()

        with self.assertRaisesMessage(ValueError, 'no es válida'):
            confirmar_compra(funcion.pk, self.cuenta.pk, ['A', 'A:2'], 'AA')

        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())

    def test_repeated_seats_are_rejected_and_cells_are_normalized(self):
        funcion = self.create_funcion()

        with self.assertRaisesMessage(ValueError, 'repetidos'):
            confirmar_compra(
                funcion.pk, self.cuenta.pk, ['A:1', ' a:1 ', 'A:2'], 'AA'
            )

        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())
        self.assert_funcion_unchanged(funcion, ['AA'], 2, 0)

    def test_stale_distribution_mark_is_rejected(self):
        funcion = self.create_funcion()

        with self.assertRaisesMessage(ValueError, 'distribución de la función cambió'):
            confirmar_compra(funcion.pk, self.cuenta.pk, ['A:1'], 'XX')

        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())

    def test_insufficient_availability_is_rejected(self):
        funcion = self.create_funcion()
        funcion.disponibilidad = 0
        funcion.save(update_fields=['disponibilidad'])

        with self.assertRaisesMessage(ValueError, 'suficientes entradas disponibles'):
            confirmar_compra(funcion.pk, self.cuenta.pk, ['A:1'], 'AA')

        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())

    def test_deactivated_function_rejects_the_batch(self):
        funcion = self.create_funcion()
        funcion.funcion_activa = False
        funcion.save(update_fields=['funcion_activa'])

        with self.assertRaisesMessage(ValueError, 'ya no está disponible'):
            confirmar_compra(
                funcion.pk, self.cuenta.pk, ['A:1', 'A:2'], 'AA'
            )

        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())

    def test_expired_function_rejects_the_batch(self):
        funcion = self.expire(self.create_funcion())

        with self.assertRaisesMessage(ValueError, 'ya no está disponible'):
            confirmar_compra(
                funcion.pk, self.cuenta.pk, ['A:1', 'A:2'], 'AA'
            )

        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())

    def test_seat_taken_after_page_load_rejects_the_batch(self):
        funcion = self.create_funcion()
        crear_entrada(funcion.pk, self.cuenta.pk, 1, 'A')

        with self.assertRaisesMessage(ValueError, 'distribución de la función cambió'):
            confirmar_compra(funcion.pk, self.cuenta.pk, ['A:2'], 'AA')

        self.assertEqual(Entrada.objects.filter(funcion=funcion).count(), 1)
        self.assert_funcion_unchanged(funcion, ['RA'], 1, 1)

    def test_batch_rolls_back_when_a_later_seat_is_occupied(self):
        funcion = self.create_funcion()
        funcion.distribucion = {'version': 4, 'filas': ['AAA']}
        funcion.disponibilidad = 3
        funcion.save(update_fields=['distribucion', 'disponibilidad'])
        crear_entrada(funcion.pk, self.cuenta.pk, 1, 'A')

        with self.assertRaisesMessage(ValueError, 'ya está reservado'):
            confirmar_compra(
                funcion.pk, self.cuenta.pk, ['A:2', 'A:1'], 'RAA'
            )

        self.assertEqual(Entrada.objects.filter(funcion=funcion).count(), 1)
        self.assert_funcion_unchanged(funcion, ['RAA'], 2, 1)


class CompraViewTests(CompraDataMixin, TestCase):
    def test_common_account_renders_purchase_page(self):
        self.create_funcion()
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compras/compra_pelicula.html')
        self.assertContains(response, self.pelicula.titulo)
        self.assertContains(response, 'Funciones disponibles')

    def test_visitor_is_sent_to_google_login_with_purchase_next(self):
        expected = (
            f'{reverse("google_login")}?'
            f'{urlencode({"process": "login", "next": f"/compras/{self.pelicula.pk}/"})}'
        )

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected)

    def test_staff_account_is_redirected_to_management(self):
        staff = Cuenta.objects.create_superuser(
            'staff@example.com', 'Staff', password='Strong-test-password-123'
        )
        self.client.force_login(staff)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertRedirects(response, '/gestion/', fetch_redirect_response=False)

    def test_missing_movie_returns_404(self):
        self.client.force_login(self.cuenta)

        response = self.client.get('/compras/999999/')

        self.assertEqual(response.status_code, 404)

    def test_hero_reuses_home_structure_without_buy_button(self):
        self.create_funcion()
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        for value in (
            'class="hero"',
            'hero__image',
            'hero__title',
            'hero__description',
            'hero__meta',
            'hero__buttons',
            self.pelicula.url_trailer,
        ):
            self.assertContains(response, value)
        self.assertNotContains(response, 'btn--secondary')

    def test_function_item_renders_all_fields(self):
        funcion = self.create_funcion()
        funcion.subtitulada = True
        funcion.disponibilidad = 7
        funcion.save(update_fields=['subtitulada', 'disponibilidad'])
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        for value in (
            timezone.localtime(funcion.inicio).strftime('%d/%m/%Y %H:%M'),
            '2D',
            'Dolby',
            'Español',
            'Sí',
            '$1500.00',
            '>7</span>',
            'Comprar entradas',
        ):
            self.assertContains(response, value)

    def test_empty_state_when_no_sellable_functions(self):
        self.create_funcion(activa=False)
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertContains(response, 'No hay funciones disponibles')
        self.assertNotContains(response, 'funcion-item')

    def test_sold_out_button_is_disabled_without_href(self):
        funcion = self.create_funcion()
        funcion.disponibilidad = 0
        funcion.save(update_fields=['disponibilidad'])
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertContains(response, 'Entradas agotadas')
        self.assertContains(response, 'disabled')
        self.assertNotContains(response, 'href="#"')

    def test_available_buy_button_links_to_its_function_selection(self):
        first = self.create_funcion()
        second = self.create_funcion(start=timezone.now() + timedelta(days=4))
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertContains(
            response,
            f'<a href="/compras/{self.pelicula.pk}/funciones/{first.pk}/" class="btn btn--buy">',
        )
        self.assertContains(
            response,
            f'<a href="/compras/{self.pelicula.pk}/funciones/{second.pk}/" class="btn btn--buy">',
        )

    def test_sold_out_button_does_not_link_to_selection(self):
        funcion = self.create_funcion()
        funcion.disponibilidad = 0
        funcion.save(update_fields=['disponibilidad'])
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertNotContains(response, f'/funciones/{funcion.pk}/')

    def test_purchase_page_loads_its_stylesheet(self):
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/')

        self.assertContains(response, 'css/compras.css')


class SeleccionAsientosViewTests(CompraDataMixin, TestCase):
    def test_common_account_renders_selection_page(self):
        funcion = self.create_funcion()
        url = f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        self.client.force_login(self.cuenta)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compras/seleccion_asientos.html')
        self.assertEqual(response.context['funcion'], funcion)
        self.assertEqual(response.context['pelicula'], self.pelicula)

    def test_visitor_is_sent_to_google_login_with_selection_next(self):
        funcion = self.create_funcion()
        url = f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        expected = (
            f'{reverse("google_login")}?'
            f'{urlencode({"process": "login", "next": url})}'
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected)

    def test_staff_account_is_redirected_to_management(self):
        funcion = self.create_funcion()
        staff = Cuenta.objects.create_superuser(
            'staff-selection@example.com', 'Staff', password='Strong-test-password-123'
        )
        self.client.force_login(staff)

        response = self.client.get(f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/')

        self.assertRedirects(response, '/gestion/', fetch_redirect_response=False)

    def test_missing_movie_returns_404(self):
        funcion = self.create_funcion()
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/999999/funciones/{funcion.pk}/')

        self.assertEqual(response.status_code, 404)

    def test_missing_function_returns_404(self):
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/funciones/999999/')

        self.assertEqual(response.status_code, 404)

    def test_function_of_another_movie_returns_404(self):
        otra_pelicula = self.create_pelicula('Otra película')
        funcion = self.create_funcion(pelicula=otra_pelicula)
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/')

        self.assertEqual(response.status_code, 404)

    def test_inactive_function_returns_404(self):
        funcion = self.create_funcion(activa=False)
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/')

        self.assertEqual(response.status_code, 404)

    def test_expired_function_returns_404(self):
        funcion = self.expire(self.create_funcion())
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/')

        self.assertEqual(response.status_code, 404)


class SeleccionCuadriculaTests(CompraDataMixin, TestCase):
    def render_selection(self, distribucion=None, disponibilidad=None):
        funcion = self.create_funcion()
        updates = []
        if distribucion is not None:
            funcion.distribucion = distribucion
            updates.append('distribucion')
        if disponibilidad is not None:
            funcion.disponibilidad = disponibilidad
            updates.append('disponibilidad')
        if updates:
            funcion.save(update_fields=updates)
        self.client.force_login(self.cuenta)
        return self.client.get(f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/')

    def test_grid_renders_cell_colors_from_distribution(self):
        response = self.render_selection({'version': 1, 'filas': ['APA']})

        self.assertContains(response, 'celda--asiento', count=2)
        self.assertContains(response, 'celda--pasillo', count=1)

    def test_available_cells_are_buttons_with_row_and_seat(self):
        response = self.render_selection({'version': 1, 'filas': ['APA']})

        self.assertContains(response, 'data-fila="A"', count=2)
        self.assertContains(response, 'data-asiento="1"')
        self.assertContains(response, 'data-asiento="2"')
        self.assertContains(response, 'title="Fila A, asiento 2"')

    def test_seat_ordinal_counts_reserved_cells(self):
        response = self.render_selection({'version': 1, 'filas': ['ARA']})

        self.assertContains(response, 'data-asiento="1"')
        self.assertContains(response, 'data-asiento="3"')
        self.assertNotContains(response, 'data-asiento="2"')
        self.assertContains(response, 'title="Reservado"')

    def test_sold_seat_renders_as_inert_reserved_span(self):
        response = self.render_selection({'version': 1, 'filas': ['RA']})

        self.assertContains(response, 'celda--reservado')
        self.assertContains(response, 'title="Reservado"')
        self.assertContains(response, 'data-asiento="2"')
        self.assertNotContains(response, 'data-asiento="1"')

    def test_second_row_uses_bijective_label(self):
        response = self.render_selection({'version': 1, 'filas': ['AA', 'AA']})

        self.assertContains(response, 'data-fila="A"', count=2)
        self.assertContains(response, 'data-fila="B"', count=2)

    def test_grid_uses_function_distribution_not_sala(self):
        funcion = self.create_funcion()
        self.sala.distribucion = {'version': 9, 'filas': ['RR']}
        self.sala.save(update_fields=['distribucion'])
        self.client.force_login(self.cuenta)

        response = self.client.get(f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/')

        self.assertContains(response, 'data-asiento="1"')
        self.assertContains(response, 'data-asiento="2"')
        self.assertNotContains(response, 'celda--reservado')

    def test_header_and_initial_summary_state(self):
        response = self.render_selection()

        self.assertContains(response, 'Elija sus asientos')
        self.assertContains(response, 'Cantidad de entradas')
        self.assertContains(response, 'data-contador>0')
        self.assertContains(response, 'data-total>$0.00')
        self.assertContains(response, 'data-precio="1500.00"')
        self.assertContains(response, 'name="distribucion" value="AA"')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'Confirmar compra')
        self.assertContains(response, 'data-confirmar disabled')
        self.assertContains(response, 'btn--sold-out')

    def test_sold_out_function_renders_without_selectable_seats(self):
        response = self.render_selection(
            distribucion={'version': 1, 'filas': ['RR']},
            disponibilidad=0,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'celda--reservado', count=2)
        self.assertNotContains(response, 'data-asiento')

    def test_selection_page_loads_its_stylesheet(self):
        response = self.render_selection()

        self.assertContains(response, 'css/compras.css')

    def test_selection_page_loads_its_script(self):
        response = self.render_selection()

        self.assertContains(response, 'compras/js/seleccion_asientos.js')
        self.assertContains(response, 'data-compra-grid')

    def test_view_renders_the_three_panels_in_order(self):
        response = self.render_selection()
        html = response.content.decode()

        self.assertEqual(html.count('panel--gold'), 1)
        self.assertEqual(html.count('panel panel--light'), 2)
        self.assertContains(response, 'panel--resumen')
        posiciones = [
            html.index('panel--gold'),
            html.index('Elija sus asientos'),
            html.index('panel panel--light'),
            html.index('class="datos"'),
            html.index('panel--resumen'),
            html.index('class="resumen"'),
        ]

        self.assertEqual(posiciones, sorted(posiciones))


class SeleccionDatosTests(CompraDataMixin, TestCase):
    def render_selection(self, subtitulada=True):
        funcion = self.create_funcion()
        funcion.subtitulada = subtitulada
        funcion.save(update_fields=['subtitulada'])
        self.client.force_login(self.cuenta)
        return funcion, self.client.get(
            f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        )

    def test_each_item_shows_its_label_above_the_value(self):
        funcion, response = self.render_selection()

        for label in (
            'Título',
            'Descripción',
            'Idioma',
            'Subtitulada',
            'Tipo de sala',
            'Tipo de sonido',
            'Inicio',
            'Fin',
            'Duración',
        ):
            self.assertContains(response, f'datos__etiqueta">{label}<')

        for value in (
            self.pelicula.titulo,
            self.pelicula.descripcion,
            'Español',
            'Sí',
            '2D',
            'Dolby',
            timezone.localtime(funcion.inicio).strftime('%d/%m/%Y %H:%M'),
            timezone.localtime(funcion.fin).strftime('%d/%m/%Y %H:%M'),
            '100 min',
        ):
            self.assertContains(response, value)

    def test_rows_appear_below_the_grid_in_spec_order(self):
        _, response = self.render_selection()
        html = response.content.decode()

        positions = [
            html.index('class="seat-grid"'),
            html.index('datos__etiqueta">Título<'),
            html.index('datos__etiqueta">Descripción<'),
            html.index('datos__etiqueta">Idioma<'),
            html.index('datos__etiqueta">Subtitulada<'),
            html.index('datos__etiqueta">Tipo de sala<'),
            html.index('datos__etiqueta">Tipo de sonido<'),
            html.index('datos__etiqueta">Inicio<'),
            html.index('datos__etiqueta">Fin<'),
            html.index('datos__etiqueta">Duración<'),
            html.index('class="resumen"'),
        ]

        self.assertEqual(positions, sorted(positions))

    def test_subtitulada_shows_no_when_the_function_is_not_subtitled(self):
        _, response = self.render_selection(subtitulada=False)

        self.assertContains(response, 'datos__valor">No<')
        self.assertNotContains(response, 'datos__valor">Sí<')

    def test_data_rows_and_summary_are_read_only(self):
        _, response = self.render_selection()
        html = response.content.decode()
        datos_html = html.split('class="datos"')[1].split('class="resumen"')[0]

        self.assertNotIn('<a', datos_html)
        self.assertNotIn('<button', datos_html)
        self.assertNotIn('<input', datos_html)
        self.assertContains(response, '<output class="resumen__valor" data-contador>')
        self.assertContains(response, '<output class="resumen__valor" data-total>')


class SeleccionPostTests(CompraDataMixin, TestCase):
    def test_post_without_session_is_sent_to_login_with_next(self):
        funcion = self.create_funcion()
        url = f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        expected = (
            f'{reverse("google_login")}?'
            f'{urlencode({"process": "login", "next": url})}'
        )

        response = self.client.post(url, {'celda': ['A:1'], 'distribucion': 'AA'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected)
        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())

    def test_valid_post_redirects_to_success_and_creates_the_entries(self):
        funcion = self.create_funcion()
        url = f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        self.client.force_login(self.cuenta)

        response = self.client.post(
            url, {'celda': ['A:1', 'A:2'], 'distribucion': 'AA'}
        )

        self.assertRedirects(
            response, f'{url}?compra=exitosa', fetch_redirect_response=False
        )
        self.assertEqual(Entrada.objects.filter(funcion=funcion).count(), 2)
        funcion.refresh_from_db()
        self.assertEqual(funcion.disponibilidad, 0)
        self.assertEqual(funcion.distribucion['filas'], ['RR'])

    def test_post_without_cells_shows_error_and_creates_nothing(self):
        funcion = self.create_funcion()
        url = f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        self.client.force_login(self.cuenta)

        response = self.client.post(url, {'celda': [], 'distribucion': 'AA'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="alert"')
        self.assertContains(response, 'Debe seleccionar al menos un asiento')
        self.assertContains(response, 'Elija sus asientos')
        self.assertFalse(Entrada.objects.filter(funcion=funcion).exists())
        funcion.refresh_from_db()
        self.assertEqual(funcion.disponibilidad, 2)

    def test_post_with_occupied_seat_shows_error_and_creates_nothing(self):
        funcion = self.create_funcion()
        funcion.distribucion = {'version': 4, 'filas': ['AAA']}
        funcion.disponibilidad = 3
        funcion.save(update_fields=['distribucion', 'disponibilidad'])
        crear_entrada(funcion.pk, self.cuenta.pk, 1, 'A')
        url = f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        self.client.force_login(self.cuenta)

        response = self.client.post(
            url, {'celda': ['A:2', 'A:1'], 'distribucion': 'RAA'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ya está reservado')
        self.assertEqual(Entrada.objects.filter(funcion=funcion).count(), 1)
        funcion.refresh_from_db()
        self.assertEqual(funcion.disponibilidad, 2)
        self.assertEqual(funcion.distribucion['filas'], ['RAA'])

    def test_post_with_stale_distribution_shows_error_and_reloads_the_grid(self):
        funcion = self.create_funcion()
        crear_entrada(funcion.pk, self.cuenta.pk, 1, 'A')
        url = f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        self.client.force_login(self.cuenta)

        response = self.client.post(url, {'celda': ['A:2'], 'distribucion': 'AA'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La distribución de la función cambió')
        self.assertEqual(Entrada.objects.filter(funcion=funcion).count(), 1)
        self.assertContains(response, 'title="Reservado"')


class CompraExitosaTests(CompraDataMixin, TestCase):
    def success_url(self, funcion):
        return f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/?compra=exitosa'

    def test_success_page_shows_the_message_and_the_entries_button(self):
        funcion = self.create_funcion()
        self.client.force_login(self.cuenta)

        response = self.client.get(self.success_url(funcion))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compras/compra_exitosa.html')
        self.assertContains(
            response, 'Compra realizada con éxito, puede ver sus entradas en'
        )
        self.assertContains(response, 'href="/entradas/"')
        self.assertContains(response, '>Mis entradas</a>')

    def test_success_page_has_no_grid_form_or_data(self):
        funcion = self.create_funcion()
        self.client.force_login(self.cuenta)

        response = self.client.get(self.success_url(funcion))

        self.assertNotContains(response, 'seat-grid')
        self.assertNotContains(response, 'Elija sus asientos')
        self.assertNotContains(response, 'data-compra-form')
        self.assertNotContains(response, 'datos__etiqueta')

    def test_url_without_the_success_param_still_shows_the_selection_grid(self):
        funcion = self.create_funcion()
        self.client.force_login(self.cuenta)

        response = self.client.get(
            f'/compras/{self.pelicula.pk}/funciones/{funcion.pk}/'
        )

        self.assertTemplateUsed(response, 'compras/seleccion_asientos.html')
        self.assertContains(response, 'Elija sus asientos')

    def test_visitor_on_the_success_url_is_sent_to_login(self):
        funcion = self.create_funcion()
        url = self.success_url(funcion)
        expected = (
            f'{reverse("google_login")}?'
            f'{urlencode({"process": "login", "next": url})}'
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected)

    def test_success_button_is_gold_and_below_the_message(self):
        funcion = self.create_funcion()
        self.client.force_login(self.cuenta)

        response = self.client.get(self.success_url(funcion))
        html = response.content.decode()

        self.assertContains(response, 'btn btn--gold')
        self.assertNotContains(response, 'btn--buy')
        self.assertLess(html.index('exito__mensaje'), html.index('btn btn--gold'))
