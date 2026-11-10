# Spec Delta

## ADDED Requirements

### Requirement: Botones del formulario de edición de los CRUDs

El formulario de edición de películas, funciones y salas SHALL ofrecer el botón de envío `Guardar cambios` y la acción `Cancelar`, y `Cancelar` SHALL mostrar el detalle del registro en lugar del listado, tanto en la página completa como dentro del panel de gestión.

#### Scenario: Etiquetas del formulario de edición

- **WHEN** se abre el formulario de edición de una película, una función o una sala
- **THEN** el botón de envío muestra `Guardar cambios` y la acción de salida muestra `Cancelar`

#### Scenario: Cancelar la edición de una película

- **WHEN** la administradora hace clic en `Cancelar` en el formulario de edición de una película
- **THEN** el cuerpo muestra el detalle de esa película sin haberla modificado

#### Scenario: Cancelar la edición dentro de la gestión

- **WHEN** se cancela una edición dentro de `/gestion/`
- **THEN** el cuerpo muestra el detalle del registro y la URL permanece en `/gestion/`

## MODIFIED Requirements

### Requirement: Cuentas dentro del shell

El botón `Cuentas` SHALL comportarse como las demás pestañas del subNAV: al hacer clic, el cuerpo SHALL mostrar el listado de cuentas con el shell de la web —nav global, subNAV, footer y paleta—, sin cambiar la URL, sin recargar la página y sin navegar al panel de administración de Django.

#### Scenario: Panel de cuentas integrado

- **WHEN** la administradora hace clic en `Cuentas`
- **THEN** el listado de cuentas aparece en el cuerpo con el nav, el subNAV, el footer y la paleta de la web, y la URL permanece en `/gestion/`

#### Scenario: Sin navegación al administrador

- **WHEN** la administradora hace clic en `Cuentas`
- **THEN** el navegador no navega a `/admin/` ni a ninguna otra URL fuera de la gestión

### Requirement: Vuelta al listado con datos frescos

Cada vista cargada dentro de la gestión SHALL ofrecer un control de salida: desde el detalle o la confirmación SHALL regresar al listado de la pestaña activa y desde un formulario SHALL salir sin crear ni modificar registros; el listado SHALL reflejar el estado actual de los registros.

#### Scenario: Volver desde el detalle o la confirmación

- **WHEN** la administradora activa el control de vuelta desde un detalle o una confirmación
- **THEN** el cuerpo vuelve a mostrar el listado de la pestaña

#### Scenario: Volver cancelando un formulario

- **WHEN** la administradora cancela un formulario de alta
- **THEN** el cuerpo vuelve al listado sin crear ningún registro

#### Scenario: Cancelar un formulario de edición

- **WHEN** la administradora cancela un formulario de edición
- **THEN** el cuerpo muestra el detalle del registro sin modificarlo

#### Scenario: Lista actualizada tras una operación

- **WHEN** la administradora crea, actualiza o elimina un registro dentro del panel
- **THEN** el listado muestra el registro nuevo, sus cambios o su ausencia
