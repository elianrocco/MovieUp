from datetime import timedelta
from decimal import Decimal

from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from peliculas.models import Pelicula
from salas.models import Sala

from .models import Funcion
from .services import (
    _ensure_no_overlap,
    create_funcion,
    delete_funcion,
    get_funcion,
    list_funciones,
    update_funcion,
)


class FuncionTestDataMixin:
    def setUp(self):
        self.pelicula = self.create_pelicula('Película base', 120)
        self.sala = self.create_sala('Sala base')

    def create_pelicula(self, title, duration):
        return Pelicula.objects.create(
            titulo=title,
            imagen_portada='imgs/test.jpg',
            genero='Drama',
            duracion_minutos=duration,
            descripcion='Descripción de prueba',
            clasificacion='ATP',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )

    def create_sala(self, name):
        return Sala.objects.create(
            nombre=name,
            tipo_sala='2D',
            tipo_sonido='Dolby',
            distribucion={'version': 4, 'filas': ['AARPP', 'PAAAR']},
            capacidad=5,
        )

    def future_start(self, days=2):
        return (timezone.localtime(timezone.now()) + timedelta(days=days)).replace(
            second=0, microsecond=0
        )

    def valid_data(self, **overrides):
        data = {
            'pelicula': str(self.pelicula.pk),
            'sala': str(self.sala.pk),
            'inicio': self.future_start(),
            'idioma': 'Español',
            'subtitulada': 'false',
            'funcion_activa': 'true',
            'precio_entrada': '1500.00',
        }
        data.update(overrides)
        return data


class FuncionReadServiceTests(FuncionTestDataMixin, TestCase):
    def test_list_funciones_orders_by_start(self):
        later = self.future_start(days=3)
        earlier = self.future_start(days=2)
        second_movie = self.create_pelicula('Película posterior', 90)

        later_funcion = create_funcion(self.valid_data(inicio=later))
        earlier_funcion = create_funcion(
            self.valid_data(inicio=earlier, pelicula=second_movie)
        )

        self.assertEqual(list(list_funciones()), [earlier_funcion, later_funcion])

    def test_list_funciones_selects_related_objects(self):
        funcion = create_funcion(self.valid_data())

        fetched = list_funciones().get(pk=funcion.pk)

        self.assertEqual(fetched.pelicula, self.pelicula)
        self.assertEqual(fetched.sala, self.sala)

    def test_get_funcion_returns_matching_record(self):
        funcion = create_funcion(self.valid_data())

        self.assertEqual(get_funcion(funcion.pk), funcion)

    def test_get_funcion_raises_http_404_for_unknown_id(self):
        with self.assertRaises(Http404):
            get_funcion(999)


