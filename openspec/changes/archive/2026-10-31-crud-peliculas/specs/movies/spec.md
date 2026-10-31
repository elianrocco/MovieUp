# Spec Delta: movies

## Purpose

La capacidad `movies` gestiona el catálogo de películas del sistema MovieUp. Permite a los administradores crear, consultar, actualizar y eliminar películas con información completa (título, portada, género, duración, descripción, clasificación, fecha de estreno, tráiler y estado en cartelera), incluyendo validaciones de negocio y manejo de archivos de imagen.

## ADDED Requirements

### Requirement: Listar el catálogo de películas

El sistema SHALL mostrar todas las películas del catálogo en una tabla con al menos título, género, duración, fecha de estreno y estado en cartelera.

#### Scenario: Listar películas existentes

- **WHEN** existen 3 películas en la base de datos y el administrador navega a `/peliculas/`
- **THEN** el sistema muestra una tabla con las 3 películas y sus datos básicos

### Requirement: Ver el detalle de una película

El sistema SHALL mostrar todos los campos de una película específica, incluida su imagen de portada. Las solicitudes sobre un identificador inexistente MUST responder con error 404.

#### Scenario: Detalle de una película existente

- **WHEN** el administrador navega a `/peliculas/<id>/` con el identificador de una película real
- **THEN** el sistema muestra todos sus campos y renderiza la imagen de portada

#### Scenario: Detalle de película inexistente

- **WHEN** no existe ninguna película con ID=999 y el administrador navega a `/peliculas/999/`
- **THEN** el sistema muestra error 404

### Requirement: Crear una película

El sistema SHALL permitir crear una película mediante un formulario HTML con todos los campos obligatorios, y SHALL impedir el envío cuando un campo requerido está vacío o mal formado. Además, el sistema MUST rechazar un título que ya exista en el catálogo, sin crear ningún registro y mostrando el motivo.

#### Scenario: Crear película exitosa

- **WHEN** el administrador completa todos los campos en `/peliculas/create/` y sube una imagen de portada
- **THEN** el sistema almacena la película, guarda la portada y redirige al listado incluyendo la nueva película

#### Scenario: Crear película con datos inválidos

- **WHEN** el administrador intenta enviar el formulario con un campo vacío o un valor inválido (por ejemplo, una URL mal formada)
- **THEN** el navegador muestra mensajes de validación HTML5 y no envía el formulario

#### Scenario: Crear película con título duplicado

- **WHEN** el administrador envía un título que ya pertenece a otra película del catálogo
- **THEN** el sistema no crea el registro y vuelve a mostrar el formulario con un mensaje que indica que el título ya existe

### Requirement: Actualizar una película parcialmente

El sistema SHALL permitir actualizar una película existente mediante un formulario HTML con todos los campos opcionales, aplicando únicamente los campos que el usuario complete. Si se envía una nueva imagen de portada, el sistema MUST reemplazar la anterior y conservar una sola. Las solicitudes sobre un identificador inexistente MUST responder con error 404.

#### Scenario: Actualizar película parcialmente

- **WHEN** existe la película "Inception" con ID=1 y el administrador navega a `/peliculas/1/update/`, modifica solo `descripcion` y deja el resto vacío
- **THEN** el sistema actualiza solo la descripción, mantiene los demás campos sin cambios y redirige al detalle

#### Scenario: Actualizar película con nueva imagen

- **WHEN** el administrador sube una nueva imagen de portada en el formulario de actualización
- **THEN** el sistema guarda la nueva imagen, elimina la anterior del almacenamiento, actualiza la referencia y redirige al detalle

#### Scenario: Actualizar película inexistente

- **WHEN** no existe ninguna película con ID=999 y el administrador navega a `/peliculas/999/update/`
- **THEN** el sistema muestra error 404

### Requirement: Eliminar una película

El sistema SHALL eliminar una película tras una confirmación explícita, y MUST responder con error 404 cuando el identificador no existe. Mientras las películas no puedan asociarse a funciones, el borrado es incondicional; cuando esa asociación exista, el sistema MUST rechazar la eliminación de una película que tenga funciones asociadas e informar el motivo.

#### Scenario: Eliminar película sin funciones asociadas

- **WHEN** existe la película "Inception" con ID=1, no tiene funciones asociadas y el administrador navega a `/peliculas/1/delete/` y confirma
- **THEN** el sistema elimina la película y redirige al listado

#### Scenario: Eliminar película inexistente

- **WHEN** no existe ninguna película con ID=999 y el administrador navega a `/peliculas/999/delete/`
- **THEN** el sistema muestra error 404

#### Scenario: Eliminar película con funciones asociadas

- **WHEN** existe una película con funciones asociadas y el administrador intenta eliminarla
- **THEN** el sistema rechaza el borrado y muestra el mensaje "No se puede eliminar: la película tiene funciones asociadas"
