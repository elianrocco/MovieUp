from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from threading import Barrier
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.contrib.admin.sites import AdminSite
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.db.models.deletion import ProtectedError
from django.template.loader import render_to_string
from django.test import Client, RequestFactory, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from entradas.models import Entrada
from funciones.models import Funcion
from peliculas.models import Pelicula
from salas.models import Sala

from .adapters import CuentaSocialAccountAdapter
from .admin import CuentaAdmin
from .models import Cuenta
from .services import list_cuentas, promote_first_admin, toggle_permisos


TEST_SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APPS': [
            {
                'client_id': 'test-client-id',
                'secret': 'test-client-secret',
                'key': '',
            },
        ],
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    },
}

FAKE_ACCESS_TOKEN = {
    'access_token': 'fake-access-token',
    'token_type': 'Bearer',
    'expires_in': 3600,
    'id_token': 'fake-id-token',
}


class CuentaModelTests(TestCase):
    def test_model_uses_email_identity_and_expected_table(self):
        self.assertEqual(Cuenta.USERNAME_FIELD, 'correo')
        self.assertEqual(Cuenta.EMAIL_FIELD, 'correo')
        self.assertEqual(Cuenta._meta.db_table, 'cuenta')

        for removed_field in ('username', 'email', 'first_name', 'last_name'):
            with self.assertRaises(FieldDoesNotExist):
                Cuenta._meta.get_field(removed_field)

    def test_create_user_normalizes_email_and_sets_unusable_password(self):
        user = Cuenta.objects.create_user('  CineFilo@Example.COM ', 'Cinefilo')

        self.assertEqual(user.correo, 'cinefilo@example.com')
        self.assertEqual(user.nombre, 'Cinefilo')
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.check_password('any-password'))

    def test_correo_is_unique(self):
        Cuenta.objects.create_user('cinefilo@example.com', 'First')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Cuenta.objects.create_user('CINEFILO@example.com', 'Second')

    def test_create_superuser_grants_full_admin_and_usable_password(self):
        user = Cuenta.objects.create_superuser(
            'admin@example.com',
            'Administrator',
            password='Strong-test-password-123',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('Strong-test-password-123'))
        self.assertTrue(user.has_usable_password())


class CuentaManagementServiceTests(TestCase):
    def setUp(self):
        self.admin = Cuenta.objects.create_superuser(
            'admin@example.com', 'Administrator', password='Strong-test-password-123'
        )
        self.common = Cuenta.objects.create_user('common@example.com', 'Common User')

    def test_list_cuentas_orders_by_email(self):
        Cuenta.objects.create_user('aaa@example.com', 'First')

        self.assertEqual(
            list(list_cuentas().values_list('correo', flat=True)),
            ['aaa@example.com', 'admin@example.com', 'common@example.com'],
        )

    def test_toggle_permisos_promotes_common_account_with_both_flags(self):
        updated = toggle_permisos(self.common, self.admin)

        self.assertTrue(updated.is_staff)
        self.assertTrue(updated.is_superuser)

    def test_toggle_permisos_demotes_admin_with_both_flags(self):
        updated = toggle_permisos(self.common, self.admin)
        updated = toggle_permisos(updated, self.admin)

        self.assertFalse(updated.is_staff)
        self.assertFalse(updated.is_superuser)

    def test_toggle_permisos_rejects_the_requesting_account(self):
        with self.assertRaisesMessage(
            ValueError, 'No se pueden cambiar los permisos de la cuenta actual.'
        ):
            toggle_permisos(self.admin, self.admin)

        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)


