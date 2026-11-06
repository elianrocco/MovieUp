from django.http import HttpResponse
from django.shortcuts import redirect, render

from estadisticas import services as estadisticas_services
from funciones import services as funciones_services
from peliculas.models import Pelicula
from peliculas import services as peliculas_services
from salas import services as salas_services

from .decorators import staff_required


def home(request):
    """Página principal con hero y grid de películas en cartelera."""
    # Redirigir administradores a la vista de gestión
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/gestion/')
    
    # Obtener la película más reciente en cartelera para el hero
    hero_pelicula = (
        Pelicula.objects
        .filter(en_cartelera=True)
        .order_by('-fecha_estreno')
        .first()
    )
    
    # Obtener todas las películas en cartelera para el grid
    peliculas_cartelera = (
        Pelicula.objects
        .filter(en_cartelera=True)
        .order_by('-fecha_estreno')
    )
    
    context = {
        'hero_pelicula': hero_pelicula,
        'peliculas': peliculas_cartelera,
    }
    
    return render(request, 'home.html', context)


@staff_required
def gestion(request):
    """Central staff dashboard with pre-rendered domain listings."""
    return render(
        request,
        'gestion.html',
        {
            'peliculas': peliculas_services.list_peliculas(),
            'funciones': funciones_services.list_funciones(),
            'salas': salas_services.list_salas(),
            'estadisticas': estadisticas_services.build_estadisticas(),
        },
    )


def favicon(_request):
    """Placeholder favicon so browsers don't 404 on templates without an icon link.

    Matches the empty ``data:,`` icon used in base.html; replace with a real
    asset when the author provides the logo/favicon.
    """
    return HttpResponse(b'', content_type='image/x-icon')
