# Spec Delta

## ADDED Requirements

### Requirement: Desactivación automática de funciones vencidas

Cuando el sistema ejecuta el barrido de funciones vencidas de la compra, toda función de la película con fin menor o igual al momento actual SHALL quedar con `funcion_activa` inactivo, aunque ya estuviera inactiva. La desactivación MUST ser idempotente y MUST NOT modificar el inicio, el fin, el precio de la entrada, la disponibilidad ni la distribución de la función.

#### Scenario: Función vencida activa

- **WHEN** el barrido procesa una función con fin anterior al momento actual y `funcion_activa` activo
- **THEN** la función queda con `funcion_activa` inactivo

#### Scenario: Función vencida ya inactiva

- **WHEN** el barrido procesa una función con fin anterior al momento actual y `funcion_activa` ya inactivo
- **THEN** la función sigue inactiva y la operación no produce errores

#### Scenario: Función futura intacta

- **WHEN** el barrido procesa una película que tiene una función con fin posterior al momento actual
- **THEN** esa función conserva su estado de activación

#### Scenario: Resto de los datos intactos

- **WHEN** el barrido desactiva una función vencida
- **THEN** el inicio, el fin, el precio de la entrada, la disponibilidad y la distribución conservan sus valores previos
