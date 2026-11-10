# Spec Delta

## ADDED Requirements

### Requirement: Listado de cuentas en la vista de gestión

La vista de gestión SHALL mostrar un listado de todas las cuentas con el mismo estilo que los listados de películas, funciones y salas, con las columnas correo, nombre y permisos. El listado MUST NO ofrecer crear, ver detalle, editar ni eliminar cuentas.

#### Scenario: Listado con el estilo de los demás listados

- **WHEN** la administradora abre la pestaña `Cuentas` de `/gestion/`
- **THEN** el cuerpo muestra el listado de cuentas con las columnas correo, nombre y permisos, con el mismo aspecto que los otros listados, y la URL permanece en `/gestion/`

#### Scenario: Sin acciones de CRUD

- **WHEN** se inspecciona el listado de cuentas
- **THEN** no aparecen botones de crear, ver detalle, editar ni eliminar; cada fila ofrece únicamente el control de permisos

#### Scenario: Permisos visibles por registro

- **WHEN** el listado renderiza una cuenta administradora y una cuenta común
- **THEN** la columna permisos muestra "Administrador" para la primera y "Usuario común" para la segunda

### Requirement: Control de permisos por cuenta

Cada registro del listado SHALL incluir un control que intercambia la cuenta entre `Usuario común` y `Administrador` sincronizando sus permisos de administración. El control SHALL estar deshabilitado en la fila de la cuenta de la sesión, y el servidor MUST rechazar ese cambio igualmente aunque se envíe directamente.

#### Scenario: Intercambiar una cuenta común a administradora

- **WHEN** la administradora activa el control de una cuenta que es `Usuario común`
- **THEN** la cuenta pasa a `Administrador` y obtiene todos los permisos de administración

#### Scenario: Intercambiar una cuenta administradora a común

- **WHEN** la administradora activa el control de una cuenta administradora que no es la suya
- **THEN** la cuenta pasa a `Usuario común` y pierde todos los permisos de administración

#### Scenario: Control deshabilitado en la propia cuenta

- **WHEN** se renderiza el listado con una sesión iniciada
- **THEN** el control de permisos de la fila de esa cuenta aparece deshabilitado

#### Scenario: El servidor rechaza el cambio sobre la propia cuenta

- **WHEN** se envía directamente el cambio de permisos sobre la cuenta de la sesión
- **THEN** el servidor lo rechaza y la cuenta conserva sus permisos sin cambios

## MODIFIED Requirements

### Requirement: Gestión de cuentas desde el panel de administración
El sistema SHALL permitir al administrador listar cuentas, activarlas o desactivarlas y cambiar el indicador de administrador usando el panel de administración de Django. La vista de gestión ofrece además un listado propio de cuentas con su cambio de permisos. Activar el indicador SHALL conceder todos los permisos de administración; desactivarlo SHALL revocarlos.

#### Scenario: Elevar a administrador
- **WHEN** un administrador marca el indicador de administrador en una cuenta y guarda
- **THEN** esa cuenta obtiene acceso al panel y todos los permisos de administración

#### Scenario: Descender a cuenta común
- **WHEN** un administrador desmarca el indicador de administrador y guarda
- **THEN** esa cuenta deja de acceder al panel y pierde todos los permisos de administración
