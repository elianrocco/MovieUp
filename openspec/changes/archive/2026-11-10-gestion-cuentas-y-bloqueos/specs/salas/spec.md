# Spec Delta

## MODIFIED Requirements

### Requirement: Bloquear operaciones sobre salas en uso

El sistema MUST rechazar la actualización de una sala que tenga al menos una función activa y la eliminación de una sala que tenga cualquier función asociada, activa o no, sin modificar ni borrar datos, e informando el motivo.

#### Scenario: Rechazar la actualización por funciones activas

- **WHEN** la sala tiene al menos una función activa asociada y el administrador intenta actualizarla
- **THEN** el sistema rechaza la operación, no modifica ningún campo y muestra el mensaje "No se puede actualizar una sala con funciones activas."

#### Scenario: Rechazar la actualización aunque no cambien los datos

- **WHEN** la administradora envía el formulario de una sala con funciones activas sin modificar ningún campo
- **THEN** el sistema rechaza la operación y la sala permanece sin cambios

#### Scenario: Rechazar el borrado por funciones activas

- **WHEN** la sala tiene al menos una función activa asociada y el administrador intenta eliminarla
- **THEN** el sistema rechaza el borrado, no elimina nada y muestra el mensaje "No se puede eliminar una sala con funciones asociadas."

#### Scenario: Rechazar el borrado con funciones desactivadas

- **WHEN** la sala solo tiene funciones desactivadas asociadas y el administrador intenta eliminarla
- **THEN** el sistema rechaza el borrado, no elimina nada y muestra el mensaje "No se puede eliminar una sala con funciones asociadas."

#### Scenario: Sala con solo funciones desactivadas es editable

- **WHEN** la sala solo tiene funciones desactivadas y la administradora modifica y guarda alguno de sus campos
- **THEN** el sistema aplica el cambio
