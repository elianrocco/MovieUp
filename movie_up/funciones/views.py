from django.shortcuts import redirect, render
from django.utils import timezone

from peliculas import services as peliculas_services
from salas import services as salas_services

from . import services


FORM_FIELDS = (
    'pelicula',
    'sala',
    'inicio',
    'idioma',
    'subtitulada',
    'funcion_activa',
    'precio_entrada',
)


def _format_datetime(value):
    if value is None:
        return ''
    return timezone.localtime(value).strftime('%Y-%m-%dT%H:%M')


def _form_values(funcion=None, post=None):
    values = {field: '' for field in FORM_FIELDS}
    if funcion is not None:
        values.update(
            {
                'pelicula': str(funcion.pelicula_id),
                'sala': str(funcion.sala_id),
                'inicio': _format_datetime(funcion.inicio),
                'idioma': funcion.idioma,
                'subtitulada': str(funcion.subtitulada).lower(),
                'funcion_activa': str(funcion.funcion_activa).lower(),
                'precio_entrada': str(funcion.precio_entrada),
            }
        )

    if post is not None:
        for field in FORM_FIELDS:
            if field in post:
                values[field] = post.get(field, '')
    return values


def _form_context(funcion=None, post=None, error=None):
    now = timezone.now()
    min_inicio = ''
    if funcion is None or funcion.inicio >= now:
        min_inicio = _format_datetime(now)

    context = {
        'funcion': funcion,
        'form_values': _form_values(funcion=funcion, post=post),
        'peliculas': peliculas_services.list_peliculas(),
        'salas': salas_services.list_salas(),
        'min_inicio': min_inicio,
    }
    if error is not None:
        context['error'] = str(error)
    return context


def funcion_list(request):
    return render(
        request,
        'funciones/list.html',
        {'funciones': services.list_funciones()},
    )


def funcion_detail(request, pk):
    funcion = services.get_funcion(pk)
    return render(request, 'funciones/detail.html', {'funcion': funcion})


def funcion_create(request):
    if request.method == 'POST':
        try:
            services.create_funcion(request.POST.dict())
            return redirect('funciones:funcion_list')
        except ValueError as exc:
            return render(
                request,
                'funciones/form.html',
                _form_context(post=request.POST, error=exc),
            )

    return render(request, 'funciones/form.html', _form_context())


def funcion_update(request, pk):
    funcion = services.get_funcion(pk)

    if request.method == 'POST':
        try:
            services.update_funcion(pk, request.POST.dict())
            return redirect('funciones:funcion_detail', pk=pk)
        except ValueError as exc:
            funcion.refresh_from_db()
            return render(
                request,
                'funciones/form.html',
                _form_context(funcion=funcion, post=request.POST, error=exc),
            )

    return render(
        request,
        'funciones/form.html',
        _form_context(funcion=funcion),
    )


def funcion_delete(request, pk):
    if request.method == 'POST':
        try:
            services.delete_funcion(pk)
            return redirect('funciones:funcion_list')
        except ValueError as exc:
            funcion = services.get_funcion(pk)
            return render(
                request,
                'funciones/confirm_delete.html',
                {'funcion': funcion, 'error': str(exc)},
            )

    funcion = services.get_funcion(pk)
    return render(request, 'funciones/confirm_delete.html', {'funcion': funcion})
