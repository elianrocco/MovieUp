from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import services


@login_required
def entrada_list(request):
    return render(
        request,
        'entradas/list.html',
        {'entradas': services.listar_entradas(request.user.pk)},
    )


@login_required
def entrada_detail(request, pk):
    entrada = services.obtener_entrada(pk, request.user.pk)
    return render(request, 'entradas/detail.html', {'entrada': entrada})


@login_required
@require_POST
def entrada_reembolsar(request, pk):
    entrada = services.obtener_entrada(pk, request.user.pk)
    try:
        services.eliminar_entrada(entrada.pk, 'reembolso')
    except ValueError as exc:
        return render(
            request,
            'entradas/detail.html',
            {'entrada': entrada, 'error': str(exc)},
        )
    return redirect('entradas:entrada_list')


@staff_member_required
def entrada_validar(request):
    context = {}
    if request.method == 'POST':
        entrada = services.validar_entrada(request.POST.get('codigo', ''))
        if entrada is None:
            context['mensaje'] = 'No se encontró ninguna entrada activa con ese código.'
        else:
            context.update(
                {
                    'mensaje': 'Entrada validada correctamente.',
                    'entrada': entrada,
                }
            )

    return render(request, 'entradas/validar.html', context)
