from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


def _clean_text(value):
    if not isinstance(value, str):
        return ''
    return ' '.join(value.split())


class CuentaSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        extra_data = sociallogin.account.extra_data or {}

        email = _clean_text(data.get('email') or extra_data.get('email')).lower()
        user.correo = email

        given_name = data.get('first_name') or extra_data.get('given_name')
        family_name = data.get('last_name') or extra_data.get('family_name')
        combined_name = ' '.join(
            name for name in (_clean_text(given_name), _clean_text(family_name)) if name
        )

        name_candidates = (
            extra_data.get('name'),
            data.get('name'),
            combined_name,
            email.partition('@')[0],
        )
        user.nombre = next(
            (cleaned for candidate in name_candidates if (cleaned := _clean_text(candidate))),
            '',
        )
        return user

    def is_open_for_signup(self, request, sociallogin):
        if not super().is_open_for_signup(request, sociallogin):
            return False

        user_email = _clean_text(getattr(sociallogin.user, 'correo', '')).casefold()
        return bool(user_email) and any(
            email_address.verified
            and _clean_text(email_address.email).casefold() == user_email
            for email_address in sociallogin.email_addresses
        )
