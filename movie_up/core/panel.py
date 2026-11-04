"""Fragment rendering for the management panel (ui-crud-pages, design D1/D2).

The panel calls the very same views as the full pages, but adds the
``X-Panel-Request: 1`` header. Those views then answer their app partial
(``salas/detail.html`` -> ``salas/_detail.html``) instead of the whole
document, plus the ``X-Panel-View`` header that tells the client which
state it just received.

Panel responses never redirect: a successful POST answers the app list
fragment, and a dead session answers ``401`` with the URL the client must
navigate to (``X-Panel-Redirect``), so a login page is never injected
into the panel.
"""

from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

PANEL_REQUEST_HEADER = 'X-Panel-Request'
PANEL_VIEW_HEADER = 'X-Panel-View'
PANEL_REDIRECT_HEADER = 'X-Panel-Redirect'

#: ``list.html`` pages are built from ``_listado.html``; every other page
#: keeps a ``_``-prefixed sibling with the same body.
PANEL_PARTIAL_OVERRIDES = {'list.html': '_listado.html'}

#: Panel requests must always return to the management view.
PANEL_RETURN_URL_NAME = 'gestion'


def is_panel_request(request):
    """True when the management panel asked for a fragment, not a page."""
    return request.headers.get(PANEL_REQUEST_HEADER) == '1'


def panel_partial(template_name):
    """Map a full-page template to its panel partial.

    ``salas/detail.html`` -> ``salas/_detail.html``,
    ``salas/list.html`` -> ``salas/_listado.html``.
    """
    prefix, _, basename = template_name.rpartition('/')

    if basename in PANEL_PARTIAL_OVERRIDES:
        basename = PANEL_PARTIAL_OVERRIDES[basename]
    elif not basename.startswith('_'):
        basename = f'_{basename}'

    return f'{prefix}/{basename}' if prefix else basename


def render_panel(request, template_name, context, view):
    """Render the full page, or the panel fragment flagged with ``view``."""
    if not is_panel_request(request):
        return render(request, template_name, context)

    response = render(request, panel_partial(template_name), context)
    response[PANEL_VIEW_HEADER] = view
    return response


def panel_list_or_redirect(request, redirect_response, template_name, context):
    """Keep the redirect for the browser, answer the list fragment to the panel."""
    if not is_panel_request(request):
        return redirect_response

    return render_panel(request, template_name, context, view='list')


def panel_unauthorized():
    """``401`` plus the login URL that brings the user back to the panel."""
    response = HttpResponse(status=401)
    response[PANEL_REDIRECT_HEADER] = redirect_to_login(
        reverse(PANEL_RETURN_URL_NAME)
    ).url
    return response
