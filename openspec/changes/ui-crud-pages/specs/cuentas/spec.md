# Spec Delta

## ADDED Requirements

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
