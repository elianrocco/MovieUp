# Spec Delta

## Purpose

Habilita la compra de entradas de una película: página de selección de función, portada reutilizada, listado de funciones vendibles y limpieza de las funciones vencidas al cargar.

## ADDED Requirements

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

Cada ítem del listado SHALL mostrar el inicio en hora local de Buenos Aires, el tipo de sala, el tipo de sonido, el idioma, si es subtitulada, el precio con signo `$`, la disponibilidad y un botón `Comprar entradas`.

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

### Requirement: Botón de compra de cada función

Cada ítem SHALL incluir el botón `Comprar entradas`. En este cambio su destino y su flujo de selección y pago quedan fuera de alcance: el botón MUST NOT navegar a ninguna ruta.

#### Scenario: Botón presente sin destino

- **WHEN** se renderiza una función vendible con disponibilidad mayor que cero
- **THEN** el botón `Comprar entradas` aparece y no navega a ninguna parte
