import json
import re
from pathlib import Path

from django.contrib import admin
from django.http import Http404
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Sala
from .templatetags.salas_tags import CELL_CLASS_MAP, celda_clase
from .services import (
    calcular_capacidad,
    create_sala,
    delete_sala,
    get_sala,
    list_salas,
    update_sala,
    validar_distribucion,
    versionar_distribucion,
)


class DistributionValidationTests(SimpleTestCase):
    def test_validates_dict_and_ignores_client_version(self):
        result = validar_distribucion({'version': 99, 'filas': [' a r p ']})

        self.assertEqual(result, {'version': 1, 'filas': ['ARP']})

    def test_accepts_json_string_and_normalizes_case_and_whitespace(self):
        payload = json.dumps({'version': 7, 'filas': [' a r p ', 'P a r']})

        self.assertEqual(
            validar_distribucion(payload),
            {'version': 1, 'filas': ['ARP', 'PAR']},
        )

    def test_rejects_invalid_json(self):
        with self.assertRaisesRegex(ValueError, 'JSON válido'):
            validar_distribucion('{invalid json')

    def test_rejects_non_object_payload(self):
        with self.assertRaisesRegex(ValueError, 'objeto JSON'):
            validar_distribucion(['AR'])

    def test_rejects_missing_or_empty_rows(self):
        for payload in ({}, {'filas': []}, {'filas': 'AR'}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validar_distribucion(payload)

    def test_rejects_non_string_or_empty_row(self):
        for row in (1, ''):
            with self.subTest(row=row), self.assertRaises(ValueError):
                validar_distribucion({'filas': [row]})

    def test_rejects_rows_with_different_lengths(self):
        with self.assertRaisesRegex(ValueError, 'misma cantidad'):
            validar_distribucion({'filas': ['AAR', 'AA']})

    def test_rejects_invalid_cell_characters(self):
        with self.assertRaisesRegex(ValueError, 'Solo se admiten P, A y R'):
            validar_distribucion({'filas': ['AXR']})

    def test_rejects_more_than_100_rows(self):
        with self.assertRaisesRegex(ValueError, '100 filas'):
            validar_distribucion({'filas': ['A'] * 101})

    def test_rejects_more_than_100_columns(self):
        with self.assertRaisesRegex(ValueError, '100 columnas'):
            validar_distribucion({'filas': ['A' * 101]})

    def test_accepts_maximum_100_by_100_distribution(self):
        result = validar_distribucion({'filas': ['A' * 100 for _ in range(100)]})

        self.assertEqual(len(result['filas']), 100)
        self.assertTrue(all(len(fila) == 100 for fila in result['filas']))

    def test_rejects_distribution_without_seats(self):
        with self.assertRaisesRegex(ValueError, 'al menos una butaca'):
            validar_distribucion({'filas': ['PPP', 'PPP']})

    def test_calculates_capacity_from_seats_and_reserved_cells(self):
        distribution = {'filas': ['A' * 120 + 'R' * 15 + 'P' * 40]}

        self.assertEqual(calcular_capacidad(distribution), 135)

    def test_pasillos_do_not_add_to_capacity(self):
        self.assertEqual(calcular_capacidad({'filas': ['PPP']}), 0)

    def test_initial_distribution_version_is_one_and_ignores_input(self):
        result = versionar_distribucion({'version': 999, 'filas': ['AR']})

        self.assertEqual(result, {'version': 1, 'filas': ['AR']})

    def test_unchanged_normalized_distribution_keeps_version(self):
        previous = {'version': 4, 'filas': ['AR']}

        result = versionar_distribucion(
            json.dumps({'version': 999, 'filas': ['a r']}),
            distribucion_anterior=previous,
        )

        self.assertEqual(result, {'version': 4, 'filas': ['AR']})

    def test_changed_distribution_increments_version(self):
        previous = {'version': 4, 'filas': ['AR']}

        result = versionar_distribucion(
            {'version': 1, 'filas': ['AA']}, distribucion_anterior=previous
        )

        self.assertEqual(result, {'version': 5, 'filas': ['AA']})


class SalaServiceTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'nombre': 'Sala A',
            'tipo_sala': '2D',
            'tipo_sonido': 'Dolby',
            'distribucion': {'version': 500, 'filas': ['AARPP']},
        }

    def test_list_salas_orders_by_name(self):
        Sala.objects.create(
            nombre='Sala Z', tipo_sala='2D', tipo_sonido='Dolby',
            distribucion={'version': 1, 'filas': ['A']}, capacidad=1,
        )
        Sala.objects.create(
            nombre='Sala B', tipo_sala='2D', tipo_sonido='Dolby',
            distribucion={'version': 1, 'filas': ['A']}, capacidad=1,
        )

        self.assertEqual([s.nombre for s in list_salas()], ['Sala B', 'Sala Z'])

    def test_get_sala_raises_http_404_for_unknown_id(self):
        with self.assertRaises(Http404):
            get_sala(999)

    def test_create_sala_derives_capacity_and_initial_version(self):
        data = {**self.valid_data, 'capacidad': 999}

        sala = create_sala(data)

        self.assertEqual(sala.capacidad, 3)
        self.assertEqual(sala.distribucion, {'version': 1, 'filas': ['AARPP']})

    def test_create_sala_rejects_duplicate_name(self):
        create_sala(self.valid_data)

        with self.assertRaisesRegex(ValueError, 'Ya existe una sala'):
            create_sala({**self.valid_data, 'tipo_sala': '3D'})

    def test_create_sala_requires_all_text_fields(self):
        for field in ('nombre', 'tipo_sala', 'tipo_sonido'):
            data = {**self.valid_data}
            data.pop(field)
            with self.subTest(field=field), self.assertRaises(ValueError):
                create_sala(data)

    def test_create_sala_rejects_non_text_and_overlong_fields(self):
        for value in (10, 'x' * 46):
            with self.subTest(value_type=type(value).__name__, length=len(str(value))):
                with self.assertRaises(ValueError):
                    create_sala({**self.valid_data, 'tipo_sala': value})

    def test_create_sala_rejects_invalid_distribution_without_saving(self):
        with self.assertRaises(ValueError):
            create_sala({**self.valid_data, 'distribucion': {'filas': ['PPP']}})

        self.assertEqual(Sala.objects.count(), 0)

    def test_update_sala_allows_own_name_and_partial_fields(self):
        sala = create_sala(self.valid_data)

        updated = update_sala(sala.pk, {'nombre': sala.nombre, 'tipo_sonido': '  DTS  '})

        self.assertEqual(updated.nombre, 'Sala A')
        self.assertEqual(updated.tipo_sonido, 'DTS')
        self.assertEqual(updated.distribucion, {'version': 1, 'filas': ['AARPP']})
        self.assertEqual(updated.capacidad, 3)

    def test_update_sala_rejects_another_salas_name(self):
        sala = create_sala(self.valid_data)
        other = create_sala({**self.valid_data, 'nombre': 'Sala B'})

        with self.assertRaisesRegex(ValueError, 'Ya existe una sala'):
            update_sala(sala.pk, {'nombre': other.nombre})

        sala.refresh_from_db()
        self.assertEqual(sala.nombre, 'Sala A')

    def test_update_sala_replaces_distribution_recalculates_and_increments_version(self):
        sala = create_sala(self.valid_data)

        updated = update_sala(
            sala.pk,
            {'distribucion': {'version': 999, 'filas': ['PAA']}},
        )

        self.assertEqual(updated.distribucion, {'version': 2, 'filas': ['PAA']})
        self.assertEqual(updated.capacidad, 2)

    def test_update_sala_keeps_version_for_identical_normalized_distribution(self):
        sala = create_sala(self.valid_data)

        updated = update_sala(sala.pk, {'distribucion': {'version': 999, 'filas': ['a a r p p']}})

        self.assertEqual(updated.distribucion, {'version': 1, 'filas': ['AARPP']})

    def test_update_sala_ignores_capacity_from_client(self):
        sala = create_sala(self.valid_data)

        updated = update_sala(sala.pk, {'capacidad': 999})

        self.assertEqual(updated.capacidad, 3)

    def test_update_sala_raises_http_404_for_unknown_id(self):
        with self.assertRaises(Http404):
            update_sala(999, {'nombre': 'Sala nueva'})

    def test_delete_sala_works_without_funciones_app(self):
        sala = create_sala(self.valid_data)

        delete_sala(sala.pk)

        self.assertFalse(Sala.objects.filter(pk=sala.pk).exists())

    def test_delete_sala_raises_http_404_for_unknown_id(self):
        with self.assertRaises(Http404):
            delete_sala(999)


