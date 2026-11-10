from django.db import connection, transaction
from django.http import Http404

from .models import Cuenta


FIRST_ADMIN_LOCK_NAME = 'movieup:cuentas:first-admin'
FIRST_ADMIN_LOCK_TIMEOUT_SECONDS = 10


def list_cuentas():
    return Cuenta.objects.order_by('correo')


def get_cuenta(pk):
    try:
        return Cuenta.objects.get(pk=pk)
    except Cuenta.DoesNotExist as exc:
        raise Http404('Cuenta no encontrada') from exc


@transaction.atomic
def toggle_permisos(cuenta, solicitante):
    if cuenta.pk == solicitante.pk:
        raise ValueError('No se pueden cambiar los permisos de la cuenta actual.')

    cuenta = Cuenta.objects.select_for_update().get(pk=cuenta.pk)
    if cuenta.pk == solicitante.pk:
        raise ValueError('No se pueden cambiar los permisos de la cuenta actual.')

    is_admin = not cuenta.is_staff
    cuenta.is_staff = is_admin
    cuenta.is_superuser = is_admin
    cuenta.save(update_fields=('is_staff', 'is_superuser'))
    return cuenta


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
