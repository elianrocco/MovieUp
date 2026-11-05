from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.http import Http404
from django.test import RequestFactory, SimpleTestCase, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Cuenta
from funciones.models import Funcion
from peliculas.models import Pelicula
from salas.models import Sala

from .admin import EntradaAdmin
from .models import Entrada
from .services import (
    CODE_ALPHABET,
    _indice_fila,
    crear_entrada,
    eliminar_entrada,
    eliminar_entradas_por_finalizacion,
    etiqueta_fila,
    listar_entradas,
    obtener_entrada,
    validar_entrada,
)


class EtiquetaFilaTests(SimpleTestCase):
    def test_row_numbers_use_bijective_base_26_labels(self):
        self.assertEqual(etiqueta_fila(1), 'A')
        self.assertEqual(etiqueta_fila(26), 'Z')
        self.assertEqual(etiqueta_fila(27), 'AA')

        self.assertEqual(_indice_fila('A'), 0)
        self.assertEqual(_indice_fila('Z'), 25)
        self.assertEqual(_indice_fila('AA'), 26)

    def test_invalid_row_labels_are_rejected(self):
        for label in ('', 'A1', 'É', 'ABCDE', None):
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, 'etiqueta'):
                _indice_fila(label)

    def test_invalid_row_numbers_are_rejected(self):
        for number in (0, -1, True, '1'):
            with self.subTest(number=number), self.assertRaisesRegex(ValueError, 'número'):
                etiqueta_fila(number)


class EntradaDataMixin:
    def setUp(self):
        self.cuenta = Cuenta.objects.create_user('customer@example.com', 'Customer')
        self.pelicula = Pelicula.objects.create(
            titulo='Película de prueba',
            imagen_portada='imgs/test.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Descripción de prueba',
            clasificacion='ATP',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )
        self.funcion = self.create_funcion(['APA'])

    def create_funcion(self, rows, start=None):
        if start is None:
            start = timezone.now() + timedelta(days=3)
        room_distribution = {'version': 7, 'filas': list(rows)}
        sala = Sala.objects.create(
            nombre=f'Sala {Sala.objects.count() + 1}',
            distribucion=room_distribution,
            tipo_sala='2D',
            tipo_sonido='Dolby',
            capacidad=sum(cell in {'A', 'R'} for row in rows for cell in row),
        )
        return Funcion.objects.create(
            funcion_activa=True,
            inicio=start,
            fin=start + timedelta(minutes=self.pelicula.duracion_minutos),
            idioma='Español',
            subtitulada=False,
            distribucion=room_distribution,
            disponibilidad=sum(row.count('A') for row in rows),
            precio_entrada='1500.00',
            pelicula=self.pelicula,
            sala=sala,
            entradas_compradas=sum(row.count('R') for row in rows),
        )

    def create(
        self,
        seat_number=1,
        row='A',
        function=None,
        account=None,
        function_id=None,
        account_id=None,
    ):
        return crear_entrada(
            function_id if function_id is not None else (
                function.pk if function is not None else self.funcion.pk
            ),
            account_id if account_id is not None else (
                account.pk if account is not None else self.cuenta.pk
            ),
            seat_number,
            row,
        )


