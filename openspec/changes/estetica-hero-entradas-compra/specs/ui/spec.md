# Spec Delta

## MODIFIED Requirements

### Requirement: Hero de la página principal

La página principal SHALL mostrar un rectángulo horizontal centrado de poco más de la mitad del alto y tres cuartos del ancho de la pantalla con las hasta tres películas en cartelera de fecha de estreno más reciente, rotando automáticamente el contenido activo entre ellas en orden descendente de estreno y en ciclo. El contenido activo —portada, título, descripción, género, clasificación y botones `Trailer` y `Comprar entradas` de su película— SHALL ocupar el sector inferior izquierdo del rectángulo.

#### Scenario: Películas en cartelera

- **WHEN** existen al menos tres películas con `en_cartelera` activo
- **THEN** el hero presenta las tres de estreno más reciente, iniciando con la de mayor fecha, con todo el contenido dentro del rectángulo y ubicado en el sector inferior izquierdo

#### Scenario: Rotación cada 7 segundos hacia la izquierda

- **WHEN** la página principal permanece visible durante un ciclo de 7 segundos
- **THEN** el contenido de la siguiente película por fecha de estreno desplaza hacia la izquierda el contenido actual mediante una transición lenta, y el ciclo continúa desde la tercera de vuelta a la primera

#### Scenario: Menos de tres películas en cartelera

- **WHEN** solo una o dos películas tienen `en_cartelera` activo
- **THEN** el hero inicia con la de mayor fecha de estreno y rota entre las disponibles, y con una sola película permanece fijo sin rotación

#### Scenario: La más reciente no está en cartelera

- **WHEN** la película de mayor fecha de estreno tiene `en_cartelera` inactivo
- **THEN** el hero inicia con la película en cartelera de mayor fecha de estreno

#### Scenario: Sin películas en cartelera

- **WHEN** no hay ninguna película con `en_cartelera` activo
- **THEN** la página principal muestra un estado vacío en lugar del hero