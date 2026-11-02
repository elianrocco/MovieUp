# Design

## Context

Ver `proposal.md` — Why.

Estado actual relevante:

- App `cuentas` creada como esqueleto (`startapp`, `INSTALLED_APPS`, `urls.py` y `services.py` vacíos, `templates/cuentas/`).
- `django-allauth[socialaccount]==65.21.1` ya está en `requirements.txt` y configurado en `movie_up/core/settings.py`: apps, dos backends de autenticación, `AccountMiddleware` y `SOCIALACCOUNT_PROVIDERS['google']` con credenciales leídas desde `.env`. `core/urls.py` ya monta `path('accounts/', include('allauth.urls'))`.
- `AUTH_USER_MODEL` sigue sin definir: el proyecto opera con `auth.User`.
- `auth_user` está vacía y ninguna app tiene foráneas a `User`, por lo que cambiar el modelo de usuario todavía no rompe nada.
- La decisión de arquitectura ya está cerrada: modelo propio `Cuenta(AbstractUser)` (ver `README.md`, sección Autenticación y roles).
- Django 6.1.1, MySQL, `DEFAULT_AUTO_FIELD` en `BigAutoField`.

## Goals / Non-Goals

**Goals:**

- Un modelo de usuario propio que identifique cuentas por `correo` único y guarde `nombre`.
- Alta de cuenta automática al iniciar sesión con Google, sin formulario de registro.
- Regla de bootstrap del primer administrador.
- Gestión de cuentas resuelta con Django admin, con `correo` y `nombre` en solo lectura.
- Guards de borrado preparados para cuando exista la app `entrada`.

**Non-Goals:**

- Interfaz web propia de gestión de cuentas (CRUD de cuentas): se usan las interfaces de Django.
- Registro local, login por usuario/contraseña o recuperación de contraseña.
- Edición del perfil por parte del usuario (`nombre` y `correo` son inmutables).
- Soporte de otros proveedores de login social.
- Implementar la app `entrada` o su relación con las cuentas.

## Decisions

### D1. Modelo propio `Cuenta(AbstractUser)` en lugar de `auth.User` + perfil

`auth.User.email` es opcional y **no único**, y su `USERNAME_FIELD` debe ser único: el correo no puede ser la identidad sin una migración a mano sobre una tabla de `contrib`. Además, `auth.User` obliga a una columna `username` que el producto no quiere.

`Cuenta(AbstractUser)` con `username = None`, `correo = EmailField(unique=True)` como `USERNAME_FIELD` y `REQUIRED_FIELDS = ['nombre']` entrega exactamente las columnas pedidas. La alternativa (perfil con `OneToOne`) descartada por duplicar identidad y dejar el correo sin unicidad real.

### D2. Manager propio

`AbstractUser` trae `UserManager`, cuya firma es `create_user(username, email, password)`. Al eliminar `username`, esa firma deja de servir. Se define un manager propio que firma `create_user(correo, nombre=None, **extra)` y usa `set_unusable_password()` en el alta, porque el acceso es siempre por Google.

### D3. `nombre` como campo propio, mapeado con un adapter de allauth

allauth puebla `first_name`/`last_name`; el producto pide un solo `nombre`. Se declaran `first_name = None` y `last_name = None` para eliminar esas columnas y se agrega `nombre = CharField(max_length=150)`.

El mapeo se resuelve en un `SOCIALACCOUNT_ADAPTER` propio que implementa `populate_user()`, leyendo el nombre del perfil de Google (`extra_data`) con esta cadena de respaldo:

1. `extra_data['name']` (perfil completo de Google).
2. combinación de los nombres que allauth extrajo del proveedor.
3. parte local del correo.

Se elige el adapter en lugar de una señal porque es el punto de extensión documentado de allauth para poblar el usuario en el alta, y porque centraliza el mapeo en un solo lugar testeable.

### D4. Bootstrap del primer administrador

La promoción se ejecuta en el alta de la cuenta, dentro de una función de `services.py` invocada desde la señal `user_signed_up`, que es la que allauth emite después de crear la cuenta. La función chequea si existe alguna cuenta administradora y, si no existe, marca la recién creada.

Para que dos altas simultáneas no generen dos administradores, el chequeo y la promoción se serializan con el lock de adquisición de MySQL (`GET_LOCK` / `RELEASE_LOCK`) sobre un nombre fijo de la aplicación. Alternativa evaluada: `transaction.atomic()` + rechequeo tras el `save()`; queda descartada porque no elimina la ventana de carrera y el escenario exige exactamente un administrador.

**Decisión registrada por el usuario:** la regla es fija y no se puede desactivar por variable de entorno.

### D5. Inmutabilidad de `correo` y `nombre`

Dos mecanismos, porque hay dos vías de escritura:

- `ACCOUNT_MAX_EMAIL_ADDRESSES = 1` bloquea que el usuario agregue o cambie correos desde allauth (documentado como: *"Setting this to 1 prevents users from changing their email address"*).
- `readonly_fields = ('correo', 'nombre')` en el `ModelAdmin` impide que el administrador los modifique desde el panel.

El nombre además no se re-escribe: allauth solo puebla el usuario en el alta, no en los logins posteriores.

### D6. Ajustes de allauth para el caso de uso

```python
SOCIALACCOUNT_ONLY = True
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*']
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_MAX_EMAIL_ADDRESSES = 1
```

