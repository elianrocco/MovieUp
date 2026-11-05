# Spec Delta

## ADDED Requirements

### Requirement: Limpieza masiva por finalización

Además de la eliminación individual, el sistema SHALL eliminar en una sola operación todas las entradas de una función cuyo fin ya pasó, con el mismo efecto que la eliminación por finalización. La operación MUST ser idempotente, MUST NO aceptar motivos distintos de la finalización y MUST NOT modificar las entradas compradas, la disponibilidad ni la distribución de la función.

#### Scenario: Función vencida con entradas

- **WHEN** se ejecuta la limpieza masiva sobre una función cuyo fin ya pasó y que tiene entradas asociadas
- **THEN** todas las entradas de esa función se eliminan

#### Scenario: Función vencida sin entradas

- **WHEN** se ejecuta la limpieza masiva sobre una función cuyo fin ya pasó y que no tiene entradas
- **THEN** la operación termina sin errores

#### Scenario: Limpieza idempotente

- **WHEN** se repite la limpieza masiva sobre la misma función
- **THEN** la operación no borra nada nuevo y no produce errores

#### Scenario: Otra función intacta

- **WHEN** se ejecuta la limpieza masiva sobre una función vencida
- **THEN** las entradas de las demás funciones permanecen

#### Scenario: Contadores de la función intactos

- **WHEN** la limpieza masiva elimina las entradas de una función vencida
- **THEN** las entradas compradas, la disponibilidad y la distribución de esa función conservan sus valores previos
