# Design

## Context

Ver `proposal.md` — Why.

Estado actual relevante:

- App `cuentas` creada como esqueleto (`startapp`, `INSTALLED_APPS`, `urls.py` y `services.py` vacíos, `templates/cuentas/`).
- `django-allauth[socialaccount]==65.21.1` ya está en `requirements.txt` y configurado en `movie_up/core/settings.py`: apps, dos backends de autenticación, `AccountMiddleware` y `SOCIALACCOUNT_PROVIDERS['google']` con credenciales leídas desde `.env`. `core/urls.py` ya monta `path('accounts/', include('allauth.urls'))`.
- `AUTH_USER_MODEL` sigue sin definir: el proyecto opera con `auth.User`.
- La observación previa encontró `auth_user` vacía y ninguna app del dominio con foráneas a `User`; esto no basta para declarar segura la sustitución porque ya hay migraciones de Django aplicadas y debe inspeccionarse el esquema persistido.
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
- Registro local y login usuario/contraseña para cuentas Google. La autenticación local del admin se reserva para una cuenta de emergencia creada explícitamente con `createsuperuser`.
- Edición del perfil por parte del usuario (`nombre` y `correo` son inmutables).
- Soporte de otros proveedores de login social.
- Implementar la app `entrada` o su relación con las cuentas.

## Decisions

### D1. Modelo propio `Cuenta(AbstractUser)` en lugar de `auth.User` + perfil

`auth.User.email` es opcional y **no único**, y su `USERNAME_FIELD` debe ser único: el correo no puede ser la identidad sin una migración a mano sobre una tabla de `contrib`. Además, `auth.User` obliga a una columna `username` que el producto no quiere.

`Cuenta(AbstractUser)` con `username = None`, `email = None`, `first_name = None`, `last_name = None`, `correo = EmailField(unique=True)` como `USERNAME_FIELD`, `EMAIL_FIELD = 'correo'`, `REQUIRED_FIELDS = ['nombre']` y `Meta.db_table = 'cuenta'` respeta la tabla propuesta y evita campos duplicados que el producto no usa. Como `AbstractUser.clean()` normaliza `self.email` y sus métodos de nombre usan `first_name`/`last_name`, el modelo sobrescribe `clean()`, `get_full_name()` y `get_short_name()` para operar con `correo` y `nombre`. La alternativa (perfil con `OneToOne`) queda descartada por duplicar identidad y dejar el correo sin unicidad real.

### D2. Manager propio

`AbstractUser` trae `UserManager`, cuya firma incluye `username`. Al eliminar `username`, esa firma deja de servir. Se define un manager propio: `create_user(correo, nombre=None, password=None, **extra)` establece contraseña inutilizable si no recibe una y usa `set_password()` si la recibe; `create_superuser()` establece `is_staff=True` e `is_superuser=True` y acepta la contraseña de recuperación de `createsuperuser`. Las cuentas creadas por Google reciben contraseña inutilizable explícitamente en el adapter social. Así, cuentas sociales no tienen contraseña local, mientras que la cuenta de emergencia creada por `createsuperuser` sí puede usar el login local del admin.

### D3. `nombre` como campo propio, mapeado con un adapter de allauth

allauth puebla `first_name`/`last_name`; el producto pide un solo `nombre`. Se declaran `first_name = None` y `last_name = None` para eliminar esas columnas y se agrega `nombre = CharField(max_length=150)`.

El mapeo se resuelve en un `SOCIALACCOUNT_ADAPTER` propio que implementa `populate_user()`, usando tanto el diccionario normalizado `data` como los datos originales `sociallogin.account.extra_data`, con esta cadena de respaldo:

1. `extra_data['name']` (perfil completo de Google).
2. combinación de los nombres que allauth extrajo del proveedor.
3. parte local del correo.

El mismo adapter acepta el alta solo si `sociallogin.email_addresses` contiene el correo recibido como verificado por Google. `ACCOUNT_EMAIL_VERIFICATION='none'` evita correos de verificación propios, pero no sustituye esta comprobación. allauth 65.21.1 ya llama `set_unusable_password()` en `DefaultSocialAccountAdapter.save_user()` para las cuentas sociales; se conserva ese comportamiento estándar.

