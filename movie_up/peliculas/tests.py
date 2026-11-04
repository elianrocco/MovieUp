from urllib.parse import urlencode

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from cuentas.models import Cuenta

from .models import Pelicula
from .services import update_pelicula, create_pelicula


class UpdatePeliculaTests(TestCase):
    def setUp(self):
        self.pelicula = Pelicula.objects.create(
            titulo='Test Movie',
            imagen_portada='imgs/test-movie.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Test description',
            clasificacion='PG',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )

        self.staff = Cuenta.objects.create_user(
            'staff-update@example.com', 'Staff Update', is_staff=True
        )
        self.client.force_login(self.staff)

    def test_update_can_uncheck_en_cartelera(self):
        pelicula = update_pelicula(self.pelicula.pk, {'en_cartelera': False})

        self.assertFalse(pelicula.en_cartelera)

    def test_update_can_check_en_cartelera(self):
        self.pelicula.en_cartelera = False
        self.pelicula.save(update_fields=['en_cartelera'])

        pelicula = update_pelicula(self.pelicula.pk, {'en_cartelera': True})

        self.assertTrue(pelicula.en_cartelera)

    def test_update_rejects_a_title_used_by_another_movie(self):
        Pelicula.objects.create(
            titulo='Other Movie',
            imagen_portada='imgs/other.jpg',
            genero='Drama',
            duracion_minutos=90,
            descripcion='Other description',
            clasificacion='PG',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/other',
            en_cartelera=True,
        )

        with self.assertRaisesRegex(ValueError, 'Ya existe una película con el título'):
            update_pelicula(self.pelicula.pk, {'titulo': 'Other Movie'})

        self.pelicula.refresh_from_db()
        self.assertEqual(self.pelicula.titulo, 'Test Movie')

    def test_update_form_can_uncheck_en_cartelera(self):
        response = self.client.post(
            reverse('peliculas:pelicula_update', args=[self.pelicula.pk]),
            data={},
        )

        self.assertRedirects(
            response,
            reverse('peliculas:pelicula_detail', args=[self.pelicula.pk]),
        )
        self.pelicula.refresh_from_db()
        self.assertFalse(self.pelicula.en_cartelera)


class CreatePeliculaTests(TestCase):
    def setUp(self):
        self.pelicula = Pelicula.objects.create(
            titulo='Test Movie',
            imagen_portada='imgs/test-movie.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Test description',
            clasificacion='PG',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )
        
        self.valid_data = {
            'titulo': 'New Movie',
            'genero': 'Action',
            'duracion_minutos': '120',
            'descripcion': 'New description',
            'clasificacion': 'R',
            'fecha_estreno': '2026-06-01',
            'url_trailer': 'https://example.com/new-trailer',
        }

        self.staff = Cuenta.objects.create_user(
            'staff-create@example.com', 'Staff Create', is_staff=True
        )
        self.client.force_login(self.staff)

    def test_create_pelicula_rejects_duplicate_title(self):
        """create_pelicula debe rechazar títulos duplicados"""
        data = self.valid_data.copy()
        data['titulo'] = 'Test Movie'  # Título que ya existe
        
        with self.assertRaises(ValueError) as context:
            create_pelicula(data, None)
        
        self.assertIn('Ya existe una película con el título', str(context.exception))

    def test_create_form_shows_error_for_duplicate_title(self):
        """El formulario debe mostrar error al intentar crear con título duplicado"""
        data = self.valid_data.copy()
        data['titulo'] = 'Test Movie'  # Título que ya existe
        
        response = self.client.post(
            reverse('peliculas:pelicula_create'),
            data=data,
        )
        
        # Debe re-renderizar el formulario (no redirect)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya existe una película con el título')
        self.assertTemplateUsed(response, 'peliculas/form.html')
        
        # No debe crear nueva película
        self.assertEqual(Pelicula.objects.count(), 1)

    def test_create_pelicula_allows_unique_title(self):
        """create_pelicula debe permitir títulos únicos"""
        data = self.valid_data.copy()
        
        pelicula = create_pelicula(data, None)
        
        self.assertEqual(pelicula.titulo, 'New Movie')
        self.assertEqual(Pelicula.objects.count(), 2)


