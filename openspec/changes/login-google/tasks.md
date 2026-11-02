# Tasks

## Lote 1 — Modelo, configuración y migración

- [ ] 1.1 Levantar el entorno con `docker compose up --build` para instalar `django-allauth` dentro de la imagen; verificar con `docker compose exec web python movie_up/manage.py check` que el proyecto arranca sin errores.
- [ ] 1.2 Definir el modelo `Cuenta(AbstractUser)` en `movie_up/cuentas/models.py` con `username = None`, `correo` único como `USERNAME_FIELD`, `nombre` (150), `first_name` y `last_name` eliminados, `REQUIRED_FIELDS = ['nombre']` y manager propio (`create_user(correo, nombre, **extra)` con `set_unusable_password()`); declarar `AUTH_USER_MODEL = 'cuentas.Cuenta'` y los ajustes de allauth (`SOCIALACCOUNT_ONLY`, `ACCOUNT_LOGIN_METHODS`, `ACCOUNT_SIGNUP_FIELDS`, `ACCOUNT_USER_MODEL_USERNAME_FIELD = None`, `ACCOUNT_MAX_EMAIL_ADDRESSES = 1`) en `movie_up/core/settings.py`; verificar con `docker compose exec web python movie_up/manage.py makemigrations --check --dry-run` que propone `cuentas.0001_initial` y con `manage.py check` sin issues.
- [ ] 1.3 Generar y aplicar `movie_up/cuentas/migrations/0001_initial.py`; verificar con `manage.py migrate --plan` que la migración va antes que las de allauth y con `manage.py migrate --show` que existen `cuentas_cuenta` y las tablas de allauth.
- [ ] 1.4 Agregar en `movie_up/cuentas/tests.py` los tests del modelo: el correo identifica la cuenta y es único, el alta no genera contraseña utilizable y el `nombre` viene del parámetro; verificar con `docker compose exec web python movie_up/manage.py test cuentas`.

## Lote 2 — Cadena de login: alta, nombre y bootstrap

- [ ] 2.1 Crear `movie_up/cuentas/adapters.py` con un `SOCIALACCOUNT_ADAPTER` que implemente `populate_user()` y llene `nombre` con la cadena de respaldo (perfil de Google → nombres extraídos → parte local del correo), y registrarlo en `SOCIALACCOUNT_ADAPTER` de `settings.py`; verificar con un test que una cuenta creada con `name` en el perfil de Google queda con ese `nombre`.
- [ ] 2.2 Agregar el test de respaldo: cuando el perfil de Google no trae `name`, el `nombre` de la cuenta es la parte local del correo; verificar con `test cuentas`.
- [ ] 2.3 Agregar el test de idempotencia: un segundo inicio de sesión con el mismo correo reutiliza la cuenta existente en lugar de crear otra; verificar con `test cuentas`.
- [ ] 3.1 Implementar en `movie_up/cuentas/services.py` la función de promoción del primer administrador, serializada con `GET_LOCK`/`RELEASE_LOCK` de MySQL, que marca `is_staff` solo si no existe ninguna cuenta administradora; verificar con el test: sin administradores → la cuenta creada queda administradora.
- [ ] 3.2 Cubrir con test que, si ya existe una cuenta administradora, el alta nueva queda como cuenta común; verificar con `test cuentas`.
- [ ] 3.3 Conectar la señal `user_signed_up` al servicio de promoción; verificar con un test de integración que un alta por Google dispara la promoción.

## Lote 3 — Panel de administración, guard y cierre

- [ ] 4.1 Registrar `Cuenta` en `movie_up/cuentas/admin.py` con `list_display` (`correo`, `nombre`, indicador de administración), `search_fields` y `readonly_fields = ('correo', 'nombre')`; verificar con un test que el formulario de administración no permite guardar cambios en `correo` ni `nombre`.
- [ ] 4.2 Agregar el guard de borrado bloqueado por entradas asociadas en `CuentaAdmin.delete_model` como bloque comentado con `TODO` que nombra la dependencia de la app `entrada`, siguiendo la convención de `salas` y `peliculas`; verificar con un test que una cuenta sin entradas se elimina y que el `TODO` está presente en el código.
- [ ] 4.3 Cubrir con test que una cuenta con `is_staff` accede a `/admin/` tras iniciar sesión con Google y que una cuenta sin el indicador no accede; verificar con `test cuentas`.
- [ ] 5.1 Actualizar la sección de autenticación y roles de `AGENTS.md`: login solo con Google, alta automática, regla fija del primer administrador y recuperación con `createsuperuser`; verificar que el archivo refleja el comportamiento implementado.
- [ ] 5.2 Actualizar `README.md`: marcar Google OAuth como funcional, documentar el modelo `Cuenta`, los ajustes de allauth y el guard pendiente de `entrada`; verificar que no quedan marcadores `[PENDIENTE]` falsos en la sección de autenticación.
- [ ] 6.1 Correr la suite completa `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas` y verificar 0 fallos.
- [ ] 6.2 Verificar `docker compose exec web python movie_up/manage.py check` y `makemigrations --check --dry-run` sin advertencias ni migraciones pendientes.
- [ ] 6.3 Verificar con Playwright MCP en `http://localhost:8000/` que la pantalla de acceso muestra únicamente la opción de Google, que la ruta de registro local no ofrece alta de cuenta y que `/admin/` no deja entrar a una cuenta sin el indicador; verificar con la consola del navegador sin errores. No cruza la frontera de elegir cuenta.
- [ ] 6.4 Completar la prueba manual con Google siguiendo el checklist de "Workflow follow-up" y registrar el resultado; sin este punto el change no se archiva.

## Workflow follow-up

- Checklist de la prueba manual (la hace el usuario, es la única que valida la integración con Google real):
  - Configurar en Google Cloud Console el redirect URI `http://localhost:8000/accounts/google/login/callback/` con scope `profile` y `email`, y dejar la cuenta en la lista de usuarios de prueba si la app está en estado Testing.
  - Cargar `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` en `.env` sin compartirlos con el agente.
  - Primer inicio de sesión con Google: la cuenta se crea con el correo y el nombre reales y queda marcada administradora.
  - Cerrar sesión y volver a entrar con la misma cuenta: se reutiliza la misma cuenta y sigue siendo administradora.
  - Iniciar con una segunda cuenta de Google: queda como cuenta común y `/admin/` le niega el acceso.
  - Desde `/admin/`, promover esa segunda cuenta: a partir de ahí sí entra al panel.
  - Confirmar que `correo` y `nombre` aparecen en solo lectura y que no se ofrece registro local.
- Correr `openspec validate --specs --strict` antes de archivar el change.
- Sincronizar `specs/cuentas/spec.md` a `openspec/specs/cuentas/spec.md` y archivar con `/opsx:archive`.
