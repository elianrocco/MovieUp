"""Access-control decorators shared across the project's apps."""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .panel import is_panel_request, panel_unauthorized


def staff_required(view_func):
    """Allow only staff accounts through a view.

    Anonymous visitors are sent to the login screen keeping ``?next=``;
    authenticated non-staff accounts are sent to the home page.

    Panel requests (``X-Panel-Request``) never follow a redirect: an
    expired session answers ``401`` with ``X-Panel-Redirect`` so the
    client leaves the panel instead of injecting a login page into it.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if is_panel_request(request):
                return panel_unauthorized()
            return redirect_to_login(request.get_full_path())

        if not request.user.is_staff:
            return redirect('/')

        return view_func(request, *args, **kwargs)

    return wrapper