class CuentaManagementViewTests(TestCase):
    panel = {'HTTP_X_PANEL_REQUEST': '1'}

    def setUp(self):
        self.admin = Cuenta.objects.create_superuser(
            'admin@example.com', 'Administrator', password='Strong-test-password-123'
        )
        self.common = Cuenta.objects.create_user('common@example.com', 'Common User')

    def test_panel_post_toggles_permissions_and_returns_list_fragment(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('cuentas:cuenta_permiso_update', args=[self.common.pk]),
            **self.panel,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'list')
        self.assertContains(response, 'Administrador')
        self.common.refresh_from_db()
        self.assertTrue(self.common.is_staff)
        self.assertTrue(self.common.is_superuser)

    def test_post_without_panel_header_redirects_to_management(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('cuentas:cuenta_permiso_update', args=[self.common.pk])
        )

        self.assertRedirects(response, reverse('gestion'), fetch_redirect_response=False)
        self.common.refresh_from_db()
        self.assertTrue(self.common.is_staff)
        self.assertTrue(self.common.is_superuser)

    def test_non_post_request_redirects_to_management(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse('cuentas:cuenta_permiso_update', args=[self.common.pk])
        )

        self.assertRedirects(response, reverse('gestion'), fetch_redirect_response=False)
        self.common.refresh_from_db()
        self.assertFalse(self.common.is_staff)
        self.assertFalse(self.common.is_superuser)

    def test_common_account_cannot_toggle_permissions(self):
        self.client.force_login(self.common)

        response = self.client.post(
            reverse('cuentas:cuenta_permiso_update', args=[self.admin.pk]),
            **self.panel,
        )

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)

    def test_panel_post_cannot_toggle_the_requesting_account(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('cuentas:cuenta_permiso_update', args=[self.admin.pk]),
            **self.panel,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Panel-View'], 'list')
        self.assertContains(response, 'No se pueden cambiar los permisos')
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)

    def test_listing_template_shows_only_account_fields_and_permission_switches(self):
        html = render_to_string(
            'cuentas/_listado.html',
            {
                'cuentas': [self.admin, self.common],
                'current_user': self.admin,
            },
        )

        for label in (
            'Correo',
            'Nombre',
            'Permisos',
            'Acciones',
            'Administrador',
            'Usuario común',
        ):
            self.assertIn(label, html)
        self.assertEqual(html.count('data-panel-form'), 2)
        self.assertEqual(html.count('role="switch"'), 2)
        self.assertEqual(html.count(' disabled title='), 1)
        self.assertNotIn('data-panel-link', html)
        self.assertNotIn('Crear', html)
        self.assertNotIn('Editar', html)
        self.assertNotIn('Eliminar', html)


class CuentaSocialAccountAdapterTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/accounts/google/login/callback/')
        self.request.session = SessionStore()
        self.adapter = CuentaSocialAccountAdapter()
        self.provider = GoogleProvider(
            self.request,
            app=SocialApp(
                provider='google',
                name='Test Google OAuth',
                client_id='test-client-id',
                secret='test-client-secret',
            ),
        )

    def create_sociallogin(self, profile):
        return self.provider.sociallogin_from_response(self.request, profile)

    def test_populates_correo_and_nombre_from_verified_google_profile(self):
        sociallogin = self.create_sociallogin(
            {
                'sub': 'google-user-1',
                'email': 'CineFilo@example.com',
                'email_verified': True,
                'name': 'Cine Filo Completo',
                'given_name': 'Cine',
                'family_name': 'Filo',
            }
        )

        self.assertEqual(sociallogin.user.correo, 'cinefilo@example.com')
        self.assertEqual(sociallogin.user.nombre, 'Cine Filo Completo')
        self.assertFalse(sociallogin.user.has_usable_password())
        self.assertTrue(
            self.adapter.is_open_for_signup(self.request, sociallogin)
        )

        sociallogin.save(self.request)
        created = Cuenta.objects.get(correo='cinefilo@example.com')
        self.assertEqual(created.nombre, 'Cine Filo Completo')
        self.assertFalse(created.has_usable_password())

    def test_populates_foto_url_from_google_profile(self):
        picture_url = 'https://lh3.googleusercontent.com/a/photo123'
        sociallogin = self.create_sociallogin(
            {
                'sub': 'google-user-photo',
                'email': 'con.foto@example.com',
                'email_verified': True,
                'name': 'Con Foto',
                'picture': picture_url,
            }
        )

        self.assertEqual(sociallogin.user.foto_url, picture_url)

        sociallogin.save(self.request)
        created = Cuenta.objects.get(correo='con.foto@example.com')
        self.assertEqual(created.foto_url, picture_url)

    def test_unverified_google_email_cannot_create_an_account(self):
        sociallogin = self.create_sociallogin(
            {
                'sub': 'google-user-unverified',
                'email': 'cinefilo@example.com',
                'email_verified': False,
                'name': 'Cine Filo',
            }
        )

        self.assertFalse(
            self.adapter.is_open_for_signup(self.request, sociallogin)
        )

    def test_existing_google_identity_reuses_the_existing_account(self):
        existing = Cuenta.objects.create_user('cinefilo@example.com', 'Existing Name')
        SocialAccount.objects.create(
            user=existing,
            provider='google',
            uid='google-user-existing',
            extra_data={},
        )
        sociallogin = self.create_sociallogin(
            {
                'sub': 'google-user-existing',
                'email': 'changed@example.com',
                'email_verified': True,
                'name': 'Changed Google Name',
            }
        )

        sociallogin.lookup()

        self.assertTrue(sociallogin.is_existing)
        self.assertEqual(sociallogin.user.pk, existing.pk)
        self.assertEqual(Cuenta.objects.count(), 1)
        self.assertEqual(sociallogin.user.correo, 'cinefilo@example.com')
        self.assertEqual(sociallogin.user.nombre, 'Existing Name')


