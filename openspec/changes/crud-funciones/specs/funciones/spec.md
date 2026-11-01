# Spec Delta: funciones

## Purpose

La capacidad `funciones` administra el programa de funciones del complejo: relaciona una película con una sala en un horario, copia la distribución de la sala como snapshot propio de la función y deriva de ella el fin y la disponibilidad. Este change cubre únicamente el CRUD administrativo; la parte comercial queda para specs futuras.

## ADDED Requirements

### Requirement: Listar el catálogo de funciones

El sistema SHALL mostrar en un listado administrativo todas las funciones registradas, activas e inactivas, con al menos película, sala, inicio, fin, estado, disponibilidad y precio.

#### Scenario: Listar funciones existentes

- **WHEN** existen 3 funciones registradas y el administrador navega a `/funciones/`
- **THEN** el sistema muestra una fila por función con esos siete datos

### Requirement: Ver el detalle de una función

El sistema SHALL mostrar todos los campos de una función; la película y la sala SHALL mostrarse por su nombre, sin exponer sus ids, y la distribución SHALL renderizarse como una cuadrícula de solo lectura. Las solicitudes sobre un identificador inexistente MUST responder con error 404.

#### Scenario: Detalle de una función existente

- **WHEN** el administrador navega a `/funciones/<id>/` con el identificador de una función real
- **THEN** el sistema muestra todos sus campos, los nombres de la película y la sala, y la distribución en una cuadrícula que no admite modificaciones

#### Scenario: Detalle de una función inexistente

- **WHEN** no existe ninguna función con ID=999 y el administrador navega a `/funciones/999/`
- **THEN** el sistema muestra error 404

### Requirement: Crear una función

El sistema SHALL permitir registrar una función con película, sala, inicio, idioma, subtitulada, precio y estado activo elegido por el administrador; todos los campos son obligatorios. Al crear, el sistema SHALL calcular el fin desde el inicio y la duración de la película, copiar la distribución de la sala, derivar la disponibilidad y fijar las entradas compradas en 0.

#### Scenario: Crear una función exitosa

- **WHEN** el administrador completa el formulario en `/funciones/create/` con una película de 120 minutos, una sala válida y un inicio de 21:00
- **THEN** el sistema registra la función con el fin a las 23:00, la distribución copiada de la sala, la disponibilidad derivada y las entradas compradas en 0, y redirige al listado

### Requirement: Película y sala elegibles por menú

Los formularios de creación y actualización SHALL ofrecer la película y la sala en menús desplegables que muestran los nombres de los registros existentes y envían su identificador como valor del campo.

#### Scenario: Seleccionar desde los menús

- **WHEN** el administrador abre el formulario de creación
- **THEN** el sistema muestra un menú con los nombres de las películas y otro con los nombres de las salas, y al elegir una opción envía el id correspondiente

### Requirement: Inicio presente o futuro

El sistema MUST rechazar un inicio anterior al momento de registrar la función, interpretando ambos momentos en el horario local de Buenos Aires.

#### Scenario: Rechazar un inicio en el pasado

- **WHEN** el administrador intenta registrar una función con un inicio ya transcurrido
- **THEN** el sistema rechaza la operación, no persiste nada y muestra el motivo

### Requirement: Fin derivado de la duración de la película

El sistema SHALL calcular el fin sumando la duración de la película asociada al inicio. El fin es de solo lectura: un valor enviado desde el formulario MUST ignorarse, y SHALL recalcularse cuando cambie el inicio o la película en una actualización.

#### Scenario: Calcular el fin al crear

- **WHEN** se registra una función con inicio a las 21:00 de una película de 120 minutos
- **THEN** el sistema persiste el fin a las 23:00 del mismo día

#### Scenario: Recalcular el fin al cambiar el inicio

- **WHEN** el administrador retrasa el inicio de una función existente en 30 minutos
- **THEN** el sistema recalcula el fin sumando la duración de la película al nuevo inicio

### Requirement: Sin solapamiento en la misma sala

El sistema MUST rechazar cualquier función cuyo intervalo `[inicio, fin)` cruce el de otra función de la misma sala, sin importar su estado. Un fin igual al inicio de otra función, o viceversa, MUST permitirse.

#### Scenario: Rechazar un solapamiento

- **WHEN** la sala ya tiene una función de 20:00 a 22:00 y el administrador intenta registrar otra de la misma sala de 21:59:59 a 23:00
- **THEN** el sistema rechaza la operación e informa el conflicto de horario

#### Scenario: Permitir funciones consecutivas

- **WHEN** la sala ya tiene una función que termina a las 22:00 y el administrador registra otra de la misma sala que empieza a las 22:00
- **THEN** el sistema acepta ambas funciones

#### Scenario: Una función inactiva también bloquea

- **WHEN** la sala tiene una función inactiva que ocupa el horario intentado
- **THEN** el sistema rechaza la operación igual que si estuviera activa

### Requirement: Precio no negativo

El sistema MUST rechazar un precio de entrada menor que 0.

#### Scenario: Rechazar un precio negativo

- **WHEN** el administrador envía un precio de entrada de -5
- **THEN** el sistema rechaza la operación sin persistir nada y muestra el motivo

