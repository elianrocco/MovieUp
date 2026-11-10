# movies Specification

## Purpose

La capacidad `movies` gestiona el catálogo de películas del sistema MovieUp. Permite a los administradores crear, consultar, actualizar y eliminar películas con información completa (título, portada, género, duración, descripción, clasificación, fecha de estreno, tráiler y estado en cartelera), incluyendo validaciones de negocio y manejo de archivos de imagen.

## Requirements

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

### Requirement: Edición restringida de películas con funciones asociadas

Cuando una película tiene funciones asociadas, activas o no, el sistema SHALL permitir únicamente cambiar el estado `en_cartelera`; cualquier otro cambio real MUST ser rechazado mostrando el motivo en el formulario, sin modificar ningún dato.

#### Scenario: Cambio permitido de en cartelera

- **WHEN** la administradora cambia solo `en_cartelera` de una película con funciones asociadas y guarda
- **THEN** el sistema actualiza el estado y conserva el resto de los campos sin cambios

#### Scenario: Guardado sin cambios

- **WHEN** la administradora envía el formulario de una película con funciones asociadas sin modificar ningún campo
- **THEN** el sistema guarda el registro sin mostrar errores y todos los campos permanecen iguales

#### Scenario: Cambio de otro atributo rechazado

- **WHEN** la administradora modifica la duración, el título o cualquier otro atributo distinto de `en_cartelera` en una película con funciones asociadas
- **THEN** el sistema rechaza el envío, no modifica ningún campo y muestra en el formulario el mensaje "No se puede editar una película con funciones asociadas; solo puede cambiarse el estado En cartelera."

#### Scenario: Película sin funciones se edita con normalidad

- **WHEN** la administradora modifica cualquier atributo de una película sin funciones asociadas
- **THEN** el sistema aplica los cambios y redirige al detalle

### Requirement: Eliminar una película

El sistema SHALL eliminar una película tras una confirmación explícita, y MUST responder con error 404 cuando el identificador no existe. Si la película tiene funciones asociadas, activas o no, la eliminación MUST ser rechazada con el motivo en la confirmación, sin modificar ni borrar ningún dato.

#### Scenario: Eliminar película sin funciones asociadas

- **WHEN** existe la película "Inception" con ID=1, no tiene funciones asociadas y el administrador navega a `/peliculas/1/delete/` y confirma
- **THEN** el sistema elimina la película y redirige al listado

#### Scenario: Eliminar película inexistente

- **WHEN** no existe ninguna película con ID=999 y el administrador navega a `/peliculas/999/delete/`
- **THEN** el sistema muestra error 404

#### Scenario: Eliminar película con funciones asociadas

- **WHEN** existe una película con funciones asociadas y el administrador intenta eliminarla
- **THEN** el sistema rechaza el borrado, conserva la película y su portada, y muestra el mensaje "No se puede eliminar una película con funciones asociadas."

### Requirement: Acceso restringido al personal en las rutas de gestión

Las rutas de listado, detalle, formulario y borrado de películas SHALL aceptar solo al personal autorizado: un visitante SHALL ser redirigido al inicio de sesión y una cuenta común SHALL ser redirigida a la página principal, sin que el registro sufra cambios.

#### Scenario: Visitante en el listado

- **WHEN** un visitante solicita `/peliculas/`
- **THEN** es redirigido a la pantalla de inicio de sesión

#### Scenario: Cuenta común en el detalle

- **WHEN** una cuenta común solicita `/peliculas/<id>/` con un ID existente
- **THEN** es redirigida a la página principal y no ve el detalle

#### Scenario: Cuenta común intenta editar

- **WHEN** una cuenta común solicita `/peliculas/<id>/update/`
- **THEN** es redirigida a la página principal y el registro queda sin cambios

#### Scenario: Cuenta común intenta borrar

- **WHEN** una cuenta común solicita `/peliculas/<id>/delete/`
- **THEN** es redirigida a la página principal y el registro permanece

#### Scenario: Personal autorizado

- **WHEN** el personal solicita cualquiera de las cuatro rutas
- **THEN** accede y opera normalmente