class CuentaSocialAccountNameFallbackTests(TestCase):
    def test_name_falls_back_to_email_local_part(self):
        request = RequestFactory().get('/accounts/google/login/callback/')
        request.session = SessionStore()
        provider = GoogleProvider(
            request,
            app=SocialApp(
                provider='google',
                name='Test Google OAuth',
                client_id='test-client-id',
                secret='test-client-secret',
            ),
        )
        sociallogin = provider.sociallogin_from_response(
            request,
            {
                'sub': 'google-user-no-name',
                'email': 'cinefilo@example.com',
                'email_verified': True,
            },
        )

        self.assertEqual(sociallogin.user.nombre, 'cinefilo')

    def test_name_uses_google_given_and_family_names_before_email_fallback(self):
        request = RequestFactory().get('/accounts/google/login/callback/')
        provider = GoogleProvider(
            request,
            app=SocialApp(
                provider='google',
                name='Test Google OAuth',
                client_id='test-client-id',
                secret='test-client-secret',
            ),
        )
        sociallogin = provider.sociallogin_from_response(
            request,
            {
                'sub': 'google-user-partial-name',
                'email': 'cinefilo@example.com',
                'email_verified': True,
                'given_name': 'Cine',
                'family_name': 'Filo',
            },
        )

        self.assertEqual(sociallogin.user.nombre, 'Cine Filo')


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    SOCIALACCOUNT_PROVIDERS=TEST_SOCIALACCOUNT_PROVIDERS,
)
class GoogleOAuthCallbackTests(TestCase):
    def google_login(self, profile, client=None):
        client = client or Client()
        start_response = client.post(
            reverse('google_login'),
            {'process': 'login'},
        )
        state = parse_qs(urlparse(start_response['Location']).query)['state'][0]

        with (
            patch(
                'allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter.get_access_token_data',
                return_value=FAKE_ACCESS_TOKEN,
            ),
            patch(
                'allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter._decode_id_token',
                return_value=profile,
            ),
        ):
            response = client.get(
                reverse('google_callback'),
                {'code': 'fake-authorization-code', 'state': state},
            )

        return client, response

    def test_first_verified_google_login_creates_full_admin_account(self):
        profile = {
            'sub': 'google-admin-1',
            'email': 'first@example.com',
            'email_verified': True,
            'name': 'First Administrator',
            'picture': 'https://example.com/avatar.png',
        }

        client, response = self.google_login(profile)

        self.assertIn(response.status_code, (200, 302))
        user = Cuenta.objects.get(correo='first@example.com')
        self.assertEqual(user.nombre, 'First Administrator')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(client.get('/admin/').status_code, 200)

    def test_repeated_google_callback_reuses_account_and_keeps_profile_immutable(self):
        profile = {
            'sub': 'google-repeat-1',
            'email': 'repeat@example.com',
            'email_verified': True,
            'name': 'Original Name',
            'picture': 'https://example.com/avatar.png',
        }
        client, _ = self.google_login(profile)
        client.logout()

        changed_profile = {
            **profile,
            'email': 'changed@example.com',
            'name': 'Changed Name',
        }
        _, response = self.google_login(changed_profile, client)

        self.assertIn(response.status_code, (200, 302))
        self.assertEqual(Cuenta.objects.count(), 1)
        user = Cuenta.objects.get()
        self.assertEqual(user.correo, 'repeat@example.com')
        self.assertEqual(user.nombre, 'Original Name')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_unverified_google_email_does_not_create_an_account(self):
        profile = {
            'sub': 'google-unverified-1',
            'email': 'unverified@example.com',
            'email_verified': False,
            'name': 'Unverified User',
            'picture': 'https://example.com/avatar.png',
        }

        _, response = self.google_login(profile)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cuenta.objects.filter(correo='unverified@example.com').exists())

    def test_later_google_signup_remains_a_regular_account(self):
        Cuenta.objects.create_superuser(
            'existing-admin@example.com',
            'Existing Admin',
            password='Strong-test-password-123',
        )
        profile = {
            'sub': 'google-regular-1',
            'email': 'regular@example.com',
            'email_verified': True,
            'name': 'Regular User',
            'picture': 'https://example.com/avatar.png',
        }

        client, response = self.google_login(profile)

        self.assertIn(response.status_code, (200, 302))
        user = Cuenta.objects.get(correo='regular@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertNotEqual(client.get('/admin/').status_code, 200)


class CuentaAdminTests(TestCase):
    def setUp(self):
        self.admin_user = Cuenta.objects.create_superuser(
            'admin@example.com',
            'Administrator',
            password='Strong-test-password-123',
        )
        self.request = RequestFactory().post('/admin/cuentas/cuenta/')
        self.request.user = self.admin_user
        self.model_admin = CuentaAdmin(Cuenta, AdminSite())

    def create_account_with_entry(self, correo, nombre):
        cuenta = Cuenta.objects.create_user(correo, nombre)
        pelicula = Pelicula.objects.create(
            titulo=f'Película {nombre}',
            imagen_portada='imgs/test.jpg',
            genero='Drama',
            duracion_minutos=90,
            descripcion='Descripción de prueba',
            clasificacion='ATP',
            fecha_estreno='2026-01-01',
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )
        distribucion = {'version': 1, 'filas': ['R']}
        sala = Sala.objects.create(
            nombre=f'Sala {nombre}',
            distribucion=distribucion,
            tipo_sala='2D',
            tipo_sonido='Dolby',
            capacidad=1,
        )
        inicio = timezone.now() + timedelta(days=2)
        funcion = Funcion.objects.create(
            funcion_activa=True,
            inicio=inicio,
            fin=inicio + timedelta(minutes=90),
            idioma='Español',
            subtitulada=False,
            distribucion=distribucion,
            disponibilidad=0,
            precio_entrada='1500.00',
            pelicula=pelicula,
            sala=sala,
            entradas_compradas=1,
        )
        entrada = Entrada.objects.create(
            funcion=funcion,
            cuenta=cuenta,
            codigo=f'ENTRY{cuenta.pk:07d}',
            l_fila='A',
            n_asiento=1,
        )
        return cuenta, entrada

    def test_profile_fields_are_read_only_and_accounts_cannot_be_added_manually(self):
        user = Cuenta.objects.create_user('customer@example.com', 'Customer')

        self.assertEqual(self.model_admin.readonly_fields, ('correo', 'nombre'))
        self.assertNotIn('is_superuser', self.model_admin.get_fields(self.request, user))
        self.assertFalse(self.model_admin.has_add_permission(self.request))

    def test_admin_flag_controls_both_django_privilege_flags(self):
        user = Cuenta.objects.create_user('customer@example.com', 'Customer')
        user.is_staff = True
        self.model_admin.save_model(self.request, user, form=None, change=True)

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        user.is_staff = False
        self.model_admin.save_model(self.request, user, form=None, change=True)

        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_accounts_without_entries_can_be_deleted_individually_and_in_bulk(self):
        individual = Cuenta.objects.create_user('individual@example.com', 'Individual')
        bulk = Cuenta.objects.create_user('bulk@example.com', 'Bulk')

        self.model_admin.delete_model(self.request, individual)
        self.model_admin.delete_queryset(
            self.request,
            Cuenta.objects.filter(pk=bulk.pk),
        )

        self.assertFalse(Cuenta.objects.filter(pk__in=[individual.pk, bulk.pk]).exists())

    def test_accounts_with_entries_cannot_be_deleted_individually(self):
        cuenta, entrada = self.create_account_with_entry('protected@example.com', 'Protected')

        with self.assertRaisesRegex(ProtectedError, 'No se puede eliminar'):
            self.model_admin.delete_model(self.request, cuenta)

        self.assertTrue(Cuenta.objects.filter(pk=cuenta.pk).exists())
        self.assertTrue(Entrada.objects.filter(pk=entrada.pk).exists())

    def test_bulk_delete_is_rejected_if_any_account_has_entries(self):
        protected, entrada = self.create_account_with_entry(
            'bulk-protected@example.com', 'Bulk Protected'
        )
        unprotected = Cuenta.objects.create_user('bulk-free@example.com', 'Bulk Free')

        with self.assertRaisesRegex(ProtectedError, 'No se pueden eliminar'):
            self.model_admin.delete_queryset(
                self.request,
                Cuenta.objects.filter(pk__in=[protected.pk, unprotected.pk]),
            )

        self.assertTrue(Cuenta.objects.filter(pk__in=[protected.pk, unprotected.pk]).count() == 2)
        self.assertTrue(Entrada.objects.filter(pk=entrada.pk).exists())

    def test_entry_deletion_guards_are_active_for_both_admin_delete_paths(self):
        source = Path(__file__).with_name('admin.py').read_text(encoding='utf-8')

        self.assertEqual(source.count('TODO(entrada)'), 0)


class FirstAdminPromotionTests(TestCase):
    def test_promotes_new_account_when_no_admin_exists(self):
        user = Cuenta.objects.create_user('first@example.com', 'First User')

        promote_first_admin(user)

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_does_not_promote_new_account_when_admin_exists(self):
        Cuenta.objects.create_superuser(
            'existing-admin@example.com',
            'Existing Admin',
            password='Strong-test-password-123',
        )
        user = Cuenta.objects.create_user('regular@example.com', 'Regular User')

        promote_first_admin(user)

        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class FirstAdminPromotionConcurrencyTests(TransactionTestCase):
    def test_concurrent_first_signups_promote_exactly_one_admin(self):
        if connection.vendor != 'mysql':
            self.skipTest('MySQL GET_LOCK is required for this concurrency test.')

        users = [
            Cuenta.objects.create_user('first@example.com', 'First User'),
            Cuenta.objects.create_user('second@example.com', 'Second User'),
        ]
        barrier = Barrier(2)

        def promote(user_id):
            close_old_connections()
            try:
                user = Cuenta.objects.get(pk=user_id)
                barrier.wait(timeout=10)
                promote_first_admin(user)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(promote, user.pk) for user in users]
            for future in futures:
                future.result(timeout=20)

        self.assertEqual(Cuenta.objects.filter(is_staff=True).count(), 1)
        self.assertEqual(Cuenta.objects.filter(is_superuser=True).count(), 1)
