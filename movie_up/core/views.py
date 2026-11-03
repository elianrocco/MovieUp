from django.shortcuts import render, redirect
from django.utils import timezone

from peliculas.models import Pelicula


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
