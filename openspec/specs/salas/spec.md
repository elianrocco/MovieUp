# salas Specification

## Purpose

La capacidad `salas` administra las salas físicas del complejo y su distribución de butacas, que define qué celdas son pasillos, asientos y reservados, y de la cual se deriva el aforo de cada sala. Un reservado es una butaca que no se ofrece a la venta, ya sea porque está rota, porque la bloquea la normativa, porque la ocupa el proyector u otro equipamiento, o porque ya fue vendida en una función.

## Requirements

### Requirement: Listar el catálogo de salas

El sistema SHALL mostrar todas las salas registradas en una tabla con al menos nombre, tipo de sala, tipo de sonido y capacidad.

#### Scenario: Listar salas existentes

- **WHEN** existen 3 salas registradas y el administrador navega a `/salas/`
- **THEN** el sistema muestra una tabla con las 3 salas y sus datos básicos

### Requirement: Ver el detalle de una sala

El sistema SHALL mostrar todos los campos de una sala junto con su distribución representada como una cuadrícula de solo lectura, que usa gris para los pasillos, azul para los asientos y dorado para los reservados. La cuadrícula MUST NOT aceptar ninguna modificación. Las solicitudes sobre un identificador inexistente MUST responder con error 404.

#### Scenario: Detalle de una sala existente

- **WHEN** el administrador navega a `/salas/<id>/` con el identificador de una sala real
- **THEN** el sistema muestra sus campos, su capacidad y la cuadrícula con cada tipo de celda en su color correspondiente

#### Scenario: Detalle de sala inexistente

- **WHEN** no existe ninguna sala con ID=999 y el administrador navega a `/salas/999/`
- **THEN** el sistema muestra error 404

### Requirement: Crear una sala

El sistema SHALL permitir registrar una sala mediante un formulario con nombre, tipo de sala, tipo de sonido y distribución. Todos los atributos MUST ser obligatorios, salvo la capacidad, que se deriva. El sistema SHALL impedir el envío cuando un campo obligatorio está vacío o excede el largo permitido.

#### Scenario: Crear sala exitosa

- **WHEN** el administrador completa todos los campos en `/salas/create/` con una distribución válida
- **THEN** el sistema registra la sala, calcula su capacidad y redirige al listado incluyendo la nueva sala

#### Scenario: Crear sala con datos inválidos

- **WHEN** el administrador intenta enviar el formulario con un campo obligatorio vacío o con más de 45 caracteres
- **THEN** el navegador muestra el mensaje de validación correspondiente y no envía el formulario

### Requirement: Nombre de sala único

El sistema MUST rechazar una sala cuyo nombre ya exista en el catálogo, tanto al crear como al actualizar, sin crear ni modificar ningún registro y mostrando el motivo. Una actualización que conserva el nombre actual de la sala MUST NOT considerarse duplicada.

#### Scenario: Crear sala con nombre duplicado

- **WHEN** el administrador envía un nombre que ya pertenece a otra sala
- **THEN** el sistema no crea el registro y vuelve a mostrar el formulario indicando que el nombre ya existe

#### Scenario: Actualizar una sala a un nombre existente

- **WHEN** el administrador cambia el nombre de una sala por el de otra sala del catálogo
- **THEN** el sistema no aplica el cambio, conserva el nombre anterior y muestra el motivo

#### Scenario: Actualizar una sala conservando su propio nombre

- **WHEN** el administrador modifica otro campo y deja el nombre tal como estaba
- **THEN** el sistema aplica el cambio sin reportar un nombre duplicado

### Requirement: Editor de distribución en cuadrícula

El formulario SHALL presentar la distribución como una cuadrícula interactiva con controles para fijar el ancho y el alto, ambos entre 1 y 100. La cuadrícula MUST iniciarse en 10 filas por 10 columnas con todas las celdas en Pasillo. Cada clic sobre una celda SHALL alternar su tipo de forma cíclica en el orden Pasillo, Asiento, Reservado. Los colores SHALL ser gris para Pasillo, azul para Asiento y dorado para Reservado.

#### Scenario: Cuadrícula inicial por defecto

- **WHEN** el administrador abre `/salas/create/`
- **THEN** el sistema muestra una cuadrícula de 10 por 10 con todas las celdas en gris

