import json

from django.shortcuts import redirect, render

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


def sala_list(request):
    return render(request, 'salas/list.html', {'salas': services.list_salas()})


def sala_detail(request, pk):
    sala = services.get_sala(pk)
    return render(request, 'salas/detail.html', {'sala': sala})


def sala_create(request):
    if request.method == 'POST':
        data = request.POST.dict()
        try:
            services.create_sala(data)
            return redirect('salas:sala_list')
        except ValueError as exc:
            return render(
                request,
                'salas/form.html',
                {
                    'error': str(exc),
                    'form_values': _form_values(post=request.POST),
                    'initial_distribution': _distribution_from_post(request.POST),
                },
            )

    return render(
        request,
        'salas/form.html',
        {'form_values': _form_values(), 'initial_distribution': None},
    )


def sala_update(request, pk):
    sala = services.get_sala(pk)

    if request.method == 'POST':
        try:
            services.update_sala(pk, request.POST.dict())
            return redirect('salas:sala_detail', pk=pk)
        except ValueError as exc:
            return render(
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
            )

    return render(
        request,
        'salas/form.html',
        {
            'sala': sala,
            'form_values': _form_values(sala=sala),
            'initial_distribution': sala.distribucion,
        },
    )


def sala_delete(request, pk):
    if request.method == 'POST':
        services.delete_sala(pk)
        return redirect('salas:sala_list')

    sala = services.get_sala(pk)
    return render(request, 'salas/confirm_delete.html', {'sala': sala})
