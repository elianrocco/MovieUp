import json

from django.shortcuts import redirect

from core.decorators import staff_required
from core.panel import panel_list_or_redirect, render_panel

from . import services


FORM_FIELDS = ('nombre', 'tipo_sala', 'tipo_sonido')


def _form_values(sala=None, post=None):
    return {
        field: (post.get(field) or getattr(sala, field, ''))
        if post is not None
        else getattr(sala, field, '')
        for field in FORM_FIELDS
    }


def _distribution_from_post(post):
    raw_distribution = post.get('distribucion')
    if not raw_distribution:
        return None

    try:
        distribution = json.loads(raw_distribution)
    except json.JSONDecodeError:
        return None

    return distribution if isinstance(distribution, dict) else None


@staff_required
def sala_list(request):
    return render_panel(
        request,
        'salas/list.html',
        {'salas': services.list_salas()},
        view='list',
    )


@staff_required
def sala_detail(request, pk):
    sala = services.get_sala(pk)
    return render_panel(request, 'salas/detail.html', {'sala': sala}, view='detail')


@staff_required
def sala_create(request):
    if request.method == 'POST':
        data = request.POST.dict()
        try:
            services.create_sala(data)
        except ValueError as exc:
            return render_panel(
                request,
                'salas/form.html',
                {
                    'error': str(exc),
                    'form_values': _form_values(post=request.POST),
                    'initial_distribution': _distribution_from_post(request.POST),
                },
                view='form',
            )

        return panel_list_or_redirect(
            request,
            redirect('salas:sala_list'),
            'salas/list.html',
            {'salas': services.list_salas()},
        )

    return render_panel(
        request,
        'salas/form.html',
        {'form_values': _form_values(), 'initial_distribution': None},
        view='form',
    )


@staff_required
def sala_update(request, pk):
    sala = services.get_sala(pk)

    if request.method == 'POST':
        try:
            services.update_sala(pk, request.POST.dict())
        except ValueError as exc:
            return render_panel(
                request,
                'salas/form.html',
                {
                    'sala': sala,
                    'error': str(exc),
                    'form_values': _form_values(sala=sala, post=request.POST),
                    'initial_distribution': (
                        _distribution_from_post(request.POST) or sala.distribucion
                    ),
                },
                view='form',
            )

        return panel_list_or_redirect(
            request,
            redirect('salas:sala_detail', pk=pk),
            'salas/list.html',
            {'salas': services.list_salas()},
        )

    return render_panel(
        request,
        'salas/form.html',
        {
            'sala': sala,
            'form_values': _form_values(sala=sala),
            'initial_distribution': sala.distribucion,
        },
        view='form',
    )


@staff_required
def sala_delete(request, pk):
    if request.method == 'POST':
        try:
            services.delete_sala(pk)
        except ValueError as exc:
            sala = services.get_sala(pk)
            return render_panel(
                request,
                'salas/confirm_delete.html',
                {'sala': sala, 'error': str(exc)},
                view='form',
            )

        return panel_list_or_redirect(
            request,
            redirect('salas:sala_list'),
            'salas/list.html',
            {'salas': services.list_salas()},
        )

    sala = services.get_sala(pk)
    return render_panel(
        request,
        'salas/confirm_delete.html',
        {'sala': sala},
        view='form',
    )
