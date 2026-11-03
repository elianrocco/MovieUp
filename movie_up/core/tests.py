from types import SimpleNamespace
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.template import engines
from django.test import RequestFactory, SimpleTestCase, TestCase

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
