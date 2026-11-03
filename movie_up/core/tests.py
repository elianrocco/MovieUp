from types import SimpleNamespace
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.template import engines
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from .decorators import staff_required


@staff_required
def protected_view(request):
    return HttpResponse('ok')


def _render_base(user):
    """Render base.html with the given user in context."""
    engine = engines['django']
    template = engine.get_template('base.html')
    context = {'user': user}
    return template.render(context)


class StaffRequiredTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _call(self, user, path='/peliculas/'):
        request = self.factory.get(path)
        request.user = user
        return protected_view(request)

    def test_anonymous_is_sent_to_login_keeping_next(self):
        response = self._call(AnonymousUser())

        expected = f'{settings.LOGIN_URL}?{urlencode({"next": "/peliculas/"}, safe="/")}'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected)

    def test_common_account_is_sent_home(self):
        user = SimpleNamespace(is_authenticated=True, is_staff=False)

        response = self._call(user)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_staff_account_reaches_the_view(self):
        user = SimpleNamespace(is_authenticated=True, is_staff=True)

        response = self._call(user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')


class NavStateTests(TestCase):
    def test_visitor_sees_login(self):
        html = _render_base(AnonymousUser())
        self.assertIn('Login', html)
        self.assertNotIn('Logout', html)
        self.assertNotIn('site-nav__ticket', html)

    def test_common_user_sees_ticket_and_logout(self):
        user = SimpleNamespace(
            is_authenticated=True,
            is_staff=False,
            nombre='Juan',
            foto_url=''
        )
        html = _render_base(user)
        self.assertIn('Logout', html)
        self.assertIn('site-nav__ticket', html)
        self.assertIn('Mis entradas', html)
        self.assertNotIn('Login', html)

    def test_admin_sees_logout_only(self):
        user = SimpleNamespace(
            is_authenticated=True,
            is_staff=True,
            nombre='Admin',
            foto_url=''
        )
        html = _render_base(user)
        self.assertIn('Logout', html)
        self.assertNotIn('site-nav__ticket', html)
        self.assertNotIn('Login', html)

    def test_user_with_photo_shows_image(self):
        user = SimpleNamespace(
            is_authenticated=True,
            is_staff=False,
            nombre='María',
            foto_url='https://example.com/photo.jpg'
        )
        html = _render_base(user)
        self.assertIn('https://example.com/photo.jpg', html)
        self.assertIn('site-nav__avatar', html)

    def test_user_without_photo_shows_initial(self):
        user = SimpleNamespace(
            is_authenticated=True,
            is_staff=False,
            nombre='Pedro',
            foto_url=''
        )
        html = _render_base(user)
        self.assertIn('site-nav__avatar-placeholder', html)
        self.assertIn('P', html)  # First letter of "Pedro"


class FooterTests(SimpleTestCase):
    def test_footer_always_present(self):
        html = _render_base(AnonymousUser())
        self.assertIn('Elian', html)
        self.assertIn('Proyecto educativo sin fines de lucro', html)
        self.assertIn('módulo de pago se incluye con propósito de aprendizaje', html)


class HomeViewTests(TestCase):
    """Tests for the home page (task 3.1, 3.2, 3.3)."""

    def setUp(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from peliculas.models import Pelicula
        self.Pelicula = Pelicula
        
        # Crear imagen dummy para los tests
        self.imagen_dummy = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )

        # Create test movies
        self.pelicula_cartelera_1 = self.Pelicula.objects.create(
            titulo='Movie 1',
            genero='Action',
            duracion_minutos=120,
            descripcion='Description 1',
            clasificacion='PG-13',
            fecha_estreno='2024-01-15',
            url_trailer='https://example.com/trailer1',
            en_cartelera=True,
            imagen_portada=self.imagen_dummy
        )
        self.pelicula_cartelera_2 = self.Pelicula.objects.create(
            titulo='Movie 2',
            genero='Drama',
            duracion_minutos=90,
            descripcion='Description 2',
            clasificacion='R',
            fecha_estreno='2024-02-20',
            url_trailer='https://example.com/trailer2',
            en_cartelera=True,
            imagen_portada=self.imagen_dummy
        )
        self.pelicula_no_cartelera = self.Pelicula.objects.create(
            titulo='Movie 3',
            genero='Comedy',
            duracion_minutos=100,
            descripcion='Description 3',
            clasificacion='PG',
            fecha_estreno='2024-03-10',
            url_trailer='https://example.com/trailer3',
            en_cartelera=False,
            imagen_portada=self.imagen_dummy
        )

    def test_visitor_gets_200(self):
        """Visitor can access home page."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_common_user_gets_200(self):
        """Common authenticated user can access home page."""
        from cuentas.models import Cuenta
        user = Cuenta.objects.create_user(
            correo='user@example.com',
            nombre='Test User'
        )
        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_admin_redirected_to_gestion(self):
        """Admin user is redirected to /gestion/."""
        from cuentas.models import Cuenta
        admin = Cuenta.objects.create_user(
            correo='admin@example.com',
            nombre='Admin User',
            is_staff=True
        )
        self.client.force_login(admin)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/gestion/', fetch_redirect_response=False)

    def test_hero_shows_most_recent_cartelera_movie(self):
        """Hero displays the most recent movie in cartelera."""
        response = self.client.get(reverse('home'))
        # Movie 2 is most recent in cartelera, should be in hero
        self.assertContains(response, 'hero__title')
        self.assertContains(response, 'Movie 2')

    def test_hero_filters_en_cartelera(self):
        """Hero only shows movies with en_cartelera=True."""
        response = self.client.get(reverse('home'))
        # Movie 3 is not in cartelera, should not be anywhere
        self.assertNotContains(response, 'Movie 3')
        # Movie 2 should be in hero (most recent in cartelera)
        self.assertContains(response, 'Movie 2')

    def test_empty_state_when_no_cartelera(self):
        """Empty state shown when no movies in cartelera."""
        self.Pelicula.objects.all().update(en_cartelera=False)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No hay películas en cartelera')

    def test_grid_shows_all_cartelera_movies(self):
        """Grid displays all movies with en_cartelera=True."""
        response = self.client.get(reverse('home'))
        # Both cartelera movies should be in the grid (as cards)
        self.assertContains(response, 'card__title')
        self.assertContains(response, 'Movie 1')
        self.assertContains(response, 'Movie 2')

    def test_grid_excludes_no_cartelera(self):
        """Grid excludes movies with en_cartelera=False."""
        response = self.client.get(reverse('home'))
        # Movie 3 should not appear anywhere
        self.assertNotContains(response, 'Movie 3')

    def test_trailer_button_links_to_url_trailer(self):
        """Trailer button links to the movie's url_trailer."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'https://example.com/trailer2')

    def test_buy_button_without_session_redirects_to_login(self):
        """Buy button without session redirects to login with ?next=/."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, '/accounts/login/?next=/')

    def test_buy_button_with_session_has_placeholder(self):
        """Buy button with session has href='#' (D8 decision)."""
        from cuentas.models import Cuenta
        user = Cuenta.objects.create_user(
            correo='user@example.com',
            nombre='Test User'
        )
        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        # Should have href="#" for authenticated users
        self.assertContains(response, 'href="#"')
