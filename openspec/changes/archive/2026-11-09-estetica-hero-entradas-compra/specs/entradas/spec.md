# Spec Delta

## ADDED Requirements

### Requirement: Encabezado del listado en panel dorado

El listado SHALL mostrar el encabezado `Mis entradas` centrado dentro de un panel dorado del mismo ancho horizontal que las tarjetas de entrada y con un alto vertical delgado que apenas encapsule el texto más un margen pequeño.

#### Scenario: Encabezado en panel dorado

- **WHEN** una cuenta con entradas abre `/entradas/`
- **THEN** el encabezado `Mis entradas` aparece centrado dentro de un panel dorado

#### Scenario: Mismo ancho que las tarjetas y alto delgado

- **WHEN** se renderiza el listado con una o más entradas
- **THEN** el panel del encabezado tiene el mismo ancho horizontal que las tarjetas de entrada y su alto apenas encapsula el texto con un pequeño margen

### Requirement: Orden de los datos en cada tarjeta del listado

Cada tarjeta SHALL centrar todo su contenido, incluido `Ver entrada`. SHALL mostrar el título sin etiqueta, luego Estado e Inicio juntos con etiquetas sobre sus valores y, debajo, Sala/Fila/Asiento juntos con etiquetas sobre sus valores. Ambas filas SHALL mantener todos sus elementos dentro del tercio central.

#### Scenario: Orden y alineación centrada de las filas

- **WHEN** se renderiza una entrada en el listado
- **THEN** el título de la película aparece arriba sin etiqueta; debajo, estado e inicio comparten una fila con cada etiqueta encima del valor; y en la última fila sala, fila y asiento comparten una fila con cada etiqueta encima del valor, con todo el contenido de la tarjeta y el botón `Ver entrada` centrados

#### Scenario: Espaciado máximo dentro del tercio central

- **WHEN** se renderiza una tarjeta en un viewport de escritorio
- **THEN** Estado/Inicio y Sala/Fila/Asiento usan el mismo margen horizontal máximo que mantiene todos sus elementos dentro del tercio central de la tarjeta, sin tocar el primer ni el tercer tercio

#### Scenario: Ancho insuficiente para el espaciado máximo

- **WHEN** el ancho del viewport o el contenido de una entrada impide mantener todos los elementos en una fila dentro del tercio central
- **THEN** los elementos se reacomodan dentro de ese tercio y no invaden las zonas laterales de la tarjeta

### Requirement: Textos de estado de la entrada

El sistema SHALL mostrar el estado de una entrada como `Sin usar` cuando está activa y como `Usada` cuando ya fue validada, en el listado y en el detalle, y MUST NO mostrar `Pendiente de validación` ni `Validada` en esas vistas.

#### Scenario: Entrada sin usar

- **WHEN** se muestra una entrada activa en el listado o en el detalle
- **THEN** el estado aparece como `Sin usar`

#### Scenario: Entrada usada

- **WHEN** se muestra una entrada ya validada en el listado o en el detalle
- **THEN** el estado aparece como `Usada`

#### Scenario: Textos antiguos ausentes

- **WHEN** se inspeccionan el listado y el detalle de entradas
- **THEN** no aparecen los textos `Pendiente de validación` ni `Validada`

## MODIFIED Requirements

### Requirement: Presentación del detalle de entrada

El detalle SHALL presentarse dentro de un rectángulo de bordes redondeados con el dorado del nav, con el título de la película fuera de los paneles y cada otro dato en su propio panel blanco que ocupa todo el ancho disponible de su columna sin sobrepasar el margen interior del panel dorado. Las etiquetas SHALL aparecer centradas fuera del panel, arriba del valor, y el contenido de los paneles SHALL estar centrado. El enlace `Volver a mis entradas` SHALL renderizarse como un botón con ese dorado y un contorno rojo, y SHALL aparecer al lado un segundo botón con el texto `Reembolso` de igual alto.

#### Scenario: Detalle dentro del rectángulo dorado

- **WHEN** se abre el detalle de una entrada
- **THEN** el título de la película aparece fuera de los paneles y cada dato aparece en su propio panel blanco que llena el ancho disponible de la columna sin sobrepasar el margen interior dorado, con su etiqueta centrada fuera del panel y arriba del valor centrado

#### Scenario: Fila de sala, fila y asiento

- **WHEN** se renderiza el detalle
- **THEN** sala, fila y asiento aparecen en una misma fila en ese orden con un margen mediano entre ellos

#### Scenario: Fila de tipo de sala, tipo de sonido y capacidad

- **WHEN** se renderiza el detalle
- **THEN** tipo de sala, tipo de sonido y capacidad de la sala aparecen en una misma fila en ese orden con un margen mediano entre ellos

#### Scenario: Los dos botones del detalle

- **WHEN** se renderiza el detalle de una entrada
- **THEN** aparecen el botón `Volver a mis entradas` con el dorado del nav y un contorno rojo y, al lado, el botón `Reembolso` con el mismo alto que el primero