class CrearEntradaServiceTests(EntradaDataMixin, TestCase):
    def test_entry_has_only_the_declared_persisted_fields(self):
        field_names = [field.name for field in Entrada._meta.local_fields]

        self.assertEqual(
            field_names,
            ['id', 'funcion', 'cuenta', 'codigo', 'l_fila', 'n_asiento', 'activa'],
        )

    def assert_creation_rejected_without_changes(self, **kwargs):
        self.funcion.refresh_from_db()
        previous = (
            self.funcion.distribucion,
            self.funcion.disponibilidad,
            self.funcion.entradas_compradas,
            Entrada.objects.count(),
        )

        with self.assertRaises(ValueError):
            self.create(**kwargs)

        self.funcion.refresh_from_db()
        self.assertEqual(
            (
                self.funcion.distribucion,
                self.funcion.disponibilidad,
                self.funcion.entradas_compradas,
                Entrada.objects.count(),
            ),
            previous,
        )

    def test_creates_entry_and_updates_function_seat_without_counting_aisles(self):
        first = self.create(seat_number=1)
        second = self.create(seat_number=2)

        self.assertEqual(first.l_fila, 'A')
        self.assertEqual(first.n_asiento, 1)
        self.assertTrue(first.activa)
        self.assertEqual(second.n_asiento, 2)

        self.funcion.refresh_from_db()
        self.assertEqual(self.funcion.distribucion, {'version': 7, 'filas': ['RPR']})
        self.assertEqual(self.funcion.disponibilidad, 0)
        self.assertEqual(self.funcion.entradas_compradas, 2)

    def test_creates_entry_for_labelled_second_row(self):
        self.funcion = self.create_funcion(['A', 'A'])

        entry = self.create(row='b')

        self.assertEqual(entry.l_fila, 'B')
        self.funcion.refresh_from_db()
        self.assertEqual(self.funcion.distribucion['filas'], ['A', 'R'])

    def test_rejects_missing_function_account_and_row(self):
        with self.assertRaisesRegex(ValueError, 'función'):
            self.create(function_id=999999)
        with self.assertRaisesRegex(ValueError, 'cuenta'):
            self.create(account_id=999999)
        self.assert_creation_rejected_without_changes(row='B')
        self.assert_creation_rejected_without_changes(row='A1')

    def test_rejects_invalid_or_out_of_range_seat_number(self):
        self.assert_creation_rejected_without_changes(seat_number=0)
        self.assert_creation_rejected_without_changes(seat_number=3)
        self.assert_creation_rejected_without_changes(seat_number=True)

    def test_rejects_reserved_seat_without_mutating_function(self):
        self.funcion = self.create_funcion(['RAP'])

        self.assert_creation_rejected_without_changes(seat_number=1)

    def test_rejects_entry_for_finished_function(self):
        self.funcion.fin = timezone.now() - timedelta(seconds=1)
        self.funcion.save(update_fields=['fin'])

        self.assert_creation_rejected_without_changes()

    def test_rejects_nonexistent_account_without_mutating_function(self):
        self.assert_creation_rejected_without_changes(account_id=999999)

    def test_generated_codes_are_unique_length_12_and_use_unambiguous_alphabet(self):
        first = self.create(seat_number=1)
        second = self.create(seat_number=2)

        self.assertEqual(len(first.codigo), 12)
        self.assertTrue(set(first.codigo) <= set(CODE_ALPHABET))
        self.assertEqual(first.codigo, first.codigo.upper())
        self.assertNotEqual(first.codigo, second.codigo)

    def test_database_rejects_duplicate_code(self):
        first = self.create(seat_number=1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Entrada.objects.create(
                    funcion=self.funcion,
                    cuenta=self.cuenta,
                    codigo=first.codigo,
                    l_fila='A',
                    n_asiento=2,
                )

        self.assertEqual(Entrada.objects.count(), 1)

    def test_code_collision_rejects_creation_and_rolls_back_function(self):
        first = self.create(seat_number=1)
        self.funcion.refresh_from_db()
        previous = (
            self.funcion.distribucion,
            self.funcion.disponibilidad,
            self.funcion.entradas_compradas,
        )

        with patch('entradas.services._generar_codigo', return_value=first.codigo):
            with self.assertRaisesRegex(ValueError, 'código'):
                self.create(seat_number=2)

        self.funcion.refresh_from_db()
        self.assertEqual(
            (
                self.funcion.distribucion,
                self.funcion.disponibilidad,
                self.funcion.entradas_compradas,
            ),
            previous,
        )
        self.assertEqual(Entrada.objects.count(), 1)


class CrearEntradaConcurrencyTests(EntradaDataMixin, TransactionTestCase):
    def test_concurrent_creation_for_same_seat_persists_only_one_entry(self):
        if connection.vendor != 'mysql':
            self.skipTest('MySQL row locks are required for this concurrency test.')

        barrier = Barrier(2)

        def create_entry():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    self.create(seat_number=1)
                    return 'created'
                except ValueError:
                    return 'rejected'
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = [future.result(timeout=20) for future in (
                executor.submit(create_entry),
                executor.submit(create_entry),
            )]

        self.assertCountEqual(results, ['created', 'rejected'])
        self.funcion.refresh_from_db()
        self.assertEqual(Entrada.objects.count(), 1)
        self.assertEqual(self.funcion.entradas_compradas, 1)
        self.assertEqual(self.funcion.disponibilidad, 1)
        self.assertEqual(self.funcion.distribucion['filas'], ['RPA'])


class EliminarEntradaServiceTests(EntradaDataMixin, TestCase):
    def test_rejects_unknown_reason_and_missing_entry(self):
        with self.assertRaisesRegex(ValueError, 'motivo'):
            eliminar_entrada(1, 'manual')
        with self.assertRaises(Http404):
            eliminar_entrada(999999, 'finalizacion')

    def test_refund_deletes_entry_and_restores_function_atomically(self):
        entry = self.create(seat_number=1)

        eliminar_entrada(entry.pk, 'reembolso')

        self.funcion.refresh_from_db()
        self.assertFalse(Entrada.objects.filter(pk=entry.pk).exists())
        self.assertEqual(self.funcion.distribucion, {'version': 7, 'filas': ['APA']})
        self.assertEqual(self.funcion.disponibilidad, 2)
        self.assertEqual(self.funcion.entradas_compradas, 0)

    def test_finalization_deletes_entry_without_changing_function(self):
        entry = self.create(seat_number=1)
        self.funcion.fin = timezone.now() - timedelta(seconds=1)
        self.funcion.save(update_fields=['fin'])
        self.funcion.refresh_from_db()
        before = (
            self.funcion.distribucion,
            self.funcion.disponibilidad,
            self.funcion.entradas_compradas,
        )

        eliminar_entrada(entry.pk, 'finalizacion')

        self.funcion.refresh_from_db()
        self.assertFalse(Entrada.objects.filter(pk=entry.pk).exists())
        self.assertEqual(
            (
                self.funcion.distribucion,
                self.funcion.disponibilidad,
                self.funcion.entradas_compradas,
            ),
            before,
        )

    def test_refund_rejects_validated_entry_without_changes(self):
        entry = self.create(seat_number=1)
        entry.activa = False
        entry.save(update_fields=['activa'])
        self.funcion.refresh_from_db()
        before = (
            self.funcion.distribucion,
            self.funcion.disponibilidad,
            self.funcion.entradas_compradas,
        )

        with self.assertRaisesRegex(ValueError, 'validada'):
            eliminar_entrada(entry.pk, 'reembolso')

        self.funcion.refresh_from_db()
        self.assertTrue(Entrada.objects.filter(pk=entry.pk).exists())
        self.assertEqual(
            (
                self.funcion.distribucion,
                self.funcion.disponibilidad,
                self.funcion.entradas_compradas,
            ),
            before,
        )

    def test_refund_rejects_less_than_24_hours_before_start(self):
        entry = self.create(seat_number=1)
        fixed_now = timezone.now()
        self.funcion.inicio = fixed_now + timedelta(hours=23, minutes=59, seconds=59)
        self.funcion.fin = self.funcion.inicio + timedelta(minutes=100)
        self.funcion.save(update_fields=['inicio', 'fin'])

        with patch('entradas.services.timezone.now', return_value=fixed_now):
            with self.assertRaisesRegex(ValueError, '24 horas'):
                eliminar_entrada(entry.pk, 'reembolso')

        self.assertTrue(Entrada.objects.filter(pk=entry.pk).exists())
        self.funcion.refresh_from_db()
        self.assertEqual(self.funcion.distribucion['filas'], ['RPA'])
        self.assertEqual(self.funcion.disponibilidad, 1)
        self.assertEqual(self.funcion.entradas_compradas, 1)

    def test_refund_accepts_exactly_24_hours_before_start(self):
        entry = self.create(seat_number=1)
        fixed_now = timezone.now()
        self.funcion.inicio = fixed_now + timedelta(hours=24)
        self.funcion.fin = self.funcion.inicio + timedelta(minutes=100)
        self.funcion.save(update_fields=['inicio', 'fin'])

        with patch('entradas.services.timezone.now', return_value=fixed_now):
            eliminar_entrada(entry.pk, 'reembolso')

        self.assertFalse(Entrada.objects.filter(pk=entry.pk).exists())

    def test_refund_rejects_already_started_function(self):
        entry = self.create(seat_number=1)
        fixed_now = timezone.now()
        self.funcion.inicio = fixed_now - timedelta(seconds=1)
        self.funcion.fin = fixed_now + timedelta(minutes=99)
        self.funcion.save(update_fields=['inicio', 'fin'])

        with patch('entradas.services.timezone.now', return_value=fixed_now):
            with self.assertRaisesRegex(ValueError, '24 horas'):
                eliminar_entrada(entry.pk, 'reembolso')

        self.assertTrue(Entrada.objects.filter(pk=entry.pk).exists())

    def test_refund_restores_available_seat_invariant(self):
        entry = self.create(seat_number=1)
        eliminar_entrada(entry.pk, 'reembolso')

        self.funcion.refresh_from_db()
        available_seats = sum(row.count('A') for row in self.funcion.distribucion['filas'])
        self.assertEqual(self.funcion.disponibilidad, available_seats)
        self.assertEqual(self.funcion.entradas_compradas, 0)

    def test_bulk_finalization_deletes_all_entries_without_changing_function(self):
        self.create(seat_number=1)
        self.create(seat_number=2)
        self.funcion.fin = timezone.now() - timedelta(seconds=1)
        self.funcion.save(update_fields=['fin'])
        self.funcion.refresh_from_db()
        before = (
            self.funcion.distribucion,
            self.funcion.disponibilidad,
            self.funcion.entradas_compradas,
        )

        eliminadas = eliminar_entradas_por_finalizacion(self.funcion.pk)

        self.assertEqual(eliminadas, 2)
        self.assertFalse(Entrada.objects.filter(funcion=self.funcion).exists())
        self.funcion.refresh_from_db()
        self.assertEqual(
            (
                self.funcion.distribucion,
                self.funcion.disponibilidad,
                self.funcion.entradas_compradas,
            ),
            before,
        )

    def test_bulk_finalization_without_entries_is_idempotent(self):
        self.funcion.fin = timezone.now() - timedelta(seconds=1)
        self.funcion.save(update_fields=['fin'])

        self.assertEqual(eliminar_entradas_por_finalizacion(self.funcion.pk), 0)
        self.assertEqual(eliminar_entradas_por_finalizacion(self.funcion.pk), 0)

    def test_bulk_finalization_leaves_other_functions_untouched(self):
        self.create(seat_number=1)
        other_funcion = self.create_funcion(
            ['APA'], start=timezone.now() + timedelta(days=2)
        )
        other_entry = crear_entrada(other_funcion.pk, self.cuenta.pk, 1, 'A')
        self.funcion.fin = timezone.now() - timedelta(seconds=1)
        self.funcion.save(update_fields=['fin'])

        eliminar_entradas_por_finalizacion(self.funcion.pk)

        self.assertTrue(Entrada.objects.filter(pk=other_entry.pk).exists())

    def test_bulk_finalization_rejects_invalid_id(self):
        for invalid in (0, -1, True, 'A'):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                ValueError, 'función'
            ):
                eliminar_entradas_por_finalizacion(invalid)


