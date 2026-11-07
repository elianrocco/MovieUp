# Spec Delta

## ADDED Requirements

### Requirement: Presentación de la vista de validación

La vista de validación SHALL mostrar su encabezado, su formulario y el resultado dentro de un panel blanco centrado horizontalmente en la página, y el botón de envío `Validar` SHALL ser de color dorado.

#### Scenario: Contenido en panel blanco centrado

- **WHEN** se abre la vista de validación
- **THEN** el encabezado y el formulario aparecen dentro de un panel blanco centrado en la página

#### Scenario: Botón Validar dorado

- **WHEN** se muestra el formulario de validación
- **THEN** el botón `Validar` tiene el color dorado de la paleta

#### Scenario: Resultado dentro del panel

- **WHEN** se envía un código y la vista muestra el resultado
- **THEN** el mensaje y los datos de la entrada aparecen dentro del mismo panel

### Requirement: Datos de entrada validados en filas etiquetadas

Tras una validación exitosa, la vista SHALL mostrar cada dato de la entrada como un par etiqueta/valor en una fila, con la etiqueta a la izquierda del valor y seguida de dos puntos, y SHALL dejar una separación vertical uniforme entre filas.

#### Scenario: Etiquetas a la izquierda de cada valor

- **WHEN** se muestran los datos de una entrada validada
- **THEN** cada etiqueta aparece a la izquierda de su valor y termina con dos puntos

#### Scenario: Separación entre los datos

- **WHEN** se muestran varias filas de datos de una entrada validada
- **THEN** hay una separación visual pequeña y uniforme entre las filas
