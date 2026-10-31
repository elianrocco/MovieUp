from django.shortcuts import render, redirect
from django.http import Http404
from . import services


def pelicula_list(request):
    """Vista de listado de películas."""
    peliculas = services.list_peliculas()
    return render(request, 'peliculas/list.html', {'peliculas': peliculas})


def pelicula_detail(request, pk):
    """Vista de detalle de una película."""
    try:
        pelicula = services.get_pelicula(pk)
        return render(request, 'peliculas/detail.html', {'pelicula': pelicula})
    except Http404:
        raise


def pelicula_create(request):#
    """Vista para crear una nueva película."""
    if request.method == 'POST':
        data = request.POST.dict()
        data['en_cartelera'] = 'en_cartelera' in request.POST
        image_file = request.FILES.get('imagen_portada')
        services.create_pelicula(data, image_file)
        return redirect('pelicula_list')
    return render(request, 'peliculas/form.html')


def pelicula_update(request, pk):
    """Vista para actualizar una película existente."""
    pelicula = services.get_pelicula(pk)
    
    if request.method == 'POST':
        data = {}
        for field in ['titulo', 'genero', 'duracion_minutos', 'descripcion', 
                      'clasificacion', 'fecha_estreno', 'url_trailer']:
            if request.POST.get(field):
                data[field] = request.POST.get(field)
        
        if 'en_cartelera' in request.POST:
            data['en_cartelera'] = request.POST.get('en_cartelera') == 'on'
        
        image_file = request.FILES.get('imagen_portada')
        services.update_pelicula(pk, data, image_file)
        return redirect('pelicula_detail', pk=pk)
    
    return render(request, 'peliculas/form.html', {'pelicula': pelicula})


def pelicula_delete(request, pk):
    """Vista para eliminar una película."""
    if request.method == 'POST':
        services.delete_pelicula(pk)
        return redirect('pelicula_list')
    
    pelicula = services.get_pelicula(pk)
    return render(request, 'peliculas/confirm_delete.html', {'pelicula': pelicula})
