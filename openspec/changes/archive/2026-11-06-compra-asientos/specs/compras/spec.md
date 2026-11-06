# Spec Delta

## REMOVED Requirements

### Requirement: Botón de compra de cada función

**Reason**: El botón ya no queda sin destino: la vista de selección de asientos existe y el flujo de compra se define en este cambio.

**Migration**: Reemplazado por el requisito "Destino del botón de compra de cada función" de este mismo delta.

## ADDED Requirements

### Requirement: Destino del botón de compra de cada función

Cada ítem SHALL incluir el botón `Comprar entradas`. El botón de una función con disponibilidad mayor que cero SHALL conducir a la vista de selección de asientos de esa función; el botón de una función agotada MUST permanecer deshabilitado y sin navegación.

#### Scenario: El botón conduce a la selección de asientos

- **WHEN** el usuario activa el botón `Comprar entradas` de una función vendible con disponibilidad mayor que cero
- **THEN** se carga la vista de selección de asientos de esa función

#### Scenario: Cada botón apunta a su función

- **WHEN** el listado muestra dos funciones vendibles de la película
- **THEN** cada botón conduce a la vista de selección de la función que representa

### Requirement: Vista de selección de asientos de una función

El sistema SHALL ofrecer la vista `/compras/<pelicula_id>/funciones/<funcion_id>/` a las cuentas comunes autenticadas. Un visitante MUST ser conducido al login con Google con retorno a esa misma página; una cuenta administradora SHALL ser redirigida a `/gestion/`; una película o función inexistente, una función ajena a la película, inactiva o finalizada MUST responder 404.

#### Scenario: Cuenta común abre la selección

- **WHEN** una cuenta común autenticada solicita la vista de una función vendible de una película existente
- **THEN** el sistema muestra la vista de selección de asientos de esa función

#### Scenario: Visitante en la selección

- **WHEN** un visitante solicita `/compras/11/funciones/5/`
- **THEN** es conducido al login con Google con retorno a esa misma página, sin renderizar la pantalla intermedia de acceso

#### Scenario: Cuenta administradora en la selección

- **WHEN** una cuenta administradora solicita la vista de selección de asientos
- **THEN** es redirigida a `/gestion/`

#### Scenario: Función ajena a la película

- **WHEN** se solicita la vista con un identificador de función que pertenece a otra película
- **THEN** el sistema responde 404

#### Scenario: Función inactiva o finalizada

- **WHEN** se solicita la vista de una función con `funcion_activa` inactivo o con el fin anterior al momento actual
- **THEN** el sistema responde 404

### Requirement: Cuadrícula de asientos de la función

La vista SHALL mostrar debajo del nav, centrada, la cuadrícula con el encabezado `Elija sus asientos` y la distribución de esa función, con el mismo estilo y colores que el editor de sala: gris para `P`, azul para `A` y dorado para `R`. Las entradas ya vendidas MUST aparecer como celdas `R`.

#### Scenario: Encabezado y centrado

- **WHEN** se carga la vista de selección de asientos
- **THEN** aparece el mensaje `Elija sus asientos` centrado por encima de la cuadrícula y la cuadrícula aparece centrada debajo del nav

#### Scenario: Colores de las celdas

- **WHEN** la distribución de la función contiene celdas `P`, `A` y `R`
- **THEN** las celdas aparecen en gris, azul y dorado respectivamente y se distinguen entre sí

#### Scenario: Asientos ya vendidos

- **WHEN** la función ya tiene entradas vendidas
- **THEN** sus celdas aparecen como `R` en dorado dentro de la cuadrícula

#### Scenario: La cuadrícula es de la función y no de la sala

- **WHEN** después de crear la función el administrador cambia la distribución de la sala
- **THEN** la cuadrícula muestra la distribución guardada de la función

### Requirement: Selección de asientos disponibles

Solo las celdas `A` de la cuadrícula SHALL ser interactivas. Un clic sobre una celda `A` SHALL marcarla como seleccionada cambiándola a rojo, y un clic sobre una celda seleccionada SHALL devolverla a azul. Las celdas `P` y `R` MUST NOT responder a la interacción.

#### Scenario: Seleccionar un asiento

- **WHEN** el usuario hace clic en una celda azul `A`
- **THEN** la celda pasa a rojo y queda marcada como seleccionada

#### Scenario: Deseleccionar un asiento

- **WHEN** el usuario hace clic en una celda roja seleccionada
- **THEN** la celda vuelve a azul y deja de estar seleccionada

#### Scenario: Celdas sin interacción

- **WHEN** el usuario hace clic en una celda gris `P` o en una celda dorada `R`
- **THEN** la celda no cambia de estado ni de color

### Requirement: Datos de solo lectura de la compra

Debajo de la cuadrícula la vista SHALL mostrar, en filas centradas y con la etiqueta encima de cada ítem, los datos de la película y de la función: título y descripción; idioma, subtitulada, tipo de sala y tipo de sonido; inicio, fin y duración. Todos los datos, el contador y el total MUST ser de solo lectura: solo la cuadrícula y el botón de confirmación admiten interacción.

#### Scenario: Cada ítem con su etiqueta encima