Se elige el adapter en lugar de una señal porque es el punto de extensión documentado de allauth para poblar el usuario en el alta, y porque centraliza el mapeo en un solo lugar testeable.

### D4. Bootstrap del primer administrador

La promoción se ejecuta en el alta de la cuenta, dentro de una función de `services.py` invocada desde la señal `user_signed_up`, que es la que allauth emite después de crear la cuenta. La función chequea si existe alguna cuenta administradora y, si no existe, marca la recién creada con `is_staff=True` e `is_superuser=True`. El flag visible de administración es una sola decisión de rol, pero se sincroniza con ambos campos de Django: `is_staff` permite entrar al admin y `is_superuser` concede todos los permisos de modelos.

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
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'correo'
ACCOUNT_MAX_EMAIL_ADDRESSES = 1
```

`SOCIALACCOUNT_ONLY` desactiva las rutas de registro y login local para cuentas regulares; allauth exige `ACCOUNT_EMAIL_VERIFICATION = 'none'` cuando esa opción está activa. El email usado para ingresar sigue validándose como dato del proveedor social; no se envían correos de verificación propios. `ACCOUNT_USER_MODEL_USERNAME_FIELD = None` es obligatorio porque el modelo no tiene `username`, y `ACCOUNT_USER_MODEL_EMAIL_FIELD = 'correo'` indica a allauth el nombre personalizado del campo de correo (el default sería `email`). El login local con `ModelBackend` queda como recuperación para superusuarios creados explícitamente con `createsuperuser`, no para cuentas Google.

### D7. Orden de migraciones y recreación de la base

El custom user model debe aparecer en su primera migración (`cuentas/0001_initial.py`), y `AUTH_USER_MODEL` debe estar configurado antes de aplicar nuevas migraciones de allauth. El entrypoint de `web` ejecuta `migrate --noinput` automáticamente al iniciar, por lo que no se puede levantar `web` antes de preparar el modelo y su migración: el primer arranque podría aplicar las migraciones con `auth.User` como modelo activo.

Django documenta que cambiar `AUTH_USER_MODEL` después de crear tablas es posible, pero complejo: puede requerir corregir el esquema, mover datos y re-aplicar migraciones manualmente. Que `auth_user` esté vacía y que las apps del dominio no tengan FKs a User no demuestra que el cambio sea seguro; las migraciones ya aplicadas de Django (por ejemplo, admin/log entries) y el esquema real también deben revisarse.

Secuencia obligatoria:

1. Definir `Cuenta` y `AUTH_USER_MODEL` antes de iniciar `web`.
2. Construir la imagen sin arrancar servicios (`docker compose build web`).
3. Generar `cuentas/0001_initial.py` usando un comando que omita el entrypoint automático, sin ejecutar `migrate`.
4. Inspeccionar el estado real de `django_migrations`, tablas, datos y FKs y revisar `migrate --plan` antes de cualquier migración de escritura.
5. Seguir la estrategia de preservación aprobada por el usuario; no borrar el volumen.
6. Aplicar las migraciones y comprobar que el modelo propio está en la migración inicial y antes de las nuevas migraciones de allauth.

Inspección read-only realizada el 2026-11-02:

- La base tiene aplicadas `auth.0001`–`auth.0012`, `admin.0001`–`admin.0003`, `peliculas.0001`, `salas.0001` y `funciones.0001`; todavía no tiene migraciones de allauth ni de `cuentas`.
- `auth_user`, `auth_user_groups`, `auth_user_user_permissions` y `django_admin_log` tienen 0 filas. Las tres tablas laterales/log existentes tienen FK a `auth_user`.
- `django_admin_log.user_id` es `INT`, pero `Cuenta.id` será `BIGINT` por `BigAutoField`; la migración debe ensanchar esa columna antes de crear la nueva FK.
- Hay datos de dominio que conviene preservar: 4 películas, 3 salas y 2 funciones.
- Con el nuevo `AUTH_USER_MODEL`, Django rechaza `migrate --plan` y `makemigrations --check --dry-run`: `admin.0001_initial` ya figura aplicado antes de su nueva dependencia `cuentas.0001_initial`.
- `manage.py check` ya no tiene errores críticos, pero emite dos warnings W036 porque MySQL no soporta dos constraints únicos condicionales del modelo allauth `EmailAddress`. No se silenciaron.

**Estrategia de preservación aprobada por el usuario:** hacer backup; quitar de `django_migrations` solo las filas `admin.0001_initial`, `admin.0002_logentry_remove_auto_add` y `admin.0003_logentry_add_action_flag_choices`; aplicar `cuentas.0001_initial`; volver a registrar las migraciones admin como aplicadas sin repetir sus operaciones (la tabla `django_admin_log` ya existe); y ejecutar una migración `RunPython`/SQL idempotente que cambie `django_admin_log.user_id` de `INT` a `BIGINT` y su FK desde `auth_user(id)` a `cuenta(id)`. Esa migración usa `atomic = False`, requerido para que Django permita DDL en MySQL; la operación se agrupa en un único `ALTER TABLE`. Las tablas laterales antiguas permanecen vacías y sin uso. Luego se aplican las migraciones restantes de allauth.

Esta ruta evita perder los datos de películas/salas/funciones, pero altera el historial de migraciones y el esquema de auditoría. El usuario aprobó esta estrategia; se realizará backup antes de la primera escritura. No se ejecutará reset del volumen.

### D8. Guard de borrado con TODO

La regla "no borrar una cuenta con entradas asociadas" no puede implementarse todavía: la app `entrada` no existe y no hay relación que consultar. Siguiendo la convención de MovieUp, el guard queda **comentado con un `TODO`** que nombra el requisito y apunta a la app futura, igual que los guards de `salas` y `peliculas` hacia `funciones`.

### D9. Panel de administración

Registro en `admin.py`: `list_display` con `correo`, `nombre` e indicador de administración, `search_fields` por `correo` y `nombre`, y `readonly_fields = ('correo', 'nombre')`. El indicador visible controla `is_staff`; al guardar se sincroniza `is_superuser` para conceder o revocar todos los permisos en conjunto. `is_superuser` no se edita independientemente. No se crean vistas propias.

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
- **Las migraciones existentes pueden conservar referencias a `auth.User`** → inspeccionar `django_migrations` y las FKs reales antes de escribir; documentar el plan de conversión y no aplicar migraciones hasta resolver incompatibilidades.
- **Reset del volumen de MySQL pierde películas, salas y funciones de prueba** → nunca ejecutar `docker compose down -v` sin autorización explícita; preferir backup y una migración de preservación si es viable.

## Migration Plan

1. Definir `Cuenta`, `AUTH_USER_MODEL` y los ajustes de allauth (D6) antes de iniciar `web`.
2. Construir la imagen sin arrancar servicios (`docker compose build web`).
3. Generar `cuentas/0001_initial.py` con `docker compose run --rm --no-deps --entrypoint python web movie_up/manage.py makemigrations cuentas`, que omite el entrypoint que migra automáticamente.
4. Iniciar solo el servicio MySQL; consultar `django_migrations`, tablas, datos y claves foráneas. Ejecutar `migrate --plan` sin aplicar cambios y registrar la incompatibilidad admin/custom-user.
5. Presentar la estrategia de preservación (backup, reparación controlada del historial admin y migración de FK `django_admin_log`) y esperar aprobación explícita; reset solo con autorización separada.
6. Aplicar la estrategia aprobada, luego migraciones de allauth; solo entonces iniciar `web` y verificar `manage.py check` y suite `test peliculas salas funciones cuentas`.
7. Verificación en navegador: login con Google, alta de cuenta, segundo login como cuenta común y acceso a `/admin/`.

Rollback: no se asume que revertir `AUTH_USER_MODEL` sea seguro después de aplicar migraciones. La estrategia de rollback debe quedar definida a partir del esquema inspeccionado y contar con backup previo. `docker compose down -v` es destructivo y requiere autorización explícita.

## Open Questions

- **¿Quién usa las plantillas de allauth?** allauth trae sus propias plantillas (`account/login.html`, etc.). Personalizarlas por una capa de estilo de MovieUp es cosmético y no cambia ningún requisito; se resuelve en la implementación si hace falta.
- **¿Vista "Mi perfil" para el cliente?** Hoy el requisito dice que el cliente no edita nada. Si más adelante se pide ver sus datos desde la app, se agrega como requisito en un cambio posterior.