class AccesoRestringidoTests(TestCase):
    def setUp(self):
        self.pelicula = Pelicula.objects.create(
            titulo='Película Restringida',
            imagen_portada='imgs/restringida.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Descripción de prueba',
            clasificacion='ATP',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )
        self.comun = Cuenta.objects.create_user(
            'comun-peliculas@example.com', 'Comun Peliculas'
        )
        self.staff = Cuenta.objects.create_user(
            'guardia-peliculas@example.com', 'Guardia Peliculas', is_staff=True
        )
        self.rutas = [
            reverse('peliculas:pelicula_list'),
            reverse('peliculas:pelicula_create'),
            reverse('peliculas:pelicula_detail', args=[self.pelicula.pk]),
            reverse('peliculas:pelicula_update', args=[self.pelicula.pk]),
            reverse('peliculas:pelicula_delete', args=[self.pelicula.pk]),
        ]

    def test_visitante_es_redirigido_al_login_en_las_cinco_rutas(self):
        for ruta in self.rutas:
            expected = f'{settings.LOGIN_URL}?{urlencode({"next": ruta}, safe="/")}'
            response = self.client.get(ruta)
            self.assertRedirects(
                response, expected, fetch_redirect_response=False, msg_prefix=ruta
            )

    def test_comun_es_redirigido_a_la_portada_en_las_cinco_rutas(self):
        self.client.force_login(self.comun)
        for ruta in self.rutas:
            response = self.client.get(ruta)
            self.assertRedirects(
                response, '/', fetch_redirect_response=False, msg_prefix=ruta
            )

    def test_comun_no_modifica_el_registro(self):
        self.client.force_login(self.comun)

        response = self.client.post(
            reverse('peliculas:pelicula_update', args=[self.pelicula.pk]),
            {'titulo': 'Titulo Intruso'},
        )

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.pelicula.refresh_from_db()
        self.assertEqual(self.pelicula.titulo, 'Película Restringida')

        response = self.client.post(
            reverse('peliculas:pelicula_delete', args=[self.pelicula.pk])
        )

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertTrue(Pelicula.objects.filter(pk=self.pelicula.pk).exists())

    def test_staff_accede_a_las_cinco_rutas(self):
        self.client.force_login(self.staff)
        for ruta in self.rutas:
            response = self.client.get(ruta)
            self.assertEqual(response.status_code, 200, ruta)


class PanelFragmentTests(TestCase):
    """ui-crud-pages 3.1-3.2: the panel gets fragments, never a document."""

    panel = {'X-Panel-Request': '1'}

    def setUp(self):
        self.pelicula = Pelicula.objects.create(
            titulo='Test Movie',
            imagen_portada='imgs/test-movie.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Test description',
            clasificacion='PG',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )
        self.valid_data = {
            'titulo': 'New Movie',
            'genero': 'Action',
            'duracion_minutos': '120',
            'descripcion': 'New description',
            'clasificacion': 'R',
            'fecha_estreno': '2026-06-01',
            'url_trailer': 'https://example.com/new-trailer',
        }
        self.staff = Cuenta.objects.create_user(
            'staff-panel-peliculas@example.com', 'Staff Panel Peliculas', is_staff=True
        )
        self.client.force_login(self.staff)

    def _panel_get(self, url):
        return self.client.get(url, headers=self.panel)

    def _page_urls(self):
        return (
            reverse('peliculas:pelicula_detail', args=[self.pelicula.pk]),
            reverse('peliculas:pelicula_create'),
            reverse('peliculas:pelicula_update', args=[self.pelicula.pk]),
            reverse('peliculas:pelicula_delete', args=[self.pelicula.pk]),
        )

    def test_detail_answers_the_partial_without_a_document(self):
        response = self._panel_get(
            reverse('peliculas:pelicula_detail', args=[self.pelicula.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'detail')
        self.assertNotContains(response, '<html')
        self.assertContains(response, 'page-card')

    def test_form_and_confirmation_are_flagged_as_form(self):
        for url in self._page_urls()[1:]:
            with self.subTest(url=url):
                response = self._panel_get(url)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['X-Panel-View'], 'form')
                self.assertNotContains(response, '<html')
                self.assertContains(response, 'page-card')

    def test_same_urls_answer_the_full_page_without_the_header(self):
        for url in self._page_urls():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<!DOCTYPE html>', html=False)
                self.assertNotIn('X-Panel-View', response)

    def test_create_success_returns_the_list_fragment(self):
        response = self.client.post(
            reverse('peliculas:pelicula_create'), self.valid_data, headers=self.panel
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'list')
        self.assertNotContains(response, '<html')
        self.assertContains(response, 'New Movie')
        self.assertTrue(Pelicula.objects.filter(titulo='New Movie').exists())

    def test_create_error_returns_the_form_with_message_and_sent_data(self):
        data = {**self.valid_data, 'titulo': 'Test Movie'}

        response = self.client.post(
            reverse('peliculas:pelicula_create'), data, headers=self.panel
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'form')
        self.assertNotContains(response, '<html')
        self.assertContains(response, 'Ya existe una película con el título')
        self.assertContains(response, 'value="Action"')
        self.assertEqual(Pelicula.objects.count(), 1)

    def test_update_error_returns_the_form_instead_of_a_server_error(self):
        """A title owned by another movie used to raise IntegrityError (HTTP 500)."""
        Pelicula.objects.create(
            titulo='Other Movie',
            imagen_portada='imgs/other.jpg',
            genero='Drama',
            duracion_minutos=90,
            descripcion='Other description',
            clasificacion='PG',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/other',
            en_cartelera=True,
        )
        data = {**self.valid_data, 'titulo': 'Other Movie'}

        response = self.client.post(
            reverse('peliculas:pelicula_update', args=[self.pelicula.pk]),
            data,
            headers=self.panel,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'form')
        self.assertContains(response, 'Ya existe una película con el título')
        self.assertContains(response, 'value="Action"')
        self.assertEqual(Pelicula.objects.get(pk=self.pelicula.pk).titulo, 'Test Movie')

    def test_delete_success_returns_the_list_without_the_record(self):
        response = self.client.post(
            reverse('peliculas:pelicula_delete', args=[self.pelicula.pk]),
            {},
            headers=self.panel,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'list')
        self.assertNotContains(response, 'Test Movie')
        self.assertFalse(Pelicula.objects.filter(pk=self.pelicula.pk).exists())

