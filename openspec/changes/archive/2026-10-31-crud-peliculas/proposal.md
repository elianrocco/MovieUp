# Proposal

## Why

MovieUp necesita gestionar el catálogo de películas como base para la venta de entradas. Sin un CRUD funcional, los administradores no pueden crear, consultar, actualizar ni eliminar películas, lo cual bloquea todos los casos de uso posteriores (funciones, ventas, consulta de clientes). Implementar este CRUD ahora establece el primer dominio funcional del sistema y valida la arquitectura de Service Layer elegida.

## What Changes

- Nuevo modelo `Pelicula` en `movie_up/peliculas/models.py` mapeando la tabla `pelicula` de MySQL con todos sus campos (titulo, imagen_portada, genero, duracion_minutos, descripcion, clasificacion, fecha_estreno, url_trailer) + nuevo campo `en_cartelera` (BooleanField, default=False, NOT NULL).
- `ImageField(upload_to='imgs/')` para `imagen_portada` → Django guarda archivos en `MEDIA_ROOT/imgs/` y en la BD solo la ruta relativa.
- Registro del modelo en `admin.py` para administración vía Django Admin.
- Service layer en `services.py` con funciones: `list_peliculas()`, `get_pelicula(id)`, `create_pelicula(data, imagen_file)`, `update_pelicula(id, data, imagen_file)`, `delete_pelicula(id)`.
- Vistas basadas en funciones en `views.py` para las 5 operaciones CRUD (list, detail, create, update, delete).
- URLs en `peliculas/urls.py` con rutas: `/peliculas/`, `/peliculas/<id>/`, `/peliculas/create/`, `/peliculas/<id>/update/`, `/peliculas/<id>/delete/`.
- Inclusión de `peliculas.urls` en `core/urls.py` a nivel raíz.
- Configuración de `MEDIA_URL` y `MEDIA_ROOT` en `settings.py` para servir imágenes.
- Templates mínimos en `templates/peliculas/`: `list.html`, `detail.html`, `form.html`, `confirm_delete.html` (HTML puro, sin CSS ni JavaScript).
- Validaciones HTML5 en formularios: `required`, `maxlength`, `type="date"`, `type="number"`, `type="url"`, etc.
- Create: todos los campos obligatorios (`required`).
- Update: todos los campos opcionales (sin `required`), solo se actualizan los ingresados. Si se actualiza la imagen, se elimina la vieja de `imgs/` antes de guardar la nueva.
- Delete: valida que el ID exista (404 si no). Preparado para validar funciones asociadas (código comentado para futura app `funciones`).

## Capabilities

### New Capabilities

- `movies`: Gestión completa del catálogo de películas (CRUD) con persistencia en MySQL, validaciones de negocio, manejo de imágenes, y presentación web básica. Esta capacidad evoluciona para incluir búsqueda, filtros, paginación y posiblemente integración con otros dominios (funciones, ventas).

### Modified Capabilities

(Ninguna - no hay specs existentes)

## Impact

- **Código**: Todos los archivos en `movie_up/peliculas/` (models.py, admin.py, services.py, views.py, urls.py, templates/). Cambios en `movie_up/core/settings.py` (MEDIA_URL, MEDIA_ROOT) y `movie_up/core/urls.py` (incluir rutas de películas).
- **Base de datos**: Creación de tabla `peliculas_pelicula` con todos los campos incluyendo `en_cartelera` (TINYINT(1) en MySQL). Migración inicial requerida.
- **Sistema de archivos**: Carpeta `imgs/` en la raíz del proyecto para almacenar imágenes de portada.
- **APIs**: Endpoints HTTP bajo `/peliculas/` (GET, POST). No hay API REST todavía; todas las operaciones son server-rendered con forms HTML.
- **Dependencias**: Ninguna nueva (Django 6.1.1 y MySQL ya configurados).
- **Sistemas**: Afecta solo el backend Django y la base de datos MySQL. No hay impacto en frontend (aún no existe), pasarela de pagos, ni autenticación.