class FuncionCreateServiceTests(FuncionTestDataMixin, TestCase):
    def test_create_derives_end_availability_and_purchase_count(self):
        start = self.future_start()
        funcion = create_funcion(
            self.valid_data(
                inicio=start,
                fin=self.future_start(days=20),
                disponibilidad=999,
                entradas_compradas=12,
                distribucion={'version': 99, 'filas': ['P']},
            )
        )

        self.assertEqual(funcion.fin, start + timedelta(minutes=120))
        self.assertEqual(funcion.disponibilidad, 5)
        self.assertEqual(funcion.precio_entrada, Decimal('1500.00'))
        self.assertEqual(funcion.entradas_compradas, 0)
        self.assertEqual(
            funcion.distribucion,
            {'version': 4, 'filas': ['AARPP', 'PAAAR']},
        )

    def test_create_stores_a_distribution_snapshot(self):
        funcion = create_funcion(self.valid_data())
        self.sala.distribucion['filas'][0] = 'PPPPP'
        self.sala.save(update_fields=['distribucion'])

        funcion.refresh_from_db()

        self.assertEqual(
            funcion.distribucion,
            {'version': 4, 'filas': ['AARPP', 'PAAAR']},
        )

    def test_create_accepts_zero_price(self):
        funcion = create_funcion(self.valid_data(precio_entrada='0'))

        self.assertEqual(funcion.precio_entrada, Decimal('0.00'))

    def test_create_rejects_start_in_the_past(self):
        past_start = timezone.localtime(timezone.now()) - timedelta(minutes=5)

        with self.assertRaisesRegex(ValueError, 'anterior al momento actual'):
            create_funcion(self.valid_data(inicio=past_start))

        self.assertEqual(Funcion.objects.count(), 0)

    def test_create_requires_all_user_supplied_fields(self):
        for field in (
            'pelicula', 'sala', 'inicio', 'idioma', 'subtitulada',
            'funcion_activa', 'precio_entrada',
        ):
            data = self.valid_data()
            data.pop(field)
            with self.subTest(field=field), self.assertRaises(ValueError):
                create_funcion(data)

        self.assertEqual(Funcion.objects.count(), 0)

    def test_create_rejects_blank_or_overlong_language(self):
        for language in ('  ', 'x' * 46):
            with self.subTest(language_length=len(language)), self.assertRaises(
                ValueError
            ):
                create_funcion(self.valid_data(idioma=language))

    def test_create_rejects_invalid_boolean_values(self):
        for field in ('subtitulada', 'funcion_activa'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                create_funcion(self.valid_data(**{field: 'yes'}))

    def test_create_rejects_negative_price(self):
        with self.assertRaisesRegex(ValueError, 'no puede ser negativo'):
            create_funcion(self.valid_data(precio_entrada='-0.01'))

        self.assertEqual(Funcion.objects.count(), 0)

    def test_create_rejects_price_with_more_than_two_decimals(self):
        with self.assertRaisesRegex(ValueError, 'dos decimales'):
            create_funcion(self.valid_data(precio_entrada='1.001'))

    def test_create_rejects_price_above_decimal_field_limit(self):
        with self.assertRaisesRegex(ValueError, 'máximo permitido'):
            create_funcion(self.valid_data(precio_entrada='100000000.00'))

    def test_create_rejects_non_numeric_price(self):
        with self.assertRaisesRegex(ValueError, 'número válido'):
            create_funcion(self.valid_data(precio_entrada='NaN'))

    def test_create_rejects_missing_related_records(self):
        for field, value in (('pelicula', '999'), ('sala', '999')):
            with self.subTest(field=field), self.assertRaises(ValueError):
                create_funcion(self.valid_data(**{field: value}))

    def test_create_rejects_non_integer_related_ids(self):
        for field in ('pelicula', 'sala'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                create_funcion(self.valid_data(**{field: 1.5}))

    def test_create_rejects_invalid_room_distribution(self):
        self.sala.distribucion = {'version': 1, 'filas': ['AAX']}
        self.sala.save(update_fields=['distribucion'])

        with self.assertRaisesRegex(ValueError, 'no permitidos'):
            create_funcion(self.valid_data())

        self.assertEqual(Funcion.objects.count(), 0)

    def test_create_rejects_overlapping_function_in_same_room(self):
        start = self.future_start()
        create_funcion(self.valid_data(inicio=start, funcion_activa='false'))

        with self.assertRaisesRegex(ValueError, 'otra función en ese horario'):
            create_funcion(
                self.valid_data(inicio=start + timedelta(seconds=1))
            )

        self.assertEqual(Funcion.objects.count(), 1)

    def test_create_allows_functions_that_touch_at_exact_boundary(self):
        start = self.future_start()
        create_funcion(self.valid_data(inicio=start))

        next_funcion = create_funcion(
            self.valid_data(inicio=start + timedelta(minutes=120))
        )

        self.assertEqual(Funcion.objects.count(), 2)
        self.assertEqual(next_funcion.inicio, start + timedelta(minutes=120))

    def test_inactive_function_still_blocks_room_overlap(self):
        start = self.future_start()
        create_funcion(self.valid_data(inicio=start, funcion_activa='false'))

        with self.assertRaises(ValueError):
            create_funcion(self.valid_data(inicio=start))

    def test_create_allows_same_time_in_a_different_room(self):
        start = self.future_start()
        create_funcion(self.valid_data(inicio=start))
        other_room = self.create_sala('Sala B')

        second = create_funcion(
            self.valid_data(inicio=start, sala=str(other_room.pk))
        )

        self.assertEqual(second.sala, other_room)


class FuncionOverlapHelperTests(FuncionTestDataMixin, TestCase):
    def test_overlap_helper_can_exclude_the_current_function(self):
        start = self.future_start()
        funcion = create_funcion(self.valid_data(inicio=start))

        _ensure_no_overlap(
            self.sala.pk,
            start,
            start + timedelta(minutes=120),
            exclude_pk=funcion.pk,
        )


class FuncionUpdateServiceTests(FuncionTestDataMixin, TestCase):
    def test_update_applies_partial_fields_and_preserves_derived_values(self):
        funcion = create_funcion(self.valid_data())
        original_end = funcion.fin
        original_distribution = funcion.distribucion.copy()

        updated = update_funcion(funcion.pk, {'idioma': '  Inglés  '})

        self.assertEqual(updated.idioma, 'Inglés')
        self.assertEqual(updated.fin, original_end)
        self.assertEqual(updated.distribucion, original_distribution)
        self.assertEqual(updated.disponibilidad, 5)

    def test_update_allows_edit_when_unchanged_start_is_in_the_past(self):
        funcion = create_funcion(self.valid_data())
        past_start = (timezone.localtime(timezone.now()) - timedelta(hours=1)).replace(
            second=0, microsecond=0
        )
        funcion.inicio = past_start
        funcion.fin = past_start + timedelta(minutes=120)
        funcion.funcion_activa = False
        funcion.save(update_fields=['inicio', 'fin', 'funcion_activa'])

        updated = update_funcion(
            funcion.pk,
            {'inicio': past_start.strftime('%Y-%m-%dT%H:%M'), 'idioma': 'Inglés'},
        )

        self.assertEqual(updated.inicio, past_start)
        self.assertEqual(updated.idioma, 'Inglés')

    def test_update_rejects_a_changed_start_in_the_past(self):
        funcion = create_funcion(self.valid_data())
        past_start = timezone.localtime(timezone.now()) - timedelta(hours=1)

        with self.assertRaisesRegex(ValueError, 'anterior al momento actual'):
            update_funcion(funcion.pk, {'inicio': past_start})

        funcion.refresh_from_db()
        self.assertGreater(funcion.inicio, timezone.now())

    def test_update_recalculates_end_when_start_changes(self):
        funcion = create_funcion(self.valid_data())
        new_start = self.future_start(days=4)

        updated = update_funcion(funcion.pk, {'inicio': new_start})

        self.assertEqual(updated.inicio, new_start)
        self.assertEqual(updated.fin, new_start + timedelta(minutes=120))

    def test_update_recalculates_end_when_movie_changes(self):
        funcion = create_funcion(self.valid_data())
        longer_movie = self.create_pelicula('Película larga', 180)

        updated = update_funcion(funcion.pk, {'pelicula': str(longer_movie.pk)})

        self.assertEqual(updated.pelicula, longer_movie)
        self.assertEqual(updated.fin, updated.inicio + timedelta(minutes=180))

    def test_update_replaces_distribution_when_room_changes(self):
        funcion = create_funcion(self.valid_data())
        new_room = Sala.objects.create(
            nombre='Sala nueva',
            tipo_sala='3D',
            tipo_sonido='Dolby',
            distribucion={'version': 7, 'filas': ['AAR', 'PPP']},
            capacidad=3,
        )

        updated = update_funcion(funcion.pk, {'sala': str(new_room.pk)})

        self.assertEqual(updated.sala, new_room)
        self.assertEqual(updated.distribucion, {'version': 7, 'filas': ['AAR', 'PPP']})
        self.assertEqual(updated.disponibilidad, 2)

    def test_update_does_not_refresh_snapshot_when_room_is_unchanged(self):
        funcion = create_funcion(self.valid_data())
        self.sala.distribucion = {'version': 5, 'filas': ['A']}
        self.sala.save(update_fields=['distribucion'])

        updated = update_funcion(funcion.pk, {'sala': str(self.sala.pk)})

        self.assertEqual(updated.distribucion, {'version': 4, 'filas': ['AARPP', 'PAAAR']})
        self.assertEqual(updated.disponibilidad, 5)

    def test_update_rejects_overlap_with_another_function(self):
        start = self.future_start()
        funcion = create_funcion(self.valid_data(inicio=start))
        other_room = self.create_sala('Sala B')
        other = create_funcion(
            self.valid_data(sala=str(other_room.pk), inicio=start + timedelta(days=1))
        )

        with self.assertRaisesRegex(ValueError, 'otra función en ese horario'):
            update_funcion(other.pk, {'sala': str(self.sala.pk), 'inicio': start})

        other.refresh_from_db()
        self.assertEqual(other.sala, other_room)

    def test_update_excludes_itself_from_overlap_check(self):
        funcion = create_funcion(self.valid_data())

        updated = update_funcion(funcion.pk, {'idioma': 'Portugués'})

        self.assertEqual(updated.idioma, 'Portugués')

    def test_update_can_set_false_and_zero_values(self):
        funcion = create_funcion(self.valid_data())

        updated = update_funcion(
            funcion.pk,
            {'subtitulada': 'false', 'funcion_activa': 'false', 'precio_entrada': '0'},
        )

        self.assertFalse(updated.subtitulada)
        self.assertFalse(updated.funcion_activa)
        self.assertEqual(updated.precio_entrada, Decimal('0.00'))

    def test_update_rejects_when_entries_were_purchased(self):
        funcion = create_funcion(self.valid_data())
        Funcion.objects.filter(pk=funcion.pk).update(entradas_compradas=1)

        with self.assertRaisesRegex(ValueError, 'entradas compradas'):
            update_funcion(funcion.pk, {'idioma': 'Inglés'})

        funcion.refresh_from_db()
        self.assertEqual(funcion.idioma, 'Español')

    def test_update_rejects_activating_an_expired_function(self):
        funcion = create_funcion(self.valid_data(funcion_activa='false'))
        past_start = timezone.localtime(timezone.now()) - timedelta(hours=3)
        Funcion.objects.filter(pk=funcion.pk).update(
            inicio=past_start,
            fin=past_start + timedelta(minutes=120),
            funcion_activa=False,
        )

        with self.assertRaisesRegex(ValueError, 'fin ya pasó'):
            update_funcion(funcion.pk, {'funcion_activa': 'true'})

        funcion.refresh_from_db()
        self.assertFalse(funcion.funcion_activa)

    def test_update_allows_other_fields_when_expired_active_state_is_unchanged(self):
        funcion = create_funcion(self.valid_data(funcion_activa='true'))
        past_start = timezone.localtime(timezone.now()) - timedelta(hours=3)
        Funcion.objects.filter(pk=funcion.pk).update(
            inicio=past_start,
            fin=past_start + timedelta(minutes=120),
            funcion_activa=True,
        )

        updated = update_funcion(
            funcion.pk,
            {'funcion_activa': 'true', 'idioma': 'Inglés'},
        )

        self.assertTrue(updated.funcion_activa)
        self.assertEqual(updated.idioma, 'Inglés')

    def test_update_raises_http_404_for_unknown_id(self):
        with self.assertRaises(Http404):
            update_funcion(999, {'idioma': 'Inglés'})


class FuncionDeleteServiceTests(FuncionTestDataMixin, TestCase):
    def test_delete_removes_only_the_function(self):
        funcion = create_funcion(self.valid_data())

        delete_funcion(funcion.pk)

        self.assertFalse(Funcion.objects.filter(pk=funcion.pk).exists())
        self.assertTrue(Pelicula.objects.filter(pk=self.pelicula.pk).exists())
        self.assertTrue(Sala.objects.filter(pk=self.sala.pk).exists())

    def test_delete_rejects_function_with_purchased_entries(self):
        funcion = create_funcion(self.valid_data())
        Funcion.objects.filter(pk=funcion.pk).update(entradas_compradas=1)

        with self.assertRaisesRegex(ValueError, 'entradas compradas'):
            delete_funcion(funcion.pk)

        self.assertTrue(Funcion.objects.filter(pk=funcion.pk).exists())

    def test_delete_raises_http_404_for_unknown_id(self):
        with self.assertRaises(Http404):
            delete_funcion(999)


class FuncionViewTests(FuncionTestDataMixin, TestCase):
    def form_data(self, **overrides):
        data = self.valid_data()
        data['inicio'] = self.future_start().strftime('%Y-%m-%dT%H:%M')
        data.update(overrides)
        return data

    def test_list_view_shows_summary_for_all_functions(self):
        create_funcion(self.valid_data())
        create_funcion(
            self.valid_data(
                inicio=self.future_start(days=4),
                funcion_activa='false',
                precio_entrada='0',
            )
        )

        response = self.client.get(reverse('funciones:funcion_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funciones/list.html')
        for value in (
            'Película base', 'Sala base', 'Activa', 'Disponibilidad',
            'Precio', '1500.00',
        ):
            self.assertContains(response, value)
        self.assertContains(response, 'Inactiva')

    def test_list_view_shows_empty_state(self):
        response = self.client.get(reverse('funciones:funcion_list'))

        self.assertContains(response, 'No hay funciones registradas.')

    def test_detail_view_shows_names_fields_and_read_only_grid(self):
        funcion = create_funcion(self.valid_data())

        response = self.client.get(
            reverse('funciones:funcion_detail', args=[funcion.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funciones/detail.html')
        self.assertContains(response, 'Película base')
        self.assertContains(response, 'Sala base')
        self.assertContains(response, 'Español')
        self.assertContains(response, 'Entradas compradas')
        self.assertContains(response, 'Versión de distribución')
        self.assertContains(response, 'celda--pasillo')
        self.assertContains(response, 'celda--asiento')
        self.assertContains(response, 'celda--reservado')
        self.assertNotContains(response, 'data-seat-grid')
        self.assertNotContains(response, 'data-row=')
        self.assertNotContains(response, 'pelicula_id')
        self.assertNotContains(response, 'sala_id')

    def test_detail_view_returns_404_for_unknown_id(self):
        response = self.client.get(
            reverse('funciones:funcion_detail', args=[999])
        )

        self.assertEqual(response.status_code, 404)

    def test_create_form_has_named_dropdowns_and_browser_constraints(self):
        response = self.client.get(reverse('funciones:funcion_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<option value="{self.pelicula.pk}"', html=False)
        self.assertContains(response, 'Película base')
        self.assertContains(response, f'<option value="{self.sala.pk}"', html=False)
        self.assertContains(response, 'Sala base')
        self.assertContains(response, 'type="datetime-local"', html=False)
        self.assertContains(response, 'min="', html=False)
        self.assertContains(response, 'name="idioma"', html=False)
        self.assertContains(response, 'maxlength="45"', html=False)
        self.assertContains(response, 'min="0"', html=False)

    def test_create_view_persists_function_and_redirects_to_list(self):
        response = self.client.post(
            reverse('funciones:funcion_create'),
            data=self.form_data(),
        )

        self.assertRedirects(response, reverse('funciones:funcion_list'))
        funcion = Funcion.objects.get()
        self.assertEqual(funcion.pelicula, self.pelicula)
        self.assertEqual(funcion.sala, self.sala)
        self.assertEqual(funcion.disponibilidad, 5)
        self.assertEqual(funcion.entradas_compradas, 0)

    def test_create_view_rerenders_form_with_service_error(self):
        data = self.form_data()
        create_funcion(data)

        response = self.client.post(
            reverse('funciones:funcion_create'),
            data=data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funciones/form.html')
        self.assertContains(response, 'otra función en ese horario')
        self.assertEqual(Funcion.objects.count(), 1)

    def test_update_form_is_prefilled_with_current_values(self):
        funcion = create_funcion(self.valid_data())

        response = self.client.get(
            reverse('funciones:funcion_update', args=[funcion.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form_values']['pelicula'], str(self.pelicula.pk))
        self.assertEqual(response.context['form_values']['sala'], str(self.sala.pk))
        self.assertEqual(response.context['form_values']['idioma'], 'Español')
        self.assertEqual(response.context['form_values']['funcion_activa'], 'true')
        self.assertContains(response, 'Fin calculado actual')

    def test_update_view_applies_partial_fields_and_redirects_to_detail(self):
        funcion = create_funcion(self.valid_data())
        original_end = funcion.fin

        response = self.client.post(
            reverse('funciones:funcion_update', args=[funcion.pk]),
            data={'idioma': 'Inglés'},
        )

        self.assertRedirects(
            response,
            reverse('funciones:funcion_detail', args=[funcion.pk]),
        )
        funcion.refresh_from_db()
        self.assertEqual(funcion.idioma, 'Inglés')
        self.assertEqual(funcion.fin, original_end)

    def test_update_view_rerenders_form_when_service_rejects(self):
        funcion = create_funcion(self.valid_data())
        past_start = timezone.localtime(timezone.now()) - timedelta(hours=1)

        response = self.client.post(
            reverse('funciones:funcion_update', args=[funcion.pk]),
            data={'inicio': past_start.strftime('%Y-%m-%dT%H:%M')},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funciones/form.html')
        self.assertContains(response, 'anterior al momento actual')

    def test_update_view_returns_404_for_unknown_id(self):
        response = self.client.get(
            reverse('funciones:funcion_update', args=[999])
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_view_confirms_then_deletes_only_function(self):
        funcion = create_funcion(self.valid_data())
        confirm = self.client.get(
            reverse('funciones:funcion_delete', args=[funcion.pk])
        )
        response = self.client.post(
            reverse('funciones:funcion_delete', args=[funcion.pk])
        )

        self.assertEqual(confirm.status_code, 200)
        self.assertTemplateUsed(confirm, 'funciones/confirm_delete.html')
        self.assertRedirects(response, reverse('funciones:funcion_list'))
        self.assertFalse(Funcion.objects.filter(pk=funcion.pk).exists())
        self.assertTrue(Pelicula.objects.filter(pk=self.pelicula.pk).exists())
        self.assertTrue(Sala.objects.filter(pk=self.sala.pk).exists())

    def test_delete_view_shows_service_error_for_purchased_entries(self):
        funcion = create_funcion(self.valid_data())
        Funcion.objects.filter(pk=funcion.pk).update(entradas_compradas=1)

        response = self.client.post(
            reverse('funciones:funcion_delete', args=[funcion.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funciones/confirm_delete.html')
        self.assertContains(response, 'entradas compradas')
        self.assertTrue(Funcion.objects.filter(pk=funcion.pk).exists())

    def test_delete_view_returns_404_for_unknown_id(self):
        response = self.client.get(
            reverse('funciones:funcion_delete', args=[999])
        )

        self.assertEqual(response.status_code, 404)
