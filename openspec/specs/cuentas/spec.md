# cuentas Specification

## Purpose

Define la identidad de las cuentas del sistema: cómo se crean automáticamente al iniciar sesión con Google, quién es administrador y qué puede ver o cambiar cada rol sobre una cuenta.

## Requirements

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

### Requirement: Acceso de cuentas sociales únicamente con Google
El sistema SHALL ofrecer inicio de sesión con Google para cuentas sociales y MUST NOT ofrecer registro local ni acceso con contraseña local para esas cuentas. La única excepción es el acceso de recuperación al Django Admin con una cuenta de emergencia creada explícitamente mediante `createsuperuser`.

#### Scenario: Pantalla de acceso
- **WHEN** un visitante abre la pantalla de acceso
- **THEN** se muestra únicamente la opción de continuar con Google

#### Scenario: Registro local no disponible
- **WHEN** se solicita la ruta de registro local
- **THEN** la ruta responde sin ofrecer alta de cuenta

#### Scenario: Recuperación administrativa local
- **WHEN** un superusuario de emergencia creado mediante `createsuperuser` usa las credenciales locales en el formulario del Django Admin
- **THEN** puede acceder al panel para recuperar la administración del sistema

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
El sistema SHALL permitir al administrador listar cuentas, activarlas o desactivarlas y cambiar el indicador de administrador usando el panel de administración de Django. La vista de gestión ofrece además un listado propio de cuentas con su cambio de permisos. Activar el indicador SHALL conceder todos los permisos de administración; desactivarlo SHALL revocarlos.

#### Scenario: Elevar a administrador
- **WHEN** un administrador marca el indicador de administrador en una cuenta y guarda
- **THEN** esa cuenta obtiene acceso al panel y todos los permisos de administración

#### Scenario: Descender a cuenta común
- **WHEN** un administrador desmarca el indicador de administrador y guarda
- **THEN** esa cuenta deja de acceder al panel y pierde todos los permisos de administración

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

### Requirement: Inicio de sesión directo con Google
Todo punto de entrada de inicio de sesión de la interfaz SHALL conducir directamente al flujo de Google sin renderizar la pantalla intermedia de acceso, conservando el destino de retorno cuando lo haya.

#### Scenario: Botón Login del nav
- **WHEN** un visitante hace clic en `Login` del nav
- **THEN** el navegador es conducido al flujo de inicio de sesión con Google y no se muestra la pantalla de acceso

#### Scenario: Compra sin sesión
- **WHEN** un visitante hace clic en `Comprar entradas` sin sesión iniciada
- **THEN** es conducido al flujo de Google con retorno a la página principal

#### Scenario: Retorno conservado
- **WHEN** el inicio de sesión se solicita con un destino de retorno
- **THEN** tras autenticarse con Google se llega a ese destino

#### Scenario: La pantalla de acceso sigue existiendo
- **WHEN** se solicita directamente la ruta de acceso
- **THEN** responde mostrando únicamente la opción de Google, sin registro local

### Requirement: Cierre de sesión desde el nav sin página intermedia
El control `Logout` del nav SHALL cerrar la sesión con un `POST` protegido por token CSRF y redirigir a la página principal, sin mostrar la pantalla de confirmación de cierre.

#### Scenario: Cierre con una sola activación
- **WHEN** una cuenta autenticada activa `Logout`
- **THEN** su sesión termina y aterriza en la página principal

#### Scenario: Sin token no se cierra la sesión
- **WHEN** se envía un cierre de sesión sin token CSRF
- **THEN** la solicitud es rechazada y la sesión permanece abierta

#### Scenario: Visitante en la ruta de cierre
- **WHEN** un visitante sin sesión abre la ruta de cierre
- **THEN** es redirigido a la página principal

#### Scenario: Sin controles de cierre por GET
- **WHEN** se revisa la navegación de la interfaz
- **THEN** ningún control de la UI invoca el cierre de sesión con un `GET`
