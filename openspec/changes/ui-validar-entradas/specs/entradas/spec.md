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