class SalaTemplateTagTests(SimpleTestCase):
    def test_cell_class_filter_maps_each_supported_cell(self):
        for cell, css_class in CELL_CLASS_MAP.items():
            with self.subTest(cell=cell):
                self.assertEqual(celda_clase(cell), css_class)

    def test_python_and_javascript_cell_class_maps_match(self):
        script_path = Path(__file__).parent / 'static' / 'salas' / 'js' / 'grid.js'
        script = script_path.read_text(encoding='utf-8')
        match = re.search(
            r'const CELL_CLASS_MAP = Object\.freeze\(\{(.*?)\}\);',
            script,
            re.DOTALL,
        )

        self.assertIsNotNone(match, 'grid.js must define CELL_CLASS_MAP')
        javascript_map = dict(
            re.findall(r'\b([PAR]):\s*"([^"]+)"', match.group(1))
        )
        self.assertEqual(javascript_map, CELL_CLASS_MAP)

    def test_stylesheet_defines_the_three_cell_classes_and_colors(self):
        css_path = Path(__file__).parent / 'static' / 'salas' / 'css' / 'salas.css'
        stylesheet = css_path.read_text(encoding='utf-8')
        expected_colors = {
            'celda--pasillo': '#888',
            'celda--asiento': '#1976d2',
            'celda--reservado': '#d4af37',
        }

        for css_class, color in expected_colors.items():
            with self.subTest(css_class=css_class):
                self.assertIn(f'.{css_class}', stylesheet)
                self.assertIn(f'background-color: {color};', stylesheet)


