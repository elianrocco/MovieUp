from django.shortcuts import redirect

from core.decorators import staff_required
from core.panel import panel_list_or_redirect, render_panel

from . import services


FORM_FIELDS = (
    'titulo',
    'genero',
    'duracion_minutos',
    'descripcion',
    'clasificacion',
    'fecha_estreno',
    'url_trailer',
)


def _form_values(pelicula=None, post=None):
    """Values rendered by the form: posted data wins over the stored row."""
    values = {}

    for field in FORM_FIELDS:
        value = post.get(field) if post is not None else ''
        if not value and pelicula is not None:
            value = getattr(pelicula, field, '')
        values[field] = value if value is not None else ''

    if post is not None:
        values['en_cartelera'] = 'en_cartelera' in post
    else:
        values['en_cartelera'] = bool(getattr(pelicula, 'en_cartelera', False))

    return values


def _form_context(pelicula=None, post=None, error=None):
    context = {
        'pelicula': pelicula,
        'form_values': _form_values(pelicula=pelicula, post=post),
    }
    if error is not None:
        context['error'] = str(error)
    return context


def _list_context():
    return {'peliculas': services.list_peliculas()}


@staff_required
def pelicula_list(request):
    return render_panel(
        request,
        'peliculas/list.html',
        _list_context(),
        view='list',
    )


@staff_required
def pelicula_detail(request, pk):
    pelicula = services.get_pelicula(pk)
    return render_panel(
        request,
        'peliculas/detail.html',
        {'pelicula': pelicula},
        view='detail',
    )


@staff_required
def pelicula_create(request):
    if request.method == 'POST':
        data = request.POST.dict()
        data['en_cartelera'] = 'en_cartelera' in request.POST
        image_file = request.FILES.get('imagen_portada')

        try:
            services.create_pelicula(data, image_file)
        except ValueError as exc:
            return render_panel(
                request,
                'peliculas/form.html',
                _form_context(post=request.POST, error=exc),
                view='form',
            )

        return panel_list_or_redirect(
            request,
            redirect('peliculas:pelicula_list'),
            'peliculas/list.html',
            _list_context(),
        )

    return render_panel(
        request,
        'peliculas/form.html',
        _form_context(),
        view='form',
    )


@staff_required
def pelicula_update(request, pk):
    pelicula = services.get_pelicula(pk)

    if request.method == 'POST':
        data = {
            field: request.POST.get(field)
            for field in FORM_FIELDS
            if request.POST.get(field)
        }
        data['en_cartelera'] = 'en_cartelera' in request.POST
        image_file = request.FILES.get('imagen_portada')

        try:
            services.update_pelicula(pk, data, image_file)
        except ValueError as exc:
            return render_panel(
                request,
                'peliculas/form.html',
                _form_context(pelicula=pelicula, post=request.POST, error=exc),
                view='form',
            )

        return panel_list_or_redirect(
            request,
            redirect('peliculas:pelicula_detail', pk=pk),
            'peliculas/list.html',
            _list_context(),
        )

    return render_panel(
        request,
        'peliculas/form.html',
        _form_context(pelicula=pelicula),
        view='form',
    )


@staff_required
def pelicula_delete(request, pk):
    if request.method == 'POST':
        services.delete_pelicula(pk)
        return panel_list_or_redirect(
            request,
            redirect('peliculas:pelicula_list'),
            'peliculas/list.html',
            _list_context(),
        )

    pelicula = services.get_pelicula(pk)
    return render_panel(
        request,
        'peliculas/confirm_delete.html',
        {'pelicula': pelicula},
        view='form',
    )
