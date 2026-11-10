# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
