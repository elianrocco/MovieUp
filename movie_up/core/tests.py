from types import SimpleNamespace
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.template import engines
from django.test import Client, RequestFactory, SimpleTestCase, TestCase
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
        self.assertNotIn('site-nav__validation', html)

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
        self.assertNotIn('site-nav__validation', html)

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
        self.assertIn('site-nav__validation', html)
        self.assertIn('Validar entradas', html)
        self.assertIn(
            f'href="{reverse("entradas:entrada_validar")}"', html
        )

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

    def test_brand_logo_uses_the_uploaded_asset(self):
        html = _render_base(AnonymousUser())
        self.assertIn('<img', html)
        self.assertIn('static/img/logo21.jpg', html)
        self.assertIn('class="site-nav__logo"', html)


class LogoutNavTests(TestCase):
    """ui-crud-pages 5.2: the nav closes the session with a POST, no interstitial."""

    def setUp(self):
        from cuentas.models import Cuenta

        # A common account: the home page redirects staff to /gestion/.
        self.user = Cuenta.objects.create_user('logout-nav@example.com', 'Logout Nav')
        self.client.force_login(self.user)

    def test_nav_renders_a_post_form_instead_of_a_get_link(self):
        html = _render_base(
            SimpleNamespace(is_authenticated=True, is_staff=True, nombre='Admin', foto_url='')
        )

        self.assertIn('action="/accounts/logout/"', html)
        self.assertIn('<button type="submit" class="site-nav__logout">Logout</button>', html)
        self.assertNotIn('href="/accounts/logout/"', html)

    def test_post_closes_the_session_and_lands_home(self):
        response = self.client.post(reverse('account_logout'))

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        page = self.client.get(reverse('home'))
        self.assertNotContains(page, 'site-nav__logout')
        self.assertContains(page, 'site-nav__login')

    def test_post_without_csrf_token_is_rejected_and_keeps_the_session(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        response = client.post(reverse('account_logout'))

        self.assertEqual(response.status_code, 403)
        page = client.get(reverse('home'))
        self.assertContains(page, 'site-nav__logout')


class FooterTests(TestCase):
    """Rendering the footer renders base.html, which now resolves the Google
    provider login URL (allauth touches the SocialApp table), so this needs a
    database."""
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

    def test_buy_button_without_session_keeps_purchase_next(self):
        """Visitor buy links carry next to the purchase page of their movie."""
        response = self.client.get(reverse('home'))
        for movie in (self.pelicula_cartelera_1, self.pelicula_cartelera_2):
            self.assertContains(response, f'next=%2Fcompras%2F{movie.pk}%2F')
        self.assertNotContains(response, '/accounts/login/?next=')

    def test_buy_button_with_session_links_to_purchase_page(self):
        """Authenticated buy links navigate to the purchase page of their movie."""
        from cuentas.models import Cuenta
        user = Cuenta.objects.create_user(
            correo='buyer@example.com',
            nombre='Buyer'
        )
        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        for movie in (self.pelicula_cartelera_1, self.pelicula_cartelera_2):
            self.assertContains(response, f'href="/compras/{movie.pk}/"')
        self.assertNotContains(response, 'href="#"')

    def test_nav_login_has_no_purchase_next(self):
        """Nav Login keeps the plain Google flow; it does not inherit the buy next."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'href="/accounts/google/login/?process=login"')


class AuthRedirectSettingsTests(SimpleTestCase):
    """Guard against losing the post-login/logout landing page."""

    def test_login_redirect_targets_home(self):
        self.assertEqual(settings.LOGIN_REDIRECT_URL, '/')

    def test_logout_redirect_targets_home(self):
        self.assertEqual(settings.LOGOUT_REDIRECT_URL, '/')


class FaviconTests(SimpleTestCase):
    def test_favicon_returns_placeholder_icon(self):
        response = self.client.get('/favicon.ico')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/x-icon')


class GestionViewTests(TestCase):
    def setUp(self):
        from datetime import timedelta

        from cuentas.models import Cuenta
        from funciones.models import Funcion
        from peliculas.models import Pelicula
        from salas.models import Sala
        from django.utils import timezone

        self.admin = Cuenta.objects.create_superuser(
            'gestion-admin@example.com', 'Gestión Admin', 'test-password'
        )
        self.common = Cuenta.objects.create_user(
            'gestion-common@example.com', 'Cuenta común'
        )
        self.pelicula = Pelicula.objects.create(
            titulo='Película del dashboard',
            imagen_portada='imgs/dashboard.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Descripción',
            clasificacion='ATP',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )
        self.sala = Sala.objects.create(
            nombre='Sala del dashboard',
            distribucion={'version': 1, 'filas': ['AAA']},
            tipo_sala='2D',
            tipo_sonido='Dolby',
            capacidad=3,
        )
        inicio = timezone.now() + timedelta(days=1)
        self.funcion = Funcion.objects.create(
            funcion_activa=True,
            inicio=inicio,
            fin=inicio + timedelta(minutes=100),
            idioma='Español',
            subtitulada=False,
            distribucion={'version': 1, 'filas': ['AAA']},
            disponibilidad=3,
            precio_entrada='1500.00',
            pelicula=self.pelicula,
            sala=self.sala,
            entradas_compradas=0,
        )

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse('gestion'))
        expected = f'{settings.LOGIN_URL}?{urlencode({"next": "/gestion/"}, safe="/")}'
        self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_common_account_is_redirected_home(self):
        self.client.force_login(self.common)

        response = self.client.get(reverse('gestion'))

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_staff_sees_dashboard_with_movies_selected_by_default(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('gestion'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion.html')
        self.assertContains(response, 'data-management-tab="movies"')
        self.assertContains(response, 'aria-pressed="true"')
        self.assertContains(response, 'data-management-panel="movies"')
        self.assertContains(response, 'Película del dashboard')

    def test_dashboard_prerenders_all_three_listings_and_five_controls(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('gestion'))

        for value in (
            'Película del dashboard',
            'Sala del dashboard',
            'data-management-panel="functions"',
            'data-management-panel="rooms"',
            'Películas',
            'Funciones',
            'Salas',
            'Cuentas',
            'Estadísticas',
        ):
            self.assertContains(response, value)
        self.assertEqual(response.content.count(b'data-management-tab='), 4)
        self.assertContains(response, 'data-management-tab="statistics"')
        self.assertNotContains(response, 'data-management-tab="statistics" disabled')
        self.assertContains(response, 'Estadísticas')
        self.assertContains(response, reverse('admin:index'))

    def test_dashboard_prerenders_statistics_panel_for_all_periods(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('gestion'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-management-panel="statistics"')
        self.assertEqual(response.content.count(b'data-stats-period='), 6)
        for period in ('semanal', 'mensual', 'anual'):
            self.assertEqual(
                response.content.count(f'data-stats-period="{period}"'.encode()), 2
            )
        self.assertContains(response, 'Recaudación por género · Semanal')
        self.assertContains(response, 'Recaudación por género · Mensual')
        self.assertContains(response, 'Recaudación por género · Anual')
        self.assertContains(response, 'data-stats-switch')
        self.assertContains(response, 'data-stats-period-label')
        self.assertContains(response, 'estadisticas/js/periodos.js')

    def test_admin_index_uses_movieup_shell_and_accounts_subnav(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="site-header site-header--admin"')
        self.assertContains(response, '<div class="site-footer" id="site-footer">', html=False)
        self.assertNotContains(response, '<footer class="site-footer"', html=False)
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, 'Estadísticas')

    def test_account_changelist_and_edit_remain_available_in_admin(self):
        from cuentas.models import Cuenta

        account = Cuenta.objects.create_user('change-me@example.com', 'Change Me')
        self.client.force_login(self.admin)
        changelist_url = reverse('admin:cuentas_cuenta_changelist')

        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, account.correo)

        response = self.client.post(
            reverse('admin:cuentas_cuenta_change', args=[account.pk]),
            {'is_active': 'on', 'is_staff': 'on', '_save': 'Save'},
        )

        self.assertEqual(response.status_code, 302)
        account.refresh_from_db()
        self.assertTrue(account.is_staff)
        self.assertTrue(account.is_superuser)


class AuthPanelTests(TestCase):
    """ui-crud-pages 3.3: panel requests never follow a redirect."""

    panel = {'X-Panel-Request': '1'}

    def _panel_urls(self):
        return (
            reverse('gestion'),
            reverse('salas:sala_list'),
            reverse('salas:sala_detail', args=[1]),
            reverse('peliculas:pelicula_create'),
            reverse('funciones:funcion_delete', args=[1]),
        )

    def test_expired_session_answers_401_with_the_login_url(self):
        expected = f'{settings.LOGIN_URL}?{urlencode({"next": "/gestion/"}, safe="/")}'

        for url in self._panel_urls():
            with self.subTest(url=url):
                response = self.client.get(url, headers=self.panel)

                self.assertEqual(response.status_code, 401)
                self.assertEqual(response['X-Panel-Redirect'], expected)

    def test_full_page_without_session_keeps_the_login_redirect(self):
        response = self.client.get(reverse('salas:sala_list'))

        expected = f'{settings.LOGIN_URL}?{urlencode({"next": "/salas/"}, safe="/")}'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected)

    def test_common_account_is_sent_home_from_the_panel(self):
        from cuentas.models import Cuenta

        user = Cuenta.objects.create_user('panel-common@example.com', 'Panel Common')
        self.client.force_login(user)

        response = self.client.get(reverse('salas:sala_list'), headers=self.panel)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_staff_reaches_the_panel_fragment(self):
        from cuentas.models import Cuenta

        staff = Cuenta.objects.create_user(
            'panel-staff@example.com', 'Panel Staff', is_staff=True
        )
        self.client.force_login(staff)

        response = self.client.get(reverse('salas:sala_list'), headers=self.panel)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'list')
