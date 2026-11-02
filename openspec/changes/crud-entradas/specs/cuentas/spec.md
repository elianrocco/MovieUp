# Spec Delta

## MODIFIED Requirements

### Requirement: Borrado bloqueado por entradas asociadas
El sistema MUST NO eliminar una cuenta que tenga entradas asociadas. La validación se aplica tanto al borrado individual como a la eliminación masiva desde el panel de administración, ahora que la relación entre cuentas y entradas existe.

#### Scenario: Cuenta sin entradas asociadas
- **WHEN** se elimina desde el panel de administración una cuenta sin entradas asociadas
- **THEN** la cuenta se elimina

#### Scenario: Cuenta con entradas asociadas
- **WHEN** se intenta eliminar una cuenta que tiene entradas asociadas
- **THEN** la eliminación se rechaza y la cuenta permanece

#### Scenario: Eliminación masiva con una cuenta que tiene entradas
- **WHEN** se ejecuta la acción masiva de borrado sobre varias cuentas y alguna tiene entradas asociadas
- **THEN** ninguna cuenta se elimina y el sistema informa el motivo
