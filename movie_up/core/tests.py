from types import SimpleNamespace
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from .decorators import staff_required


@staff_required
def protected_view(request):
    return HttpResponse('ok')


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
