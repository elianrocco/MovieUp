# Spec Delta

## ADDED Requirements

### Requirement: Botón de validación en el nav

El sistema SHALL mostrar en el nav de todas las vistas, al extremo izquierda, un botón dorado con enlace a la vista de validación de entradas, visible únicamente para cuentas administradoras.

#### Scenario: Administradora en cualquier vista

- **WHEN** una cuenta administradora navega a cualquier vista
- **THEN** el botón dorado aparece al extremo izquierdo del nav

#### Scenario: Cuenta común no lo ve

- **WHEN** una cuenta común autenticada navega a cualquier vista
- **THEN** el nav no muestra el botón de validación

#### Scenario: Visitante no lo ve

- **WHEN** un visitante navega a cualquier vista
- **THEN** el nav no muestra el botón de validación

#### Scenario: Clic en el botón

- **WHEN** la administradora hace clic en el botón de validación
- **THEN** es conducida a la vista de validación de entradas
