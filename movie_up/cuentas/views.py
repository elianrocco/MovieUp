from django.shortcuts import redirect

from core.decorators import staff_required
from core.panel import is_panel_request, render_panel

from . import services


def _list_context(request, error=None):
    context = {'cuentas': services.list_cuentas(), 'current_user': request.user}
    if error is not None:
        context['error'] = str(error)
    return context


@staff_required
def cuenta_permiso_update(request, pk):
    if request.method != 'POST':
        return redirect('gestion')

    cuenta = services.get_cuenta(pk)
    try:
        services.toggle_permisos(cuenta, request.user)
    except ValueError as exc:
        if is_panel_request(request):
            return render_panel(
                request,
                'cuentas/_listado.html',
                _list_context(request, error=exc),
                view='list',
            )
        return redirect('gestion')

    if is_panel_request(request):
        return render_panel(
            request,
            'cuentas/_listado.html',
            _list_context(request),
            view='list',
        )
    return redirect('gestion')
