from django.test import TestCase
from django.urls import reverse
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

    def test_update_can_uncheck_en_cartelera(self):
        pelicula = update_pelicula(self.pelicula.pk, {'en_cartelera': False})

        self.assertFalse(pelicula.en_cartelera)

    def test_update_can_check_en_cartelera(self):
        self.pelicula.en_cartelera = False
        self.pelicula.save(update_fields=['en_cartelera'])

        pelicula = update_pelicula(self.pelicula.pk, {'en_cartelera': True})

        self.assertTrue(pelicula.en_cartelera)

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

