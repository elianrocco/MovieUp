# Películas — Especificación de Capacidad

## Propósito

La capacidad `movies` gestiona el catálogo de películas del sistema MovieUp. Permite a los administradores crear, consultar, actualizar y eliminar películas con información completa (título, portada, género, duración, descripción, clasificación, fecha de estreno, tráiler y estado en cartelera), incluyendo validaciones de negocio y manejo de archivos de imagen.

## Requisitos

### Datos y Persistencia

- **REQ-MOV-001**: El sistema debe almacenar películas en MySQL con los siguientes campos:
  - `titulo` (VARCHAR 150, único, NOT NULL)
  - `imagen_portada` (ruta a archivo de imagen, NOT NULL)
  - `genero` (VARCHAR 45, NOT NULL)
  - `duracion_minutos` (INT, NOT NULL)
  - `descripcion` (MEDIUMTEXT, NOT NULL)
  - `clasificacion` (VARCHAR 10, NOT NULL)
  - `fecha_estreno` (DATE, NOT NULL)
  - `url_trailer` (VARCHAR 255, NOT NULL)
  - `en_cartelera` (BooleanField, default=False, NOT NULL)

- **REQ-MOV-002**: Las imágenes de portada deben almacenarse en la carpeta `imgs/` en la raíz del proyecto, y la base de datos debe contener únicamente la ruta relativa al archivo.

- **REQ-MOV-003**: El campo `titulo` debe ser único en todo el catálogo.

### Operaciones CRUD

- **REQ-MOV-010 (Listar)**: El sistema debe mostrar todas las películas en una tabla con columnas básicas (título, género, duración, fecha de estreno, en cartelera).

- **REQ-MOV-011 (Detalle)**: El sistema debe mostrar todos los campos de una película específica, incluyendo la imagen de portada. El sistema debe validar que el ID pertenezca a un registro real (404 si no existe).

- **REQ-MOV-020 (Crear)**:
  - El sistema debe permitir crear una nueva película mediante un formulario HTML.
  - Todos los campos son obligatorios (atributo `required` en HTML).
  - Validaciones HTML5: `maxlength` según el tipo de campo, `type="date"` para fecha_estreno, `type="number"` para duracion_minutos, `type="url"` para url_trailer.
  - La imagen recibida del formulario debe guardarse en `imgs/` y la ruta almacenarse en la BD.

- **REQ-MOV-030 (Actualizar)**:
  - El sistema debe validar que el ID pertenezca a un registro real (404 si no existe).
  - El sistema debe permitir actualizar una película existente mediante un formulario HTML.
  - Todos los campos son opcionales (sin atributo `required`).
  - Solo se actualizan los campos que fueron ingresados en el formulario (update parcial).
  - Si se proporciona una nueva imagen:
    1. Guardar la nueva imagen en `imgs/`.
    2. Eliminar la imagen vieja de `imgs/`.
    3. Actualizar la ruta en la BD.
  - Las mismas validaciones HTML5 que en crear, pero sin `required`.

- **REQ-MOV-040 (Eliminar)**:
  - El sistema debe validar que el ID pertenezca a un registro real (404 si no existe).
  - El sistema debe preparar validación para verificar que la película no esté asociada a ninguna función (tabla futura `funciones`). Esta validación debe estar comentada y lista para activarse cuando exista la app `funciones`.
  - Si la película tiene funciones asociadas (cuando la validación esté activa), el sistema debe rechazar el borrado y mostrar un mensaje de error.

### Arquitectura y Organización

- **REQ-MOV-050**: La lógica de negocio debe residir en `services.py` (Service Layer). Las vistas deben ser delgadas: request → service → response.

- **REQ-MOV-051**: Los formularios HTML deben usar atributos HTML5 para validación (no validación server-side adicional más allá de lo que Django hace por defecto con ModelForm).

- **REQ-MOV-052**: Los templates deben ser HTML puro, sin CSS ni JavaScript.

- **REQ-MOV-053**: El código preparado para la futura app `funciones` debe estar comentado y no debe romper tests ni ejecutar queries reales hasta que la app exista.

## Escenarios

### Escenario 1: Listar películas existentes
- **Dado** que existen 3 películas en la base de datos
- **Cuando** el administrador navega a `/peliculas/`
- **Entonces** el sistema muestra una tabla con las 3 películas y sus datos básicos

### Escenario 2: Crear película exitosa
- **Dado** que el administrador está en `/peliculas/create/`
- **Cuando** completa todos los campos del formulario y sube una imagen de portada
- **Entonces** el sistema guarda la imagen en `imgs/`, almacena la ruta en la BD, y redirige al listado con la nueva película

### Escenario 3: Crear película con datos inválidos
- **Dado** que el administrador está en `/peliculas/create/`
- **Cuando** intenta enviar el formulario con un campo vacío o un valor inválido (ej: URL mal formada)
- **Entonces** el navegador muestra mensajes de validación HTML5 y no envía el formulario

### Escenario 4: Actualizar película parcialmente
- **Dado** que existe la película "Inception" con ID=1
- **Cuando** el administrador navega a `/peliculas/1/update/`, solo modifica el campo `descripcion` y deja el resto vacío
- **Entonces** el sistema actualiza solo la descripción, mantiene los demás campos sin cambios, y redirige al detalle

### Escenario 5: Actualizar película con nueva imagen
- **Dado** que existe la película "Inception" con ID=1 y su imagen en `imgs/inception.jpg`
- **Cuando** el administrador sube una nueva imagen `inception_v2.jpg` en el formulario de actualización
- **Entonces** el sistema guarda `inception_v2.jpg` en `imgs/`, elimina `inception.jpg`, actualiza la ruta en la BD, y redirige al detalle

### Escenario 6: Eliminar película sin funciones asociadas
- **Dado** que existe la película "Inception" con ID=1 y no tiene funciones asociadas
- **Cuando** el administrador navega a `/peliculas/1/delete/` y confirma
- **Entonces** el sistema elimina la película de la BD y redirige al listado

### Escenario 7: Eliminar película inexistente
- **Dado** que no existe ninguna película con ID=999
- **Cuando** el administrador navega a `/peliculas/999/delete/`
- **Entonces** el sistema muestra error 404

### Escenario 8: Eliminar película con funciones asociadas (preparado para futuro)
- **Dado** que existe la película "Inception" con ID=1 y tiene funciones asociadas (cuando la app `funciones` exista)
- **Cuando** el administrador intenta eliminarla
- **Entonces** el sistema rechaza el borrado y muestra mensaje "No se puede eliminar: la película tiene funciones asociadas"

### Escenario 9: Ver detalle de película inexistente
- **Dado** que no existe ninguna película con ID=999
- **Cuando** el administrador navega a `/peliculas/999/`
- **Entonces** el sistema muestra error 404

### Escenario 10: Actualizar película inexistente
- **Dado** que no existe ninguna película con ID=999
- **Cuando** el administrador navega a `/peliculas/999/update/`
- **Entonces** el sistema muestra error 404
