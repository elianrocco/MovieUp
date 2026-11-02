from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Cuenta


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
