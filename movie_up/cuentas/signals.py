from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from .services import promote_first_admin


@receiver(user_signed_up, dispatch_uid='cuentas.promote_first_admin')
def promote_first_admin_on_signup(request, user, **kwargs):
    promote_first_admin(user)
