# compras Specification

## Purpose
Habilita la compra de entradas de una película: página de selección de función, portada reutilizada, listado de funciones vendibles y limpieza de las funciones vencidas al cargar.

## Requirements

### Requirement: Página de compra por película

El sistema SHALL ofrecer la página `/compras/<pelicula_id>/` a las cuentas comunes autenticadas. Un visitante MUST ser conducido al login con Google con retorno a esa misma página; una cuenta administradora SHALL ser redirigida a `/gestion/`; una película inexistente MUST responder 404.

#### Scenario: Cuenta común abre la compra

- **WHEN** una cuenta común autenticada solicita `/compras/<pelicula_id>/` de una película existente
- **THEN** el sistema muestra la página de compra de esa película

#### Scenario: Visitante en la compra

- **WHEN** un visitante solicita `/compras/<pelicula_id>/`
- **THEN** es conducido al login con Google con retorno a esa misma página, sin renderizar la pantalla intermedia de acceso

#### Scenario: Cuenta administradora en la compra

- **WHEN** una cuenta administradora solicita `/compras/<pelicula_id>/`
- **THEN** es redirigida a `/gestion/`

#### Scenario: Película inexistente

- **WHEN** se solicita `/compras/999/` y no existe ninguna película con ID=999
- **THEN** el sistema responde 404

### Requirement: Portada de la película seleccionada

La página SHALL abrir con la portada de la película seleccionada en el mismo hero de la página principal: mismas dimensiones, posición y contenido, con imagen, título, descripción, género, clasificación y botón `Trailer` dentro del rectángulo. El hero de la compra MUST NOT mostrar el botón `Comprar entradas`.

#### Scenario: La portada coincide con la home

- **WHEN** se abre la compra de una película
- **THEN** la portada usa el mismo tamaño, la misma ubicación y los mismos datos que el hero de la página principal para esa película

#### Scenario: Trailer dentro de la portada

- **WHEN** el usuario hace clic en `Trailer` dentro de la portada
- **THEN** se abre la URL del tráiler de esa película

#### Scenario: Sin botón de compra en la portada

- **WHEN** se inspecciona la portada de la página de compra
- **THEN** no aparece el botón `Comprar entradas`

### Requirement: Listado de funciones vendibles

El sistema SHALL listar las funciones de la película con `funcion_activa` activo y fin posterior al momento actual, ordenadas por inicio ascendente. Las funciones inactivas o cuyo fin ya pasó MUST NOT aparecer en el listado.

#### Scenario: Listar solo funciones activas y futuras

- **WHEN** la película tiene dos funciones activas con fin futuro y una función activa con fin pasado
- **THEN** el listado muestra las dos funciones futuras y no la vencida

#### Scenario: Orden por inicio

- **WHEN** la película tiene funciones vendibles con inicios desordenados
- **THEN** el listado las muestra de la más próxima a la más lejana

#### Scenario: Función inactiva excluida

- **WHEN** una función de la película tiene `funcion_activa` inactivo
- **THEN** no aparece en el listado aunque su fin sea futuro

#### Scenario: Función finalizada excluida

- **WHEN** una función de la película tiene el fin anterior al momento actual
- **THEN** no aparece en el listado

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

### Requirement: Entradas agotadas

Cuando la disponibilidad de una función sea 0, el botón de esa función MUST quedar deshabilitado, con el rojo primario atenuado, sin navegación y con el texto `Entradas agotadas` en lugar de `Comprar entradas`.

#### Scenario: Función sin disponibilidad

- **WHEN** una función vendible tiene disponibilidad 0
- **THEN** su botón aparece deshabilitado, con el color primario atenuado y el texto `Entradas agotadas`

#### Scenario: Función con disponibilidad

- **WHEN** una función vendible tiene disponibilidad mayor que cero
- **THEN** su botón aparece habilitado con el texto `Comprar entradas`

#### Scenario: El botón agotado no navega

- **WHEN** el usuario intenta activar el botón de una función agotada
- **THEN** no se produce ninguna navegación

### Requirement: Barrido de funciones vencidas al cargar

Antes de construir el listado, el sistema SHALL ejecutar el barrido de funciones vencidas de la película: por cada función con fin menor o igual al momento actual SHALL aplicar la desactivación definida en `funciones` y la limpieza masiva por finalización definida en `entradas`. El barrido MUST ser atómico, idempotente y acotado a esa película.

#### Scenario: Función vencida con entradas

- **WHEN** se carga la compra de una película que tiene una función vencida con entradas asociadas
- **THEN** las entradas de esa función se eliminan, la función queda inactiva y no aparece en el listado

#### Scenario: Función vencida sin entradas

- **WHEN** se carga la compra de una película que tiene una función vencida sin entradas
- **THEN** la función queda inactiva y no aparece en el listado

#### Scenario: Solo la película seleccionada

- **WHEN** otra película tiene una función vencida
- **THEN** el barrido de la compra no modifica esa función ni sus entradas

#### Scenario: Contadores intactos

- **WHEN** el barrido elimina las entradas de una función vencida
- **THEN** las entradas compradas, la disponibilidad y la distribución de esa función conservan sus valores previos

#### Scenario: Barrido idempotente

- **WHEN** se vuelve a cargar la compra después de un barrido
- **THEN** la operación no produce errores ni efectos duplicados

#### Scenario: Función futura intacta

- **WHEN** la película tiene una función activa con fin futuro
- **THEN** el barrido no la modifica

### Requirement: Estado vacío del listado

Si la película no tiene funciones vendibles, la página SHALL mostrar un estado vacío en lugar del listado.

#### Scenario: Película sin funciones vendibles

- **WHEN** se abre la compra de una película sin funciones activas con fin futuro
- **THEN** la página muestra un mensaje de estado vacío y ningún ítem de función

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
