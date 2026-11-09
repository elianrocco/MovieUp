# Spec Delta

## MODIFIED Requirements

### Requirement: Vista de compra realizada

Tras crear las entradas, el sistema SHALL mostrar dentro de un único panel blanco el mensaje `Compra realizada con éxito, puede ver sus entradas en` y, debajo de él, centrado y con un margen pequeño arriba, el botón `Mis entradas` que SHALL conducir a `/entradas/`. El botón SHALL usar el dorado del nav en lugar de rojo. La confirmación SHALL presentarse centrada.

#### Scenario: Mensaje de éxito

- **WHEN** la compra se confirma con éxito
- **THEN** aparece el mensaje `Compra realizada con éxito, puede ver sus entradas en` con el botón `Mis entradas`, y ambos comparten el mismo panel blanco

#### Scenario: Botón debajo del mensaje

- **WHEN** se renderiza la pantalla de compra realizada
- **THEN** el botón `Mis entradas` aparece por debajo del mensaje, centrado, con un margen pequeño arriba y con el dorado del nav como fondo

#### Scenario: Un único panel blanco

- **WHEN** se renderiza la pantalla de compra realizada
- **THEN** todo el contenido —mensaje y botón— está dentro de un mismo panel blanco y no queda contenido fuera de él

#### Scenario: Botón Mis entradas

- **WHEN** el usuario activa el botón `Mis entradas`
- **THEN** se carga el listado de sus entradas en `/entradas/`