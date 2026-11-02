from django.db import connection, transaction

from .models import Cuenta


FIRST_ADMIN_LOCK_NAME = 'movieup:cuentas:first-admin'
FIRST_ADMIN_LOCK_TIMEOUT_SECONDS = 10


def promote_first_admin(user):
    if user.pk is None:
        raise ValueError('The account must be saved before administrator promotion.')

    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT GET_LOCK(%s, %s)',
            [FIRST_ADMIN_LOCK_NAME, FIRST_ADMIN_LOCK_TIMEOUT_SECONDS],
        )
        lock_acquired = cursor.fetchone()[0]

    if lock_acquired != 1:
        raise RuntimeError('Could not acquire the first-administrator lock.')

    try:
        with transaction.atomic():
            another_admin_exists = (
                Cuenta.objects.filter(is_staff=True).exclude(pk=user.pk).exists()
            )
            if not another_admin_exists:
                Cuenta.objects.filter(pk=user.pk).update(
                    is_staff=True,
                    is_superuser=True,
                )
                user.is_staff = True
                user.is_superuser = True
        return user
    finally:
        with connection.cursor() as cursor:
            cursor.execute('SELECT RELEASE_LOCK(%s)', [FIRST_ADMIN_LOCK_NAME])
            lock_released = cursor.fetchone()[0]
        if lock_released != 1:
            raise RuntimeError('Could not release the first-administrator lock.')