class SalaViewTests(TestCase):
    def setUp(self):
        self.sala = create_sala({
            'nombre': 'Sala Central',
            'tipo_sala': '2D',
            'tipo_sonido': 'Dolby',
            'distribucion': {'version': 1, 'filas': ['PAR', 'AAR']},
        })

    def test_all_sala_urls_reverse(self):
        self.assertEqual(reverse('salas:sala_list'), '/salas/')
        self.assertEqual(reverse('salas:sala_create'), '/salas/create/')
        self.assertEqual(reverse('salas:sala_detail', args=[self.sala.pk]), f'/salas/{self.sala.pk}/')
        self.assertEqual(reverse('salas:sala_update', args=[self.sala.pk]), f'/salas/{self.sala.pk}/update/')
        self.assertEqual(reverse('salas:sala_delete', args=[self.sala.pk]), f'/salas/{self.sala.pk}/delete/')

    def test_list_renders_salas_and_shared_stylesheet(self):
        response = self.client.get(reverse('salas:sala_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sala.nombre)
        self.assertContains(response, '2D')
        self.assertContains(response, 'Dolby')
        self.assertContains(response, 'href="/static/salas/css/salas.css"')

    def test_detail_renders_read_only_grid_with_shared_css_without_grid_script(self):
        response = self.client.get(reverse('salas:sala_detail', args=[self.sala.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sala.nombre)
        self.assertContains(response, 'href="/static/salas/css/salas.css"')
        self.assertNotContains(response, 'salas/js/grid.js')
        self.assertContains(response, 'celda--pasillo')
        self.assertContains(response, 'celda--asiento')
        self.assertContains(response, 'celda--reservado')
        self.assertEqual(response.content.decode().count('seat-grid__cell'), 6)

    def test_detail_returns_404_for_unknown_id(self):
        response = self.client.get(reverse('salas:sala_detail', args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_create_form_loads_shared_css_grid_script_and_html_constraints(self):
        response = self.client.get(reverse('salas:sala_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/salas/css/salas.css"')
        self.assertContains(response, 'src="/static/salas/js/grid.js"')
        self.assertContains(response, 'name="nombre" type="text" maxlength="45"')
        self.assertContains(response, 'name="tipo_sala" type="text" maxlength="45"')
        self.assertContains(response, 'name="tipo_sonido" type="text" maxlength="45"')
        self.assertContains(response, 'required', count=5)
        self.assertContains(response, 'min="1" max="100"', count=2)
        self.assertContains(response, '"initial-distribution"')

    def test_create_post_persists_distribution_capacity_and_ignores_version(self):
        response = self.client.post(
            reverse('salas:sala_create'),
            {
                'nombre': 'Sala Nueva',
                'tipo_sala': '3D',
                'tipo_sonido': 'DTS',
                'distribucion': json.dumps({'version': 500, 'filas': ['AARPP']}),
                'capacidad': '999',
            },
        )

        self.assertRedirects(response, reverse('salas:sala_list'))
        nueva = Sala.objects.get(nombre='Sala Nueva')
        self.assertEqual(nueva.capacidad, 3)
        self.assertEqual(nueva.distribucion, {'version': 1, 'filas': ['AARPP']})

    def test_create_post_rerenders_error_for_duplicate_name(self):
        response = self.client.post(
            reverse('salas:sala_create'),
            {
                'nombre': self.sala.nombre,
                'tipo_sala': '3D',
                'tipo_sonido': 'DTS',
                'distribucion': json.dumps({'filas': ['AR']}),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya existe una sala')
        self.assertEqual(Sala.objects.count(), 1)

    def test_create_post_rerenders_distribution_error(self):
        distribution = {'filas': ['PPP']}
        response = self.client.post(
            reverse('salas:sala_create'),
            {
                'nombre': 'Sala Vacía',
                'tipo_sala': '2D',
                'tipo_sonido': 'Dolby',
                'distribucion': json.dumps(distribution),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'al menos una butaca')
        self.assertEqual(response.context['initial_distribution'], distribution)
        self.assertEqual(Sala.objects.count(), 1)

    def test_update_form_prefills_fields_and_grid_state(self):
        response = self.client.get(reverse('salas:sala_update', args=[self.sala.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Sala Central"')
        self.assertContains(response, 'value="2D"')
        self.assertContains(response, 'value="Dolby"')
        self.assertContains(response, '"version": 1')
        self.assertContains(response, '"filas": ["PAR", "AAR"]')
        self.assertNotContains(response, 'name="nombre" type="text" maxlength="45" value="Sala Central" required')

    def test_update_post_can_change_only_one_scalar_field(self):
        response = self.client.post(
            reverse('salas:sala_update', args=[self.sala.pk]),
            {'tipo_sonido': 'DTS'},
        )

        self.assertRedirects(response, reverse('salas:sala_detail', args=[self.sala.pk]))
        self.sala.refresh_from_db()
        self.assertEqual(self.sala.tipo_sonido, 'DTS')
        self.assertEqual(self.sala.nombre, 'Sala Central')
        self.assertEqual(self.sala.distribucion, {'version': 1, 'filas': ['PAR', 'AAR']})

    def test_update_post_rerenders_error_for_duplicate_name(self):
        other = create_sala({
            'nombre': 'Sala Ocupada',
            'tipo_sala': '2D',
            'tipo_sonido': 'DTS',
            'distribucion': {'filas': ['AR']},
        })

        response = self.client.post(
            reverse('salas:sala_update', args=[self.sala.pk]),
            {'nombre': other.nombre},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya existe una sala')
        self.assertContains(response, f'value="{other.nombre}"')
        self.sala.refresh_from_db()
        self.assertEqual(self.sala.nombre, 'Sala Central')

    def test_update_post_replaces_grid_and_increments_version(self):
        response = self.client.post(
            reverse('salas:sala_update', args=[self.sala.pk]),
            {'distribucion': json.dumps({'version': 100, 'filas': ['PAA']})},
        )

        self.assertRedirects(response, reverse('salas:sala_detail', args=[self.sala.pk]))
        self.sala.refresh_from_db()
        self.assertEqual(self.sala.distribucion, {'version': 2, 'filas': ['PAA']})
        self.assertEqual(self.sala.capacidad, 2)

    def test_update_returns_404_for_unknown_id(self):
        response = self.client.get(reverse('salas:sala_update', args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_delete_confirmation_loads_css_and_post_deletes_sala(self):
        response = self.client.get(reverse('salas:sala_delete', args=[self.sala.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sala.nombre)
        self.assertContains(response, 'href="/static/salas/css/salas.css"')

        response = self.client.post(reverse('salas:sala_delete', args=[self.sala.pk]))

        self.assertRedirects(response, reverse('salas:sala_list'))
        self.assertFalse(Sala.objects.filter(pk=self.sala.pk).exists())

    def test_delete_returns_404_for_unknown_id(self):
        response = self.client.get(reverse('salas:sala_delete', args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_sala_is_registered_in_admin(self):
        self.assertIn(Sala, admin.site._registry)