class EntradaReadServiceTests(EntradaDataMixin, TestCase):
    def test_list_filters_by_account_and_selects_related_data(self):
        own_entry = self.create(seat_number=1)
        other_account = Cuenta.objects.create_user('other@example.com', 'Other')
        other_entry = self.create(seat_number=2, account=other_account)

        entries = listar_entradas(self.cuenta.pk)

        self.assertEqual(list(entries), [own_entry])
        self.assertEqual(entries[0].funcion.pelicula, self.pelicula)
        self.assertEqual(entries[0].funcion.sala, self.funcion.sala)
        self.assertNotIn(other_entry, entries)

    def test_list_for_account_without_entries_is_empty(self):
        other_account = Cuenta.objects.create_user('empty@example.com', 'Empty')

        self.assertEqual(list(listar_entradas(other_account.pk)), [])

    def test_get_returns_only_owned_entry_and_404s_for_foreign_or_missing(self):
        own_entry = self.create(seat_number=1)
        other_account = Cuenta.objects.create_user('other@example.com', 'Other')
        other_entry = self.create(seat_number=2, account=other_account)

        self.assertEqual(obtener_entrada(own_entry.pk, self.cuenta.pk), own_entry)
        with self.assertRaises(Http404):
            obtener_entrada(other_entry.pk, self.cuenta.pk)
        with self.assertRaises(Http404):
            obtener_entrada(999999, self.cuenta.pk)