#### Scenario: Cambiar el tamaño de la cuadrícula

- **WHEN** el administrador fija un ancho de 12 y un alto de 8
- **THEN** la cuadrícula pasa a tener 12 columnas y 8 filas, conserva el tipo de las celdas que siguen existiendo y completa las nuevas en Pasillo

#### Scenario: Alternar el tipo de una celda

- **WHEN** el administrador hace clic repetidas veces sobre la misma celda
- **THEN** el tipo recorre Pasillo, Asiento, Reservado y vuelve a Pasillo, cambiando el color en cada paso

#### Scenario: Rechazar dimensiones fuera de rango

- **WHEN** el administrador intenta ingresar un ancho o un alto menor a 1 o mayor a 100
- **THEN** el navegador impide el valor y no envía el formulario

### Requirement: Distribución válida

El sistema SHALL aceptar solo distribuciones rectangulares de hasta 100 filas por 100 columnas, con todas las filas de igual longitud y celdas restringidas a `P` (Pasillo), `A` (Asiento) o `R` (Reservado). La distribución MUST contener al menos una celda `A` o `R`.

#### Scenario: Aceptar una distribución válida

- **WHEN** el administrador envía una cuadrícula de 4 filas por 11 columnas con celdas `P`, `A` y `R`
- **THEN** el sistema persiste la distribución sin alterar sus dimensiones ni el contenido de sus celdas

#### Scenario: Rechazar filas de distinta longitud

- **WHEN** el servicio recibe una distribución cuyas filas no tienen todas la misma cantidad de celdas
- **THEN** el sistema rechaza la operación e informa que la distribución debe ser rectangular

#### Scenario: Rechazar un carácter fuera del alfabeto

- **WHEN** el servicio recibe una celda distinta de `P`, `A` o `R`
- **THEN** el sistema rechaza la operación e informa qué caracteres están permitidos

#### Scenario: Rechazar una distribución que excede el tamaño máximo

- **WHEN** el servicio recibe una distribución con más de 100 filas o más de 100 columnas
- **THEN** el sistema rechaza la operación e informa el límite permitido

#### Scenario: Rechazar una distribución sin butacas

- **WHEN** el administrador intenta guardar una sala cuya distribución tiene todas las celdas en Pasillo, como el estado inicial por defecto
- **THEN** el sistema rechaza la operación e informa que la sala debe tener al menos una butaca

#### Scenario: Registrar una sala con butacas reservadas

- **WHEN** el administrador registra una sala cuya distribución contiene celdas `R`
- **THEN** el sistema las persiste como reservadas, las cuenta en la capacidad y el detalle las muestra en dorado como no ofrecidas a la venta

### Requirement: Capacidad derivada de la distribución

El sistema SHALL calcular la capacidad contando las celdas `A` y `R` e ignorando las celdas `P`, y MUST recalcularla en cada creación y actualización de la sala. La capacidad MUST ser de solo lectura: un valor enviado por el formulario nunca se persiste.

#### Scenario: Calcular la capacidad de una distribución mixta

- **WHEN** se registra una sala cuya distribución contiene 120 celdas `A`, 15 celdas `R` y 40 celdas `P`
- **THEN** el sistema persiste una capacidad de 135

#### Scenario: Recalcular la capacidad al editar la distribución

- **WHEN** el administrador reemplaza la distribución de una sala por una con menos butacas
- **THEN** el sistema actualiza la capacidad al nuevo conteo

#### Scenario: Ignorar una capacidad enviada por el formulario

- **WHEN** el administrador manipula el envío e incluye un valor de capacidad
- **THEN** el sistema descarta ese valor y persiste el conteo derivado de la distribución

### Requirement: Versionado de la distribución

El sistema SHALL asignar la versión 1 a toda distribución nueva y MUST ignorar cualquier versión enviada desde el formulario. Al actualizar una sala, si la distribución enviada difiere de la almacenada el sistema MUST incrementar la versión en 1; si es idéntica, MUST conservarla sin cambios.

#### Scenario: Asignar la versión inicial

- **WHEN** se registra una sala con una distribución nueva
- **THEN** la distribución se persiste con versión 1

#### Scenario: Incrementar la versión al cambiar la distribución

