from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CuentaManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, correo, nombre, password, **extra_fields):
        if not correo:
            raise ValueError('The email address must be set.')

        correo = self.normalize_email(correo.strip()).lower()
        user = self.model(correo=correo, nombre=nombre, **extra_fields)
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, correo, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(correo, nombre, password, **extra_fields)

    def create_superuser(self, correo, nombre, password=None, **extra_fields):
        if not password:
            raise ValueError('A superuser must have a password for recovery access.')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields['is_staff'] is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields['is_superuser'] is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(correo, nombre, password, **extra_fields)


class Cuenta(AbstractUser):
    username = None
    email = None
    first_name = None
    last_name = None

    correo = models.EmailField(max_length=254, unique=True)
    nombre = models.CharField(max_length=150)
    foto_url = models.URLField(max_length=500, blank=True, default='')

    objects = CuentaManager()

    USERNAME_FIELD = 'correo'
    EMAIL_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'cuenta'

    def clean(self):
        # AbstractUser.clean() assumes the default `email` field still exists.
        super(AbstractUser, self).clean()
        self.correo = self.__class__.objects.normalize_email(self.correo).lower()

    def get_full_name(self):
        return self.nombre

    def get_short_name(self):
        return self.nombre
