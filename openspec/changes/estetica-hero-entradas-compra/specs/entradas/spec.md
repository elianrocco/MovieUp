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

Cada tarjeta del listado SHALL mostrar el título de la película arriba sin etiqueta, debajo el estado con su etiqueta, debajo la fecha y hora de inicio con su etiqueta y, en la última fila, sala, fila y asiento en una misma fila con sus etiquetas, separando filas y elementos con un margen pequeño.

#### Scenario: Orden de las filas de la tarjeta

- **WHEN** se renderiza una entrada en el listado
- **THEN** el título de la película aparece arriba sin etiqueta, debajo el estado con su etiqueta, debajo la fecha y hora de inicio con su etiqueta y en la última fila sala, fila y asiento juntos, cada uno con su etiqueta

#### Scenario: Margen pequeño entre filas

- **WHEN** se renderiza una tarjeta con todas sus filas
- **THEN** hay un margen pequeño visible entre cada fila y entre los elementos de la fila de sala, fila y asiento

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

El detalle SHALL presentarse dentro de un rectángulo de bordes redondeados con el dorado del nav, con el título de la película fuera de los paneles y cada otro dato en su propio panel blanco con la etiqueta fuera del panel, arriba del valor. El enlace `Volver a mis entradas` SHALL renderizarse como un botón con ese dorado y un contorno rojo, y SHALL aparecer al lado un segundo botón con el texto `Reembolso` de igual alto.

#### Scenario: Detalle dentro del rectángulo dorado

- **WHEN** se abre el detalle de una entrada
- **THEN** el título de la película aparece fuera de los paneles y cada dato aparece en su propio panel blanco con su etiqueta fuera del panel, arriba del valor, todo dentro de un rectángulo de bordes redondeados con el dorado del nav

#### Scenario: Fila de sala, fila y asiento

- **WHEN** se renderiza el detalle
- **THEN** sala, fila y asiento aparecen en una misma fila en ese orden con un margen mediano entre ellos

#### Scenario: Fila de tipo de sala, tipo de sonido y capacidad

- **WHEN** se renderiza el detalle
- **THEN** tipo de sala, tipo de sonido y capacidad de la sala aparecen en una misma fila en ese orden con un margen mediano entre ellos

#### Scenario: Los dos botones del detalle

- **WHEN** se renderiza el detalle de una entrada
- **THEN** aparecen el botón `Volver a mis entradas` con el dorado del nav y un contorno rojo y, al lado, el botón `Reembolso` con el mismo alto que el primero