class EntradaViewTests(EntradaDataMixin, TestCase):
    def test_list_shows_only_current_account_entries_and_summary(self):
        own_entry = self.create(seat_number=1)
        other_account = Cuenta.objects.create_user('other@example.com', 'Other')
        other_entry = self.create(seat_number=2, account=other_account)
        self.client.force_login(self.cuenta)

        response = self.client.get(reverse('entradas:entrada_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Película de prueba')
        self.assertContains(response, 'Sala 1')
        self.assertContains(
            response,
            timezone.localtime(self.funcion.inicio).strftime('%d/%m/%Y %H:%M'),
        )
        self.assertContains(response, 'Fila')
        self.assertContains(response, 'Asiento')
        self.assertContains(response, 'Pendiente de validación')
        self.assertContains(
            response,
            f'href="{reverse("entradas:entrada_detail", args=[own_entry.pk])}"',
        )
        self.assertNotContains(
            response,
            f'href="{reverse("entradas:entrada_detail", args=[other_entry.pk])}"',
        )

    def test_empty_list_and_login_requirement(self):
        empty_account = Cuenta.objects.create_user('empty@example.com', 'Empty')
        response = self.client.get(reverse('entradas:entrada_list'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(empty_account)
        response = self.client.get(reverse('entradas:entrada_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No tenés entradas.')

    def test_detail_shows_allowed_data_without_ids_or_distribution(self):
        entry = self.create(seat_number=1)
        self.client.force_login(self.cuenta)

        response = self.client.get(reverse('entradas:entrada_detail', args=[entry.pk]))

        self.assertEqual(response.status_code, 200)
        for text in (
            entry.codigo,
            'Película de prueba',
            timezone.localtime(self.funcion.inicio).strftime('%d/%m/%Y %H:%M'),
            'Sala 1',
            'Tipo de sala',
            '2D',
            'Tipo de sonido',
            'Dolby',
            'Capacidad de la sala',
            '2',
            'Fila',
            'A',
            'Asiento',
            '1',
            'Pendiente de validación',
        ):
            self.assertContains(response, text)
        for forbidden in ('funcion_id', 'cuenta_id', 'distribucion', 'entradas_compradas'):
            self.assertNotContains(response, forbidden)

    def test_detail_hides_foreign_and_missing_entries_with_404(self):
        own_entry = self.create(seat_number=1)
        other_account = Cuenta.objects.create_user('other@example.com', 'Other')
        other_entry = self.create(seat_number=2, account=other_account)
        self.client.force_login(self.cuenta)

        foreign_response = self.client.get(
            reverse('entradas:entrada_detail', args=[other_entry.pk])
        )
        missing_response = self.client.get(
            reverse('entradas:entrada_detail', args=[999999])
        )

        self.assertEqual(foreign_response.status_code, 404)
        self.assertEqual(missing_response.status_code, 404)
        self.assertNotContains(foreign_response, other_entry.codigo, status_code=404)
        self.assertTrue(Entrada.objects.filter(pk=own_entry.pk).exists())

    def test_manual_create_and_delete_routes_are_not_exposed(self):
        self.client.force_login(self.cuenta)

        self.assertEqual(self.client.get('/entradas/crear/').status_code, 404)
        self.assertEqual(self.client.get('/entradas/create/').status_code, 404)
        self.assertEqual(self.client.get('/entradas/1/delete/').status_code, 404)

    def test_staff_can_validate_code_once_and_non_staff_is_denied(self):
        entry = self.create(seat_number=1)
        staff = Cuenta.objects.create_superuser(
            'staff@example.com',
            'Staff',
            password='Strong-test-password-123',
        )
        url = reverse('entradas:entrada_validar')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.cuenta)
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.force_login(staff)
        response = self.client.post(url, {'codigo': entry.codigo.lower()})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Entrada validada correctamente.')
        self.assertContains(response, 'Película de prueba')
        entry.refresh_from_db()
        self.assertFalse(entry.activa)

        response = self.client.post(url, {'codigo': entry.codigo})
        self.assertContains(response, 'No se encontró ninguna entrada activa')


class ValidarEntradaServiceTests(EntradaDataMixin, TestCase):
    def test_validation_deactivates_active_code_once(self):
        entry = self.create(seat_number=1)

        validated = validar_entrada(entry.codigo.lower())

        self.assertIsNotNone(validated)
        self.assertFalse(validated.activa)
        self.assertIsNone(validar_entrada(entry.codigo))
        self.assertIsNone(validar_entrada('NO-EXISTE'))
        self.assertIsNone(validar_entrada(''))


class ValidarEntradaConcurrencyTests(EntradaDataMixin, TransactionTestCase):
    def test_concurrent_validation_accepts_code_only_once(self):
        if connection.vendor != 'mysql':
            self.skipTest('MySQL row updates are required for this concurrency test.')

        entry = self.create(seat_number=1)
        barrier = Barrier(2)

        def validate():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return validar_entrada(entry.codigo) is not None
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = [future.result(timeout=20) for future in (
                executor.submit(validate),
                executor.submit(validate),
            )]

        self.assertCountEqual(results, [True, False])


class EntradaAdminTests(TestCase):
    def setUp(self):
        self.admin_user = Cuenta.objects.create_superuser(
            'admin@example.com',
            'Administrator',
            password='Strong-test-password-123',
        )
        self.request = RequestFactory().get('/admin/entradas/entrada/')
        self.request.user = self.admin_user
        self.model_admin = EntradaAdmin(Entrada, AdminSite())

    def test_admin_is_read_only_and_has_no_delete_action(self):
        self.assertTrue(self.model_admin.has_view_permission(self.request))
        self.assertFalse(self.model_admin.has_add_permission(self.request))
        self.assertFalse(self.model_admin.has_change_permission(self.request))
        self.assertFalse(self.model_admin.has_delete_permission(self.request))
        self.assertNotIn('delete_selected', self.model_admin.get_actions(self.request))

    def test_staff_can_open_changelist_without_manual_creation_or_deletion(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('admin:entradas_entrada_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Add entrada')
        self.assertNotContains(response, 'Delete selected')
