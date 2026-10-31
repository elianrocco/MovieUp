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
    """
    pelicula = get_pelicula(pk)
    
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
    
    # TODO: Cuando exista la app 'funciones', descomentar las siguientes líneas
    # para validar que la película no tenga funciones asociadas
    # from funciones.models import Funcion
    # if Funcion.objects.filter(pelicula=pelicula).exists():
    #     raise ValidationError("No se puede eliminar: la película tiene funciones asociadas")
    
    # Eliminar la imagen del sistema de archivos
    if pelicula.imagen_portada:
        image_path = pelicula.imagen_portada.path
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Eliminar el registro de la base de datos
    pelicula.delete()