- **WHEN** el administrador envía una distribución diferente a la almacenada para una sala con versión 1
- **THEN** el sistema persiste la nueva distribución con versión 2

#### Scenario: Conservar la versión al reenviar la misma distribución

- **WHEN** el administrador guarda una sala sin modificar ninguna celda de la distribución
- **THEN** la distribución conserva su versión actual

#### Scenario: Ignorar una versión enviada por el formulario

- **WHEN** el administrador manipula el envío e incluye un número de versión
- **THEN** el sistema descarta ese valor y aplica la regla de versionado propia

### Requirement: Actualizar una sala

El sistema SHALL permitir actualizar una sala con nombre, tipo de sala y tipo de sonido opcionales. Al cargar el formulario, todos los campos MUST estar precargados con sus valores actuales, incluida la cuadrícula con la distribución vigente. Cuando se envía una distribución, MUST reemplazar la anterior por completo y recalcular la capacidad. Las solicitudes sobre un identificador inexistente MUST responder con error 404.

#### Scenario: Actualizar solo algunos campos

- **WHEN** el administrador modifica solo el tipo de sonido y deja el nombre y el tipo de sala sin cambios
- **THEN** el sistema actualiza ese campo, conserva la distribución y la capacidad anteriores, y redirige al detalle

#### Scenario: Reemplazar la distribución completa

- **WHEN** el administrador envía una distribución distinta para una sala existente
- **THEN** el sistema reemplaza la anterior sin fusionarla, recalcula la capacidad e incrementa la versión

#### Scenario: Precargar el formulario de edición

- **WHEN** el administrador abre `/salas/<id>/update/` de una sala con distribución de 8 por 9
- **THEN** el formulario muestra los valores actuales de todos los campos y una cuadrícula de 8 por 9 con los tipos y colores vigentes

#### Scenario: Actualizar una sala inexistente

- **WHEN** no existe ninguna sala con ID=999 y el administrador navega a `/salas/999/update/`
- **THEN** el sistema muestra error 404

### Requirement: Bloquear operaciones sobre salas en uso

Mientras las salas no puedan asociarse a funciones, las operaciones son incondicionales. Cuando exista esa asociación, el sistema MUST rechazar la actualización y la eliminación de una sala que tenga al menos una función activa, sin modificar ni borrar datos, e informando el motivo.

#### Scenario: Rechazar la actualización por funciones activas

- **WHEN** la sala tiene al menos una función activa asociada y el administrador intenta actualizarla
- **THEN** el sistema rechaza la operación, no modifica ningún campo e informa que la sala está en uso

#### Scenario: Rechazar el borrado por funciones activas

- **WHEN** la sala tiene al menos una función activa asociada y el administrador intenta eliminarla
- **THEN** el sistema rechaza el borrado, no elimina nada e informa que la sala está en uso

### Requirement: Eliminar una sala

El sistema SHALL eliminar una sala tras una confirmación explícita y MUST responder con error 404 cuando el identificador no existe.

#### Scenario: Eliminar una sala existente

- **WHEN** existe una sala y el administrador confirma el borrado
- **THEN** el sistema elimina la sala y redirige al listado

#### Scenario: Eliminar una sala inexistente

- **WHEN** no existe ninguna sala con ID=999 y el administrador navega a `/salas/999/delete/`
- **THEN** el sistema muestra error 404

### Requirement: Validación en dos niveles

El sistema SHALL bloquear en el navegador los envíos con campos obligatorios vacíos, valores de más de 45 caracteres o dimensiones fuera del rango 1 a 100. El servicio MUST revalidar esas mismas reglas y además las que el navegador no puede verificar: nombre único, existencia del registro, composición de la distribución y estado de las funciones asociadas.

#### Scenario: El navegador bloquea un envío inválido

- **WHEN** el administrador deja vacío el nombre de la sala o fija un ancho de 150
- **THEN** el navegador no envía el formulario y muestra el mensaje correspondiente

#### Scenario: El servicio rechaza un envío manipulado

- **WHEN** se envía al servicio una sala con nombre vacío, dimensiones fuera de rango o una distribución sin butacas, evadiendo la validación del navegador
- **THEN** el servicio rechaza la operación e informa el motivo sin persistir nada