### Requirement: Distribución copiada de la sala

Al crear una función, el sistema SHALL almacenar una copia completa de la distribución de la sala elegida, sin referencia ni puntero. La disponibilidad SHALL derivarse contando únicamente las celdas `A` de esa copia. Cambios posteriores de la sala en su distribución MUST NOT alterar la copia de la función.

#### Scenario: Copiar la distribución y derivar la disponibilidad

- **WHEN** se registra una función en una sala cuya distribución tiene 120 celdas `A`, 15 celdas `R` y 40 celdas `P`
- **THEN** la función almacena una copia idéntica de la distribución y una disponibilidad de 120

#### Scenario: La copia no cambia con la sala

- **WHEN** después de crear la función el administrador modifica la distribución de la sala
- **THEN** la distribución y la disponibilidad de la función quedan sin cambios

### Requirement: Actualizar una función

El sistema SHALL permitir actualizar una función con todos los campos opcionales y precargados con sus valores actuales, incluidos los menús de película y sala. Al enviar cambios, el fin SHALL recalcularse si cambia el inicio o la película, y la distribución y la disponibilidad SHALL reemplazarse si cambia la sala. Las solicitudes sobre un identificador inexistente MUST responder con error 404.

#### Scenario: Precargar y actualizar parcialmente

- **WHEN** el administrador abre `/funciones/<id>/update/` y modifica solo el idioma
- **THEN** el formulario muestra los valores actuales de todos los campos y el sistema aplica solo el idioma, conservando el resto sin cambios

#### Scenario: Recalcular el fin al cambiar la película

- **WHEN** el administrador reemplaza la película por otra de mayor duración sin tocar el inicio
- **THEN** el sistema recalcula el fin con la duración de la nueva película

#### Scenario: Reemplazar la distribución al cambiar de sala

- **WHEN** el administrador cambia la sala de una función
- **THEN** el sistema copia la distribución de la nueva sala y recalcula la disponibilidad contando sus celdas `A`

#### Scenario: Actualizar una función inexistente

- **WHEN** no existe ninguna función con ID=999 y el administrador navega a `/funciones/999/update/`
- **THEN** el sistema muestra error 404

### Requirement: Actualización bloqueada por entradas compradas

El sistema MUST rechazar la actualización de una función que ya tiene entradas compradas, sin modificar ningún dato e informando el motivo.

#### Scenario: Rechazar la actualización de una función con entradas

- **WHEN** la función tiene entradas compradas y el administrador intenta actualizarla
- **THEN** el sistema rechaza la operación, no modifica ningún campo y muestra el motivo

### Requirement: Eliminación bloqueada por entradas compradas

El sistema MUST rechazar la eliminación de una función que ya tiene entradas compradas, sin borrar nada e informando el motivo.

#### Scenario: Rechazar la eliminación de una función con entradas

- **WHEN** la función tiene entradas compradas y el administrador confirma el borrado
- **THEN** el sistema rechaza la operación y la función permanece registrada

### Requirement: Activación limitada a funciones no vencidas

El sistema MUST impedir que una función cuyo fin ya pasó pase a estar activa, sin importar el estado que traiga.

#### Scenario: Rechazar activar una función vencida

- **WHEN** el administrador intenta marcar como activa una función cuyo fin ya transcurrió
- **THEN** el sistema rechaza el cambio, conserva el estado anterior e informa el motivo

### Requirement: Eliminar una función

El sistema SHALL eliminar una función tras una confirmación explícita, sin eliminar la película ni la sala asociadas. Las solicitudes sobre un identificador inexistente MUST responder con error 404.

#### Scenario: Eliminar una función existente

- **WHEN** existe una función sin entradas compradas y el administrador confirma el borrado
- **THEN** el sistema elimina solo la función y la película y la sala permanecen registradas

#### Scenario: Eliminar una función inexistente

- **WHEN** no existe ninguna función con ID=999 y el administrador navega a `/funciones/999/delete/`
- **THEN** el sistema muestra error 404

### Requirement: Horarios en hora local de Buenos Aires

El sistema SHALL interpretar y mostrar las fechas y horas de las funciones en el horario local de Buenos Aires.

#### Scenario: Crear con hora local

- **WHEN** el administrador registra una función con inicio a las 21:00
- **THEN** el listado y el detalle muestran las 21:00 sin conversión aparente para el usuario

### Requirement: Validación en dos niveles

El navegador SHALL bloquear envíos con campos obligatorios vacíos, precio negativo o un inicio ya transcurrido. El servicio MUST revalidar esas mismas reglas y además las que el navegador no puede verificar: cálculo del fin, solapamiento por sala, derivados, bloqueos por entradas compradas y activación de funciones vencidas.

#### Scenario: El navegador bloquea un envío inválido

- **WHEN** el administrador deja vacía la película o el idioma, o intenta enviar un precio negativo
- **THEN** el navegador no envía el formulario y muestra el mensaje correspondiente

#### Scenario: El servicio rechaza un envío manipulado

- **WHEN** se envía al servicio un inicio en el pasado, un precio negativo o un horario en conflicto, evadiendo la validación del navegador
- **THEN** el servicio rechaza la operación e informa el motivo sin persistir nada
