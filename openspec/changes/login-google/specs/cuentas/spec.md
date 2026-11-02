# Spec Delta: cuentas

## Purpose

Define la identidad de las cuentas del sistema: cómo se crean automáticamente al iniciar sesión con Google, quién es administrador y qué puede ver o cambiar cada rol sobre una cuenta.

## ADDED Requirements

### Requirement: Identidad de la cuenta
El sistema SHALL identificar cada cuenta por un correo electrónico único y guardar un nombre asociado, sin nombre de usuario ni contraseña utilizables para iniciar sesión localmente.

#### Scenario: Alta por Google
- **WHEN** un usuario inicia sesión con Google por primera vez
- **THEN** se crea una cuenta con el correo verificado por Google y con el nombre del perfil de Google

#### Scenario: El mismo correo no genera dos cuentas
- **WHEN** un usuario que ya tiene cuenta vuelve a iniciar sesión con Google
- **THEN** se reutiliza la cuenta existente y no se crea una segunda

#### Scenario: Google no verificó el correo
- **WHEN** Google devuelve un correo sin marcarlo como verificado
- **THEN** el inicio de sesión se rechaza y no se crea una cuenta

### Requirement: Acceso únicamente con Google
El sistema SHALL ofrecer solo el inicio de sesión con Google y MUST NOT ofrecer registro local ni inicio de sesión con usuario y contraseña.

#### Scenario: Pantalla de acceso
- **WHEN** un visitante abre la pantalla de acceso
- **THEN** se muestra únicamente la opción de continuar con Google

#### Scenario: Registro local no disponible
- **WHEN** se solicita la ruta de registro local
- **THEN** la ruta responde sin ofrecer alta de cuenta

### Requirement: Nombre tomado del perfil de Google
El sistema SHALL poblar el nombre desde el perfil de Google en el alta y MUST NOT re-escribirlo en inicios de sesión posteriores.

#### Scenario: Nombre desde el perfil
- **WHEN** se crea la cuenta en el primer inicio de sesión
- **THEN** el nombre queda igual al nombre del perfil de Google

#### Scenario: El nombre no cambia con el tiempo
- **WHEN** el usuario vuelve a iniciar sesión con Google y su nombre de Google cambió
- **THEN** el nombre de la cuenta permanece sin cambios

### Requirement: Nombre de reemplazo
El sistema SHALL asignar un nombre de reemplazo cuando el perfil de Google no incluya nombre.

#### Scenario: Perfil sin nombre
- **WHEN** el perfil de Google no incluye nombre
- **THEN** el nombre de la cuenta se completa con la parte local del correo

### Requirement: Correo inmutable
El sistema MUST NOT permitir que un usuario cambie o agregue direcciones de correo, y el campo de correo SHALL ser de solo lectura en la interfaz de administración de cuentas.

#### Scenario: No se asocia un segundo correo
- **WHEN** el usuario intenta agregar una dirección de correo distinta
- **THEN** el sistema no permite asociar un segundo correo a la cuenta

#### Scenario: El administrador no edita correo ni nombre
- **WHEN** un administrador abre el detalle de una cuenta en el panel de administración
- **THEN** correo y nombre aparecen en solo lectura y no pueden guardarse modificados

### Requirement: Primera cuenta administradora
Si al crear una cuenta no existe ninguna cuenta administradora, esa cuenta SHALL recibir el rol de administración completo. El resto de las altas SHALL crear cuentas comunes.

#### Scenario: Primer usuario del sistema
- **WHEN** inicia sesión con Google el primer usuario del sistema y no hay ninguna cuenta administradora
- **THEN** la cuenta creada obtiene acceso al panel de administración y todos sus permisos

#### Scenario: Usuario posterior
- **WHEN** inicia sesión un usuario después de que ya existe una cuenta administradora
- **THEN** la cuenta creada queda como cuenta común

#### Scenario: Administrador creado por otro medio
- **WHEN** ya existe una cuenta administradora creada por la consola de administración y alguien inicia sesión con Google
- **THEN** la cuenta creada queda como cuenta común

#### Scenario: Dos primeros inicios de sesión simultáneos
- **WHEN** ocurren al mismo tiempo dos inicios de sesión de primer usuario
- **THEN** se crea exactamente una cuenta administradora

### Requirement: Gestión de cuentas desde el panel de administración
El sistema SHALL permitir al administrador listar cuentas, activarlas o desactivarlas y cambiar el indicador de administrador usando el panel de administración de Django, sin una interfaz de gestión propia. Activar el indicador SHALL conceder todos los permisos de administración; desactivarlo SHALL revocarlos.

#### Scenario: Elevar a administrador
- **WHEN** un administrador marca el indicador de administrador en una cuenta y guarda
- **THEN** esa cuenta obtiene acceso al panel y todos los permisos de administración

#### Scenario: Descender a cuenta común
- **WHEN** un administrador desmarca el indicador de administrador y guarda
- **THEN** esa cuenta deja de acceder al panel y pierde todos los permisos de administración

### Requirement: Acceso al panel de administración
El sistema SHALL permitir el acceso al panel de administración solo a cuentas con el indicador de administrador activo.

#### Scenario: Cuenta administradora
- **WHEN** una cuenta con el indicador activo inicia sesión con Google
- **THEN** accede al panel de administración sin ingresar contraseña

#### Scenario: Cuenta común
- **WHEN** una cuenta sin el indicador intenta acceder al panel de administración
- **THEN** se le niega el acceso

### Requirement: Desactivación lógica
El sistema MUST NOT permitir que una cuenta desactivada complete un inicio de sesión.

#### Scenario: Cuenta desactivada
- **WHEN** una cuenta está desactivada y su usuario intenta iniciar sesión con Google
- **THEN** el inicio de sesión no se completa

### Requirement: Borrado bloqueado por entradas asociadas
El sistema MUST NO eliminar una cuenta que tenga entradas asociadas. La validación permanece comentada con un TODO mientras la app `entrada` no exista, porque todavía no hay relación que consultar.

#### Scenario: Cuenta sin entradas asociadas
- **WHEN** se elimina desde el panel de administración una cuenta sin entradas asociadas
- **THEN** la cuenta se elimina

#### Scenario: Cuenta con entradas asociadas
- **WHEN** se intenta eliminar una cuenta que tiene entradas asociadas
- **THEN** la eliminación se rechaza y la cuenta permanece