`SOCIALACCOUNT_ONLY` desactiva las rutas de registro y login local; `ACCOUNT_USER_MODEL_USERNAME_FIELD = None` es obligatorio porque el modelo no tiene `username`.

### D7. Orden de migraciones y recreación de la base

`AUTH_USER_MODEL` debe declararse antes de aplicar las migraciones de allauth. Se hace en este orden: declarar el setting, `makemigrations cuentas`, y recién entonces `migrate`.

**La recreación de la base NO es obligatoria**, a diferencia de lo que se planteó al inicio: `auth_user` está vacía, ninguna app tiene foráneas a `User` y las migraciones de `contrib.auth` aplicadas no se re-ejecutan. `migrate` agrega `cuentas_cuenta` y las tablas de allauth, y la tabla `auth_user` queda como residuo vacío e inofensivo.

Plan B: si `migrate --plan` muestra algo inesperado, recrear con `docker compose down -v` y `docker compose up --build`, perdiendo los datos de prueba de `peliculas` y `salas`.

### D8. Guard de borrado con TODO

La regla "no borrar una cuenta con entradas asociadas" no puede implementarse todavía: la app `entrada` no existe y no hay relación que consultar. Siguiendo la convención de MovieUp, el guard queda **comentado con un `TODO`** que nombra el requisito y apunta a la app futura, igual que los guards de `salas` y `peliculas` hacia `funciones`.

### D9. Panel de administración

Registro estándar en `admin.py`: `list_display` con `correo`, `nombre` e indicador de administración, `search_fields` por `correo` y `nombre`, y `readonly_fields = ('correo', 'nombre')`. No se crean vistas propias.

### D10. Estrategia de prueba sin credenciales de Google

El secreto del cliente no se comparte con el agente: `settings.py` lo lee con `os.environ.get(...)`, por lo que el código es idéntico con el valor vacío o real, y solo el login en vivo falla. La cobertura se reparte en cuatro niveles:

1. **Servicio y modelo, sin red:** identidad por correo, unicidad, mapeo de `nombre` con su respaldo, promoción con `GET_LOCK`, campos en solo lectura y guard de borrado.
2. **Rutas y plantillas:** pantalla de acceso con única opción de Google, ruta de registro local sin alta de cuenta y `/admin/` protegido.
3. **Flujo OAuth simulado:** se parchea el intercambio del token para recorrer redirect → callback → alta de cuenta → `populate_user` → señal → promoción, con credenciales falsas. Cubre toda la lógica del servidor sin que exista Google.
4. **Flujo real con Google:** lo realiza el usuario a mano. Es la única validación de la integración real (redirect URI, campos devueltos, usuarios de prueba) y es condición para archivar el cambio.

Alternativa evaluada: el provider de prueba que allauth incluye desde la versión 0.62.0. Quedó descartada porque no tiene página propia de documentación en 65.21.1; el mock del intercambio de token cubre el mismo alcance sin depender de un componente no documentado.

## Risks / Trade-offs

- **Cualquiera que inicie sesión primero queda como administrador** → aceptado explícitamente por el usuario; es la regla de bootstrap. Documentado en `README.md` como limitación de seguridad al desplegar.
- **Si se desactiva la única cuenta administradora no queda nadie para administrar** → recuperación mediante `createsuperuser`; queda anotado en la documentación.
- **`GET_LOCK` es específico de MySQL** → aceptado: el proyecto usa `mysqlclient` contra MySQL, no hay portabilidad que preservar.
- **allauth no llena `nombre` por defecto** → resuelto con el adapter de D3; si el adapter no se registra, todas las cuentas quedan sin nombre, por eso el alta lo cubre con un test.
- **El borrado desde el admin todavía no está bloqueado por entradas** → cubierto con el TODO de D8; se cierra cuando exista `entrada`.
- **Queda una tabla `auth_user` vacía si no se recrea la base** → inofensiva; se puede eliminar a mano después si molesta.

## Migration Plan

1. Declarar `AUTH_USER_MODEL = 'cuentas.Cuenta'` y los ajustes de allauth (D6).
2. `docker compose up --build` para instalar allauth en la imagen.
3. `python movie_up/manage.py makemigrations cuentas` → `cuentas/0001_initial.py`.
4. `python movie_up/manage.py migrate --plan` y revisar el orden antes de aplicar.
5. `python movie_up/manage.py migrate` (crea `cuentas_cuenta` y las tablas de allauth).
6. `python movie_up/manage.py check` y suite completa: `test peliculas salas funciones cuentas`.
7. Verificación en navegador: login con Google, alta de cuenta, segundo login como cuenta común y acceso a `/admin/`.

Rollback: una vez aplicadas las migraciones, la única vuelta atrás es recrear la base (`docker compose down -v`), porque `AUTH_USER_MODEL` no se puede cambiar después sin cirugía (documentación de Django: *"You cannot change the AUTH_USER_MODEL setting during the lifetime of a project ... without serious effort"*).

## Open Questions

- **¿Quién usa las plantillas de allauth?** allauth trae sus propias plantillas (`account/login.html`, etc.). Personalizarlas por una capa de estilo de MovieUp es cosmético y no cambia ningún requisito; se resuelve en la implementación si hace falta.
- **¿Vista "Mi perfil" para el cliente?** Hoy el requisito dice que el cliente no edita nada. Si más adelante se pide ver sus datos desde la app, se agrega como requisito en un cambio posterior.
