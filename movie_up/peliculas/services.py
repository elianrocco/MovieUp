from django.http import Http404
from .models import Pelicula
import os


def list_peliculas():
    """Retorna todas las películas ordenadas por título."""
    return Pelicula.objects.all().order_by('titulo')


def get_pelicula(pk):
    """Retorna una película por su ID o lanza Http404 si no existe."""
    try:
        return Pelicula.objects.get(pk=pk)
    except Pelicula.DoesNotExist:
        raise Http404("Película no encontrada")


def create_pelicula(data, image_file):
    """
    Crea una nueva película.
    
    Args:
        data: Diccionario con los datos del formulario
        image_file: Archivo de imagen para el campo imagen_portada
    
    Returns:
        La instancia de Pelicula creada
    
    Raises:
        ValueError: Si ya existe una película con el mismo título
    """
    titulo = data.get('titulo', '').strip()
    if Pelicula.objects.filter(titulo=titulo).exists():
        raise ValueError(f"Ya existe una película con el título '{titulo}'")
    
    pelicula = Pelicula(
        titulo=data['titulo'],
        genero=data['genero'],
        duracion_minutos=int(data['duracion_minutos']),
        descripcion=data['descripcion'],
        clasificacion=data['clasificacion'],
        fecha_estreno=data['fecha_estreno'],
        url_trailer=data['url_trailer'],
        en_cartelera=data.get('en_cartelera', False),
        imagen_portada=image_file
    )
    pelicula.save()
    return pelicula


def _normalized_update_value(value):
    if isinstance(value, str):
        return value.strip()
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


def _guard_associated_movie_update(pelicula, data, image_file):
    from funciones.models import Funcion

    if not Funcion.objects.filter(pelicula_id=pelicula.pk).exists():
        return data

    has_restricted_change = image_file is not None
    for field, value in data.items():
        if field == 'en_cartelera' or value is None or value == '':
            continue
        current_value = getattr(pelicula, field, None)
        if _normalized_update_value(value) != _normalized_update_value(current_value):
            has_restricted_change = True

    if has_restricted_change:
        raise ValueError(
            'No se puede editar una película con funciones asociadas; '
            'solo puede cambiarse el estado En cartelera.'
        )

    return {field: value for field, value in data.items() if field == 'en_cartelera'}


def update_pelicula(pk, data, image_file=None):
    """
    Actualiza una película existente con update parcial.
    
    Args:
        pk: ID de la película
        data: Diccionario con los campos a actualizar (solo los no vacíos se aplican)
        image_file: Nueva imagen opcional
    
    Returns:
        La instancia de Pelicula actualizada
    
    Raises:
        Http404: Si la película no existe
        ValueError: Si otra película ya usa el título enviado
    """
    pelicula = get_pelicula(pk)
    data = _guard_associated_movie_update(pelicula, data, image_file)

    titulo = data.get('titulo')
    if titulo:
        if Pelicula.objects.filter(titulo=titulo.strip()).exclude(pk=pk).exists():
            raise ValueError(f"Ya existe una película con el título '{titulo.strip()}'")
    
    # Actualizar solo campos no vacíos
    for field, value in data.items():
        if value is not None and value != '':
            setattr(pelicula, field, value)
    
    # Manejo de imagen
    if image_file:
        # Guardar referencia a la imagen vieja antes de asignar la nueva
        old_image_path = None
        if pelicula.imagen_portada:
            old_image_path = pelicula.imagen_portada.path
        
        # Asignar nueva imagen (se guardará al hacer save())
        pelicula.imagen_portada = image_file
        
        # Guardar en BD
        pelicula.save()
        
        # Eliminar imagen vieja del disco DESPUÉS de guardar exitosamente
        if old_image_path and os.path.exists(old_image_path):
            os.remove(old_image_path)
    else:
        # Sin nueva imagen, solo guardar cambios
        pelicula.save()
    
    return pelicula


def delete_pelicula(pk):
    """
    Elimina una película y su imagen asociada.
    
    Args:
        pk: ID de la película a eliminar
    
    Raises:
        Http404: Si la película no existe
    """
    pelicula = get_pelicula(pk)

    from funciones.models import Funcion

    if Funcion.objects.filter(pelicula_id=pelicula.pk).exists():
        raise ValueError('No se puede eliminar una película con funciones asociadas.')
    
    # Eliminar la imagen del sistema de archivos
    if pelicula.imagen_portada:
        image_path = pelicula.imagen_portada.path
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Eliminar el registro de la base de datos
    pelicula.delete()