- **WHEN** se renderiza la vista con todos los datos
- **THEN** cada ítem muestra su valor con la etiqueta (`Título`, `Descripción`, `Idioma`, `Subtitulada`, `Tipo de sala`, `Tipo de sonido`, `Inicio`, `Fin`, `Duración`) por encima

#### Scenario: Orden de las filas

- **WHEN** se renderiza la vista
- **THEN** las filas aparecen en el orden título, descripción, idioma-subtitulada-tipo de sala-tipo de sonido, inicio-fin-duración

#### Scenario: Estado de subtitulada y duración

- **WHEN** la función es subtitulada y la película dura 100 minutos
- **THEN** el ítem de subtitulada muestra `Sí` y el de duración muestra 100 min

#### Scenario: Solo cuadrícula y botón son interactivos

- **WHEN** se inspecciona la vista
- **THEN** los datos, el contador y el total no admiten interacción y solo la cuadrícula y el botón `Confirmar compra` la admiten

### Requirement: Resumen de la compra

La vista SHALL mostrar abajo a la derecha el contador `Cantidad de entradas` y el total de la compra, cada uno con su etiqueta a la izquierda y no arriba. El contador SHALL igualar la cantidad de celdas seleccionadas y el total SHALL ser ese valor multiplicado por el precio de la entrada, con signo `$` y dos decimales; ambos se actualizan con cada cambio de selección.

#### Scenario: Selección de dos asientos

- **WHEN** el usuario tiene seleccionadas dos celdas `A` y el precio de la entrada es 15000
- **THEN** el contador muestra 2 y el total muestra $30000.00

#### Scenario: Deseleccionar un asiento

- **WHEN** el usuario deselecciona una de las dos celdas
- **THEN** el contador baja a 1 y el total muestra el precio de una entrada

#### Scenario: Página sin selección

- **WHEN** la vista carga con ninguna celda seleccionada
- **THEN** el contador muestra 0 y el total muestra $0.00

### Requirement: Botón de confirmar compra

La vista SHALL incluir el botón `Confirmar compra` a la derecha del total, sin etiqueta propia. Con ninguna celda seleccionada el botón MUST aparecer deshabilitado con el mismo formato que el botón agotado del listado, sin navegación ni envío; con una o más celdas seleccionadas SHALL aparecer habilitado.

#### Scenario: Confirmación deshabilitada al cargar

- **WHEN** la vista carga con el contador en 0
- **THEN** el botón `Confirmar compra` aparece deshabilitado con el formato del botón agotado

#### Scenario: Confirmación habilitada con selección

- **WHEN** el usuario selecciona una celda `A`
- **THEN** el botón queda habilitado conservando su texto `Confirmar compra`

### Requirement: Creación de las entradas de la compra

Al confirmar, el sistema SHALL crear una entrada por cada celda seleccionada con la fila y el número de asiento que corresponden a cada celda, aplicando la actualización de la función definida en `entradas`. La operación MUST ser atómica y rechazarse completa, sin crear ni modificar nada, si alguna celda ya no está disponible, la función dejó de estar vendible o la solicitud no incluye celdas.

#### Scenario: Compra de tres asientos

- **WHEN** el usuario confirma con tres celdas `A` seleccionadas
- **THEN** se crean tres entradas con la fila y el número de asiento de cada celda, la disponibilidad baja en tres y la distribución marca esas celdas como `R`

#### Scenario: Asiento tomado durante la compra

- **WHEN** entre la carga de la vista y la confirmación otro usuario compra uno de los asientos seleccionados
- **THEN** la operación se rechaza completa: no se crea ninguna entrada y la función queda intacta

#### Scenario: Función deja de estar vendible

- **WHEN** al confirmar la función está inactiva o su fin ya pasó
- **THEN** el sistema rechaza la compra sin crear entradas

#### Scenario: Confirmación sin celdas

- **WHEN** se envía la confirmación sin ninguna celda seleccionada
- **THEN** el sistema la rechaza sin crear entradas

### Requirement: Confirmación sin barrera de pago

En este cambio la confirmación MUST avanzar directamente como si el pago se hubiera confirmado, sin mostrar ninguna pantalla ni paso de pago; la barrera de pago queda fuera de alcance.

#### Scenario: El usuario confirma

- **WHEN** el usuario activa `Confirmar compra` con asientos seleccionados
- **THEN** no aparece ninguna pantalla de pago y el sistema procesa la compra directamente

### Requirement: Vista de compra realizada

Tras crear las entradas, el sistema SHALL mostrar el mensaje `Compra realizada con éxito, puede ver sus entradas en` seguido del botón `Mis entradas`, que SHALL conducir a `/entradas/`. La confirmación SHALL presentarse centrada.

#### Scenario: Mensaje de éxito

- **WHEN** la compra se confirma con éxito
- **THEN** aparece el mensaje `Compra realizada con éxito, puede ver sus entradas en` con el botón `Mis entradas`

#### Scenario: Botón Mis entradas

- **WHEN** el usuario activa el botón `Mis entradas`
- **THEN** se carga el listado de sus entradas en `/entradas/`
