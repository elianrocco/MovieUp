"""Access-control decorators shared across the project's apps."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def staff_required(view_func):
    """Allow only staff accounts through a view.

    Anonymous visitors are sent to the login screen keeping ``?next=``;
    authenticated non-staff accounts are sent to the home page.
    """

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/')
        return view_func(request, *args, **kwargs)

    return wrapper
