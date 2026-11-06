# Spec Delta

## MODIFIED Requirements

### Requirement: Datos de cada función

Cada ítem del listado SHALL mostrar el inicio en hora local de Buenos Aires, el tipo de sala, el tipo de sonido, el idioma, si es subtitulada, el precio con signo `$`, la disponibilidad y un botón `Comprar entradas`. Los siete datos SHALL aparecer en una sola línea dentro del ítem, sin salto de línea entre ellos.

#### Scenario: Ítem con todos los datos

- **WHEN** se renderiza una función vendible
- **THEN** el ítem muestra inicio, tipo de sala, tipo de sonido, idioma, subtitulada, precio con `$`, disponibilidad y el botón `Comprar entradas`

#### Scenario: Estado de subtitulada

- **WHEN** una función es subtitulada y otra no
- **THEN** cada ítem indica su estado de subtitulado de forma explícita

#### Scenario: Precio con signo pesos

- **WHEN** una función tiene un precio de entrada de 15000
- **THEN** el ítem muestra el precio con el signo `$` y dos decimales

#### Scenario: Disponibilidad visible

- **WHEN** una función tiene disponibilidad mayor que cero
- **THEN** el ítem muestra esa cantidad de entradas disponibles

#### Scenario: Todos los datos en una sola línea

- **WHEN** se renderiza un ítem del listado en una ventana de escritorio
- **THEN** inicio, tipo de sala, tipo de sonido, idioma, subtitulada, precio y disponibilidad aparecen en la misma fila, sin partirse en dos

### Requirement: Cuadrícula de asientos de la función

La vista SHALL mostrar el encabezado `Elija sus asientos` y la cuadrícula de la distribución dentro de un rectángulo horizontal de bordes redondeados con el dorado del nav, con margen del 10% del ancho de pantalla a cada lado y padding vertical apenas suficiente. Los colores SHALL ser gris para `P`, azul para `A` y dorado para `R`, y las entradas ya vendidas MUST aparecer como celdas `R`.

#### Scenario: Encabezado y centrado

- **WHEN** se carga la vista de selección de asientos
- **THEN** aparece el mensaje `Elija sus asientos` centrado por encima de la cuadrícula y la cuadrícula aparece centrada debajo del nav

#### Scenario: Panel dorado de la cuadrícula

- **WHEN** se carga la vista de selección de asientos
- **THEN** el encabezado y la cuadrícula aparecen dentro de un rectángulo de bordes redondeados con el dorado del nav, que deja un margen del 10% del ancho de pantalla a cada lado y sobresale apenas por arriba y por abajo de su contenido

#### Scenario: Colores de las celdas

- **WHEN** la distribución de la función contiene celdas `P`, `A` y `R`
- **THEN** las celdas aparecen en gris, azul y dorado respectivamente y se distinguen entre sí

#### Scenario: Asientos ya vendidos

- **WHEN** la función ya tiene entradas vendidas
- **THEN** sus celdas aparecen como `R` en dorado dentro de la cuadrícula

#### Scenario: La cuadrícula es de la función y no de la sala

- **WHEN** después de crear la función el administrador cambia la distribución de la sala
- **THEN** la cuadrícula muestra la distribución guardada de la función

### Requirement: Datos de solo lectura de la compra

Debajo del panel dorado la vista SHALL mostrar los datos dentro de un rectángulo blanco de bordes redondeados del mismo ancho, pegado por arriba al panel dorado y con margen entre sus filas centradas, cada ítem con la etiqueta encima: título y descripción; idioma, subtitulada, tipo de sala y tipo de sonido; inicio, fin y duración. Todos los datos, el contador y el total MUST ser de solo lectura: solo la cuadrícula y el botón de confirmación admiten interacción.

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

#### Scenario: Panel blanco pegado al dorado

- **WHEN** se carga la vista de selección de asientos
- **THEN** las filas de datos aparecen dentro de un rectángulo blanco de bordes redondeados cuyo borde superior toca el borde inferior del panel dorado, con un margen visible entre sus filas

### Requirement: Resumen de la compra

La vista SHALL mostrar el resumen dentro de un rectángulo blanco de bordes redondeados del mismo ancho que los otros paneles y con margen por arriba y por abajo. Dentro, abajo a la derecha, SHALL estar el contador `Cantidad de entradas` y el total, cada uno con su etiqueta a la izquierda y no arriba. El contador SHALL igualar las celdas seleccionadas y el total SHALL ser ese valor por el precio de la entrada, con `$` y dos decimales; ambos se actualizan con cada cambio de selección.

#### Scenario: Selección de dos asientos

- **WHEN** el usuario tiene seleccionadas dos celdas `A` y el precio de la entrada es 15000
- **THEN** el contador muestra 2 y el total muestra $30000.00

#### Scenario: Deseleccionar un asiento

- **WHEN** el usuario deselecciona una de las dos celdas
- **THEN** el contador baja a 1 y el total muestra el precio de una entrada

#### Scenario: Página sin selección

- **WHEN** la vista carga con ninguna celda seleccionada
- **THEN** el contador muestra 0 y el total muestra $0.00

#### Scenario: Panel del resumen con márgenes

- **WHEN** se carga la vista de selección de asientos
- **THEN** el rectángulo blanco del resumen queda separado por un margen del rectángulo de los datos, tanto por arriba como por abajo

### Requirement: Vista de compra realizada

Tras crear las entradas, el sistema SHALL mostrar el mensaje `Compra realizada con éxito, puede ver sus entradas en` y, debajo de él, centrado y con un margen pequeño arriba, el botón `Mis entradas` que SHALL conducir a `/entradas/`. El botón SHALL usar el dorado del nav en lugar del rojo. La confirmación SHALL presentarse centrada.

#### Scenario: Mensaje de éxito

- **WHEN** la compra se confirma con éxito
- **THEN** aparece el mensaje `Compra realizada con éxito, puede ver sus entradas en` con el botón `Mis entradas`

#### Scenario: Botón debajo del mensaje

- **WHEN** se renderiza la pantalla de compra realizada
- **THEN** el botón `Mis entradas` aparece por debajo del mensaje, centrado, con un margen pequeño arriba y con el dorado del nav como fondo

#### Scenario: Botón Mis entradas

- **WHEN** el usuario activa el botón `Mis entradas`
- **THEN** se carga el listado de sus entradas en `/entradas/`
