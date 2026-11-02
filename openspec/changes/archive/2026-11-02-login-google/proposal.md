# Proposal

## Why

Hoy el sistema no tiene ningún tipo de identidad: existen `peliculas`, `salas` y `funciones`, pero nada sabe quién compra, quién administra ni qué cuenta hizo qué. `auth_user` está vacía, no hay ningún flujo de autenticación y AGENTS.md exige login con Google. Sin un modelo de usuario, los casos de uso "Vincular cuenta de Google" y "Comprar entradas" no tienen dueño.

## What Changes

- Nuevo modelo de usuario `Cuenta(AbstractUser)` en la app `cuentas`, declarado como `AUTH_USER_MODEL = 'cuentas.Cuenta'`: `correo` único como `USERNAME_FIELD`, `nombre` (150), `is_staff`/`is_superuser` sincronizados por un solo indicador de administración, `is_active` para desactivación lógica, sin columnas `username`, `email`, `first_name` ni `last_name`; usa el nombre de tabla `cuenta` del esquema entregado.
- **BREAKING:** Se cambia el modelo de usuario por defecto después de que el proyecto ya aplicó migraciones. Django no hace este cambio automáticamente: antes de migrar hay que inspeccionar el estado real de la base y definir una estrategia segura (preservar datos con ajustes manuales o recrear la base si el usuario lo autoriza). No se ejecutará un reset destructivo sin autorización explícita.
- Login únicamente con Google, gestionado por django-allauth: sin registro local, sin login por usuario y contraseña, con el correo como identidad y `ACCOUNT_MAX_EMAIL_ADDRESSES = 1` para que no se pueda cambiar.
- Alta automática de cuenta en el primer inicio de sesión con Google: `correo` y `nombre` se toman del perfil de Google, sin formulario de registro.
- La primera cuenta creada se marca administradora con permisos completos si no existe ninguna; las altas posteriores son cuentas comunes. En Django esto sincroniza `is_staff` y `is_superuser`.
- La gestión de cuentas se hace con las interfaces de Django (Django admin): listado, activación/desactivación y elevación/descenso del flag de administrador. `correo` y `nombre` son de solo lectura.
- Guard de borrado: no se puede eliminar una cuenta con entradas asociadas. Como la app `entrada` todavía no existe, la validación se deja comentada con un TODO (convención de MovieUp para guards pendientes).
- `nombre` no se re-escribe en inicios de sesión posteriores; proviene del perfil de Google y se mantiene.

## Capabilities

### New Capabilities

- `cuentas`: identidad y autenticación de las cuentas — modelo de usuario, alta automática vía Google, regla de bootstrap del primer administrador, inmutabilidad de correo y nombre, y reglas de acceso y borrado.

### Modified Capabilities

<!-- Ninguna spec existente cambia de requisitos. -->

## Impact

- `movie_up/cuentas/models.py`: modelo `Cuenta` y manager propio.
- `movie_up/cuentas/admin.py`: registro en Django admin con `correo` y `nombre` en solo lectura.
- `movie_up/cuentas/adapters.py`: mapeo del perfil de Google (`name`) al campo `nombre`.
- `movie_up/core/settings.py`: `AUTH_USER_MODEL` y ajustes de allauth (`SOCIALACCOUNT_ONLY`, `ACCOUNT_LOGIN_METHODS`, `ACCOUNT_SIGNUP_FIELDS`, `ACCOUNT_MAX_EMAIL_ADDRESSES`, `ACCOUNT_USER_MODEL_USERNAME_FIELD`, `ACCOUNT_USER_MODEL_EMAIL_FIELD = 'correo'`).
- `movie_up/cuentas/migrations/0001_initial.py`: debe generar y aplicarse antes que las migraciones de allauth.
- Dependencia `django-allauth[socialaccount]` ya presente en `requirements.txt`.
- Inspección de `django_migrations`, tablas y claves foráneas existentes antes de elegir y aplicar la estrategia de migración; no se asume que recrear la base sea obligatorio ni que el cambio sea seguro sin ajustes.
- `AGENTS.md` y `README.md`: secciones de autenticación y roles.
- Sin cambios de requisitos en `movies`, `salas` ni `funciones`.
