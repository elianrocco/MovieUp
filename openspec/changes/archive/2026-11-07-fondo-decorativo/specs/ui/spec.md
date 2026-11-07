# Spec Delta

## ADDED Requirements

### Requirement: Fondo decorativo global

Todas las vistas de la web SHALL mostrar un fondo decorativo sobre el crema: degradados radiales sutiles (más claro arriba y más dorado abajo), una capa de grano de película de opacidad muy baja y cintas de cine detrás del contenido —verticales a los costados y cruzadas en diagonal— con opacidad baja que no interfiere con la lectura ni con la interacción.

#### Scenario: Degradados y grano de película

- **WHEN** se abre cualquier vista de la web
- **THEN** el fondo crema muestra un degradado radial más claro arriba y más dorado abajo, con una capa de grano de película de opacidad muy baja

#### Scenario: Cintas verticales a los costados

- **WHEN** se observa el fondo de cualquier vista
- **THEN** hay cintas de película verticales en ink a ambos costados, con perforaciones en crema y separadores de fotograma en dorado al 35%, de baja opacidad

#### Scenario: Cintas cruzadas en diagonal

- **WHEN** se observa el fondo de cualquier vista
- **THEN** cintas de película cruzan en diagonal todo el fondo, visibles detrás del contenido

#### Scenario: El contenido queda por encima

- **WHEN** se navega, se rellena un formulario o se interactúa con paneles sobre el fondo
- **THEN** el contenido se lee con normalidad por encima de la decoración y los clics llegan a los elementos interactivos
