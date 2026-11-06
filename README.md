# MovieUp - Log de Ingeniería

## 1. Visión general y arquitectura del sistema

**Fuente:** [AGENTS.md](AGENTS.md), [core/settings.py](movie_up/core/settings.py), [core/urls.py](movie_up/core/urls.py), [movie_up/](movie_up/), [requirements.txt](requirements.txt), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)

### Propósito del proyecto
MovieUp es un sistema web para la gestión y comercialización de entradas de cine. Permite a los usuarios comprar entradas, gestionar sus compras, y a los administradores gestionar películas, salas, funciones y ventas. [AGENTS.md](AGENTS.md)

### Stack tecnológico
- **Backend:** Python 3.14.7 con Django 6.1.1 y LangChain 1.4.0 [AGENTS.md](AGENTS.md), [requirements.txt](requirements.txt), [Dockerfile](Dockerfile)
- **Frontend:** HTML (Living Standard), CSS3 (Snapshot 2023) y JavaScript (ES2025) [AGENTS.md](AGENTS.md)
- **Base de datos:** MySQL 9.7.2 LTS [AGENTS.md](AGENTS.md), [docker-compose.yml](docker-compose.yml), [core/settings.py](movie_up/core/settings.py)
- **Pasarela de pagos:** Mercado Pago SDK Python 3.5.0 [AGENTS.md](AGENTS.md), [requirements.txt](requirements.txt)
- **Control de versiones:** Git + GitHub [AGENTS.md](AGENTS.md)
- **Containerización:** Docker 29.8.0 [AGENTS.md](AGENTS.md), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)
- **Versiones exactas:** definidas en `requirements.txt`, `Dockerfile` y `docker-compose.yml` [AGENTS.md](AGENTS.md)

### Arquitectura (Patrón MVT de Django)
El proyecto sigue el patrón **Modelo-Vista-Template (MVT)** de Django como arquitectura base, extendido con **Service Layer** [AGENTS.md](AGENTS.md).

- **Modelo (Model):** Define la estructura de datos y la persistencia en MySQL mediante `models.py`. La app `peliculas` contiene el modelo `Pelicula` con 9 campos (título, género, duración, descripción, clasificación, fecha de estreno, URL del tráiler, imagen de portada, en cartelera) [models.py](movie_up/peliculas/models.py).
- **Vista (View):** Lógica HTTP delgada en `views.py` (request → service → response), enrutada desde `urls.py`. La app `peliculas` implementa 5 vistas funcionales: list, detail, create, update y delete [views.py](movie_up/peliculas/views.py).
- **Template:** Presentación mediante el motor de plantillas de Django con HTML/CSS/JS.
- **Service Layer:** Lógica de negocio concentrada en `services.py`. Toda app incluye este archivo para mantener consistencia entre apps [AGENTS.md](AGENTS.md).

#### Actualizaciones parciales y valores booleanos
`update_pelicula()` omite solo valores `None` y `''`; aplica `False` como valor explícito para permitir desmarcar `en_cartelera` [services.py](movie_up/peliculas/services.py). El filtro es explícito y no por truthiness: `if value:` descartaba `False` y hacía imposible pasar `en_cartelera` de Sí a No [design.md](openspec/changes/archive/2026-10-31-crud-peliculas/design.md). En un POST de edición, la vista asigna `False` si el checkbox no está presente [views.py](movie_up/peliculas/views.py). Las pruebas cubren los valores `True` y `False` en el servicio, además del POST con el checkbox desmarcado [tests.py](movie_up/peliculas/tests.py). **Contrapartida:** `False` y `0` se tratan como valores intencionales, así que un llamador debe omitir el campo —no enviarlo vacío— para dejarlo sin modificar.

#### CRUD de salas (`crud-salas`, lotes 1–3)
- **Lote 1 — modelo y Service Layer:** `Sala` persiste la distribución como JSON. El service valida y normaliza filas de hasta 100×100 con celdas `P`, `A` y `R`, deriva la capacidad contando `A` y `R`, y guarda dentro del JSON una versión que solo aumenta ante cambios reales de la distribución normalizada. Los guards para funciones activas quedan comentados hasta que exista la app `funciones`, evitando imports a módulos inexistentes [models.py](movie_up/salas/models.py), [services.py](movie_up/salas/services.py), [design.md](openspec/changes/archive/2026-11-01-crud-salas/design.md).
- **Lote 2 — interfaz y administración:** el CRUD web usa vistas y rutas con namespace, templates y registro en Django Admin. El editor JavaScript alterna `P` → `A` → `R` → `P` y permite redimensionar conservando la intersección; el detalle renderiza la misma distribución en modo de solo lectura [urls.py](movie_up/salas/urls.py), [views.py](movie_up/salas/views.py), [admin.py](movie_up/salas/admin.py), [grid.js](movie_up/salas/static/salas/js/grid.js), [salas.css](movie_up/salas/static/salas/css/salas.css), [design.md](openspec/changes/archive/2026-11-01-crud-salas/design.md).
- **Lote 3 — integración:** la verificación cubrió los tests de `peliculas` y `salas`, además del recorrido CRUD de salas en navegador real con Playwright [tasks.md](openspec/changes/archive/2026-11-01-crud-salas/tasks.md).

#### CRUD de funciones (`crud-funciones`)
El Service Layer concentra esta lógica porque la función conserva un snapshot de la distribución de su sala y la validación de solapamientos debe ejecutarse de forma serializada [services.py](movie_up/funciones/services.py), [design.md](openspec/changes/archive/2026-11-01-crud-funciones/design.md).

La suite completa pasó 111/111 tests. En navegador se verificaron Create, Detail con cuadrícula, Update y Delete; el rechazo de solapamientos fue visible y la consola quedó limpia [tasks.md](openspec/changes/archive/2026-11-01-crud-funciones/tasks.md), [.playwright-mcp/](.playwright-mcp/).

- **Flujo de petición:** `urls.py` → `views.py` → `services.py` → `models.py` → `templates/`.

### Estructura del proyecto
Según [AGENTS.md](AGENTS.md), la estructura completa del proyecto es:

```
MovieUp/
├── .dockerignore
├── .env                          # NO versionar
├── .gitignore
├── AGENTS.md
├── docker-compose.yml
├── docker-entrypoint.sh
├── Dockerfile
├── README.md
├── requirements.txt
│
├── .atl/                         # caché del skill-registry
├── .opencode/
│   ├── agent/
│   │   └── readme-maintainer.md
│   ├── commands/
│   │   ├── opsx-apply.md
│   │   ├── opsx-archive.md
│   │   ├── opsx-explore.md
│   │   ├── opsx-propose.md
│   │   ├── opsx-sync.md
│   │   └── opsx-update.md
│   └── skills/                   # 9 skills: crud-conventions, django-app-creator, ui-design y 6 openspec-*
│       ├── crud-conventions/
│       │   └── SKILL.md
│       ├── django-app-creator/
│       │   └── SKILL.md
│       ├── openspec-*/           # 6 skills (explore, propose, apply, archive, sync, update)
│       │   └── SKILL.md
│       └── ui-design/
│           ├── SKILL.md
│           └── references/
│               └── palette.md
├── .playwright-mcp/              # logs de Playwright
├── movie_up/
│   ├── manage.py
│   ├── compras/
│   ├── cuentas/
│   ├── entradas/
│   ├── funciones/
│   ├── peliculas/              # __init__.py, admin.py, apps.py, models.py, views.py, tests.py, migrations/, templates/, urls.py, services.py
│   ├── salas/
│   └── core/
│       ├── __init__.py
│       ├── asgi.py
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
└── openspec/
    ├── config.yaml
    ├── changes/
    │   └── archive/
    │       ├── .gitkeep
    │       ├── 2026-10-31-crud-peliculas/
    │       ├── 2026-11-01-crud-funciones/
    │       ├── 2026-11-01-crud-salas/
    │       ├── 2026-11-02-crud-entradas/
    │       ├── 2026-11-02-login-google/
    │       ├── 2026-11-03-ui-shell/
    │       ├── 2026-11-05-compra-pelicula/
    │       ├── 2026-11-05-ui-crud-pages/
    │       ├── 2026-11-06-compra-asientos/
    │       └── 2026-11-06-estetica-compra-entradas/
    └── specs/
        ├── .gitkeep
        ├── compras/
        ├── cuentas/
        ├── entradas/
        ├── funciones/
        ├── movies/
        ├── salas/
        └── ui/
```

### Configuración y despliegue con Docker
**Fuentes:** [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), [docker-entrypoint.sh](docker-entrypoint.sh), [core/settings.py](movie_up/core/settings.py)

- **Multi-stage build** (builder/runtime): el builder compila dependencias como wheels usando `python:3.14.7-slim-trixie`, el runtime instala únicamente wheels precompilados con usuario no privilegiado (`appuser`) [Dockerfile](Dockerfile)
- **Servicios**: `db` (MySQL 9.7.2) y `web` (Django app) [docker-compose.yml](docker-compose.yml)
- **Variables de entorno**: inyectadas via `.env` y `env_file`; `DB_HOST=db`, `DB_PORT` se sobreescriben para el contenedor web [docker-compose.yml](docker-compose.yml)
- **Punto de entrada**: `docker-entrypoint.sh` espera a que la base de datos responda vía TCP, luego ejecuta `python movie_up/manage.py migrate --noinput` automáticamente [docker-entrypoint.sh](docker-entrypoint.sh), [AGENTS.md](AGENTS.md)
- **Healthcheck:** ejecuta `curl -fsS http://localhost:8000/` cada 30 s. La raíz no tiene una ruta configurada y responde 404, por lo que este healthcheck falla [Dockerfile](Dockerfile), [urls.py](movie_up/core/urls.py).

**Cómo ejecutar (según AGENTS.md):**
- Levantar todo: `docker compose up --build` [AGENTS.md](AGENTS.md)
- Migraciones: se aplican automáticamente al arrancar (docker-entrypoint.sh) [AGENTS.md](AGENTS.md)
- Migraciones manuales: `docker compose exec web python movie_up/manage.py migrate` [AGENTS.md](AGENTS.md)
- Crear superusuario: `docker compose exec web python movie_up/manage.py createsuperuser` [AGENTS.md](AGENTS.md)
- Correr tests: `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas compras` — cada app nueva se suma a la lista, porque el discovery sin etiquetas no descubre nada [AGENTS.md](AGENTS.md)
- **Gotcha de discovery:** ejecutar `test` sin etiquetas termina con código 0, pero descubre cero tests porque el contenedor inicia en `/app` y `movie_up/` no es un paquete Python; indicar las apps evita ese falso positivo [AGENTS.md](AGENTS.md).
- App: http://localhost:8000/ (usar `localhost`, NO `0.0.0.0`) [AGENTS.md](AGENTS.md)
- **Estado verificado (smoke test vía Docker + Playwright):** `http://localhost:8000/` responde 404 porque no hay una ruta raíz configurada; no se debe atribuir a que `movie_up` falte de `INSTALLED_APPS`. `/admin/login/` renderiza correctamente [urls.py](movie_up/core/urls.py), [settings.py](movie_up/core/settings.py).
- **Gotcha crítica resuelta (2026-10-30):** La estructura del proyecto coloca `manage.py` en `movie_up/manage.py` (no en la raíz), lo cual es atípico en Django. Un bug inicial en [Dockerfile](Dockerfile) y [docker-entrypoint.sh](docker-entrypoint.sh) usaba rutas incorrectas (`manage.py` en vez de `movie_up/manage.py`), causando que el contenedor web no iniciara y las migraciones automáticas no se ejecutaran (bug silencioso). Todos los comandos `docker compose exec` y el entrypoint fueron actualizados consistentemente para usar la ruta correcta. **Lección:** En proyectos Django con estructura no estándar, verificar siempre la ruta relativa de `manage.py` en Dockerfile, entrypoint y documentación.

### Configuración Django
- **DEBUG/SECRET_KEY** desde variables de entorno [settings.py](movie_up/core/settings.py)
- **ALLOWED_HOSTS** incluye `localhost`, `0.0.0.0`, `127.0.0.1` [settings.py](movie_up/core/settings.py)
- **Base de datos MySQL** configurada con credenciales desde `.env` [settings.py](movie_up/core/settings.py)
- **Apps instaladas:** `django.contrib.*`, luego las apps de `django-allauth` (`allauth`, `allauth.account`, `allauth.socialaccount`, `allauth.socialaccount.providers.google`) y al final las apps del proyecto `compras`, `cuentas`, `entradas`, `funciones`, `peliculas`, `salas` en orden alfabético — la regla vigente es que las apps del proyecto cierran la lista [settings.py](movie_up/core/settings.py)
- **Zona horaria:** `America/Argentina/Buenos_Aires`; `USE_TZ` habilitado [settings.py](movie_up/core/settings.py)
- **MEDIA_ROOT** configurado como `BASE_DIR / 'imgs'` para almacenamiento de imágenes subidas [settings.py](movie_up/core/settings.py)
- **MEDIA_URL** configurado como `/imgs/` para acceso a archivos multimedia [settings.py](movie_up/core/settings.py)
- **EMAIL_BACKEND:** `console.EmailBackend` (configuración para desarrollo) [settings.py](movie_up/core/settings.py)

### Configuración de ImageField en Django containerizado
Para soportar subida de imágenes (imagen de portada de películas), se configuró Django con `ImageField`:

- **Dependencia:** `Pillow==11.0.0` agregado a `requirements.txt` para procesamiento de imágenes [requirements.txt](requirements.txt)
- **Docker:** El `Dockerfile` instala `libjpeg-dev` y `zlib1g-dev` (dependencias del sistema requeridas por Pillow para compilar) [Dockerfile](Dockerfile)
- **Storage:** `ImageField` guarda archivos en `MEDIA_ROOT/imgs/` y almacena solo la ruta relativa en la base de datos
- **Git:** `/imgs/` agregado a `.gitignore` para no versionar archivos subidos por usuarios [.gitignore](.gitignore)

**Lección:** En proyectos Django containerizados, `ImageField` requiere (1) Pillow en requirements, (2) dependencias del sistema en Dockerfile (`libjpeg-dev`, `zlib1g-dev`), (3) configuración de `MEDIA_ROOT`/`MEDIA_URL`. Sin estas librerías, Pillow falla al compilar durante `docker compose build`.

### Convenciones
- Artefactos (código, identificadores, UI, comentarios): inglés [AGENTS.md](AGENTS.md)
- Documentación (AGENTS.md, OpenSpec, skills, agents): español; en los artefactos OpenSpec el texto va en español y las palabras clave de formato quedan en inglés [AGENTS.md](AGENTS.md)
- Tests: en `<app>/tests.py`, ejecutados con `python movie_up/manage.py test` [AGENTS.md](AGENTS.md)

#### Reglas de Git (obligatorio)
Según [AGENTS.md](AGENTS.md):
- **PROHIBIDO** hacer `git add`, `git commit`, `git push` o cualquier operación de staging/commit sin consultar primero al usuario
- El agente SIEMPRE debe mostrar los cambios pendientes y esperar confirmación explícita antes de ejecutar cualquier operación de Git
- Commits: conventional commits, sin atribución a IA

### Autenticación y roles
- Roles: Cliente y Administrador/Empleado [AGENTS.md](AGENTS.md).
- El modelo de usuario es `cuentas.Cuenta` (`AUTH_USER_MODEL`), basado en `AbstractUser`, con `correo` único y `nombre`; no conserva `username`, `email`, `first_name` ni `last_name` [models.py](movie_up/cuentas/models.py), [settings.py](movie_up/core/settings.py).
- Las cuentas sociales ingresan solo con Google. El alta requiere que Google marque el correo como verificado. El nombre se obtiene del perfil, con respaldo en los nombres parciales y luego en la parte local del correo; los logins siguientes no reescriben los datos del perfil [adapters.py](movie_up/cuentas/adapters.py), [spec.md](openspec/changes/archive/2026-11-02-login-google/specs/cuentas/spec.md).
- La primera cuenta nueva se promueve a administradora completa; las posteriores quedan como cuentas comunes. La señal `user_signed_up` llama al servicio que serializa la promoción con `GET_LOCK`/`RELEASE_LOCK` de MySQL [signals.py](movie_up/cuentas/signals.py), [services.py](movie_up/cuentas/services.py).
- En Django Admin, `correo` y `nombre` son de solo lectura, no se permiten altas manuales y el indicador de administración sincroniza `is_staff` con `is_superuser`. Los guards de borrado individual y masivo están activos: bloquean la eliminación de cuentas con entradas asociadas. [admin.py](movie_up/cuentas/admin.py), [tasks.md](openspec/changes/archive/2026-11-02-crud-entradas/tasks.md)
- `createsuperuser` queda como acceso local de recuperación para una cuenta administrativa de emergencia [AGENTS.md](AGENTS.md).

#### Integración con django-allauth y Google
- `SOCIALACCOUNT_ONLY` restringe el acceso social a Google; la configuración usa los campos de correo del modelo `Cuenta`, el middleware de allauth y los backends de autenticación de Django y allauth [settings.py](movie_up/core/settings.py).
- Google es el único proveedor habilitado, con scopes `profile` y `email`, `access_type: online` y PKCE. `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` se leen del entorno y no se incluyen aquí [settings.py](movie_up/core/settings.py).
- Las rutas de allauth están montadas bajo `/accounts/` [urls.py](movie_up/core/urls.py).

#### Migración de `AUTH_USER_MODEL` y preservación de datos
Se aplicó el cambio de modelo de usuario sin resetear el volumen. Tras inspeccionar el historial de migraciones y el esquema existentes, se reparó el historial de migraciones de `admin` de forma controlada [design.md](openspec/changes/archive/2026-11-02-login-google/design.md), [tasks.md](openspec/changes/archive/2026-11-02-login-google/tasks.md). La migración `0002` convierte `django_admin_log.user_id` de `INT` a `BIGINT` y redirige su clave foránea de `auth_user(id)` a `cuenta(id)`; usa `atomic = False` para el DDL de MySQL [0002_retarget_admin_log_user_fk.py](movie_up/cuentas/migrations/0002_retarget_admin_log_user_fk.py), [design.md](openspec/changes/archive/2026-11-02-login-google/design.md). Se preservaron 4 películas, 3 salas y 2 funciones [design.md](openspec/changes/archive/2026-11-02-login-google/design.md).

#### Verificación local y límite de la prueba
Pasaron los 20 tests de `cuentas` y los 131 tests de la suite completa. `manage.py check` terminó sin errores y con dos warnings W036; `makemigrations --check --dry-run` no encontró cambios y el plan de migraciones quedó vacío [tasks.md](openspec/changes/archive/2026-11-02-login-google/tasks.md), [tests.py](movie_up/cuentas/tests.py).

Con Playwright se verificó que `/accounts/login/` ofrece solo Google, que `/accounts/signup/` responde 404 y que `/admin/` redirige al login de administración para visitantes anónimos. No se observaron errores JavaScript; el 404 del signup y el del favicon fueron esperados [tasks.md](openspec/changes/archive/2026-11-02-login-google/tasks.md).

La prueba automatizada del callback simula el intercambio OAuth; **no verifica el login real con Google ni permite afirmar que OAuth funciona end-to-end** [tests.py](movie_up/cuentas/tests.py), [tasks.md](openspec/changes/archive/2026-11-02-login-google/tasks.md).

La prueba manual con Google, ejecutada por el usuario según el checklist de `Workflow follow-up`, quedó registrada como tarea 6.4 completada antes de archivar el change; es la única evidencia de la integración end-to-end con Google real [tasks.md](openspec/changes/archive/2026-11-02-login-google/tasks.md).

**Verificación local:** la suite completa reportó 169 tests y terminó en `OK`; `manage.py check` terminó con los 2 warnings `W036` conocidos; `makemigrations --check --dry-run` no encontró cambios. [tasks.md](openspec/changes/archive/2026-11-02-crud-entradas/tasks.md), [tests.py](movie_up/entradas/tests.py)

**Playwright:** se comprobaron el listado, el detalle y la vista de validación con un fixture temporal, luego eliminado. Hubo un 404 de `favicon.ico` solicitado por el admin; no se describe la consola como limpia. [tasks.md](openspec/changes/archive/2026-11-02-crud-entradas/tasks.md), [views.py](movie_up/entradas/views.py)

### Desarrollo dirigido por especificaciones (OpenSpec)
**Fuentes:** [AGENTS.md](AGENTS.md), [openspec/](openspec/), [openspec/config.yaml](openspec/config.yaml), [opsx-propose.md](.opencode/commands/opsx-propose.md)

- El proyecto usa **OpenSpec** para desarrollo dirigido por especificaciones (spec-driven development) [AGENTS.md](AGENTS.md)
- Especificaciones de verdad en `openspec/specs/` (organizadas por dominio) y cambios propuestos en `openspec/changes/` [AGENTS.md](AGENTS.md)
- Cada cambio incluye `proposal.md` (por qué), `specs/` (qué cambia), `design.md` (cómo) y `tasks.md` (pasos) [AGENTS.md](AGENTS.md)
- Flujo de trabajo: `/opsx:explore` → `/opsx:propose` → `/opsx:apply` → `/opsx:archive` [AGENTS.md](AGENTS.md)
- Comandos adicionales: `/opsx:sync` (sincronizar specs), `/opsx:update` (revisar el plan) [AGENTS.md](AGENTS.md)
- Definir specs antes de implementar cualquier nueva funcionalidad [AGENTS.md](AGENTS.md)
- Estado actual: los cinco changes implementados y archivados son `crud-peliculas` (CRUD completo de películas con Service Layer), en `openspec/changes/archive/2026-10-31-crud-peliculas/`; `crud-salas` (CRUD de salas con editor de distribución en grilla), en `openspec/changes/archive/2026-11-01-crud-salas/`; `crud-funciones` (CRUD de funciones con snapshot de la distribución de la sala y bloqueo de solapamientos serializado), en `openspec/changes/archive/2026-11-01-crud-funciones/`; `crud-entradas` (entradas de cine: creación interna por compra, listado y detalle propios, validación por código y reembolso con límite de 24 horas), en `openspec/changes/archive/2026-11-02-crud-entradas/`; y `login-google` (identidad y login únicamente con Google vía django-allauth, modelo `Cuenta` y regla del primer administrador), en `openspec/changes/archive/2026-11-02-login-google/`, los cinco con todos sus artefactos (proposal, specs, design, tasks) [proposal.md](openspec/changes/archive/2026-10-31-crud-peliculas/proposal.md), [proposal.md](openspec/changes/archive/2026-11-01-crud-salas/proposal.md), [proposal.md](openspec/changes/archive/2026-11-01-crud-funciones/proposal.md), [proposal.md](openspec/changes/archive/2026-11-02-crud-entradas/proposal.md), [proposal.md](openspec/changes/archive/2026-11-02-login-google/proposal.md). Los archives escribieron las specs de verdad del proyecto: `openspec/specs/movies/spec.md` con 5 requisitos (listar, detalle, crear, actualizar, eliminar) y 12 escenarios [spec.md](openspec/specs/movies/spec.md), `openspec/specs/salas/spec.md` con 12 requisitos y 35 escenarios [spec.md](openspec/specs/salas/spec.md), `openspec/specs/funciones/spec.md` con 16 requisitos y 28 escenarios [spec.md](openspec/specs/funciones/spec.md), `openspec/specs/entradas/spec.md` con 17 requisitos y 41 escenarios [spec.md](openspec/specs/entradas/spec.md), y `openspec/specs/cuentas/spec.md` con 10 requisitos y 23 escenarios [spec.md](openspec/specs/cuentas/spec.md). `openspec validate --specs --strict` pasa con las 5 specs (exit 0) y `openspec list` no reporta cambios activos.

`crud-entradas` fue archivado el 2026-11-02 en `openspec/changes/archive/2026-11-02-crud-entradas/` con su `.openspec.yaml` preservado y 29/29 tareas completadas; la sincronización de specs escribió `openspec/specs/entradas/spec.md` y actualizó en `openspec/specs/cuentas/spec.md` el requisito "Borrado bloqueado por entradas asociadas", que dejó de condicionar el guard a un `TODO` [tasks.md](openspec/changes/archive/2026-11-02-crud-entradas/tasks.md), [proposal.md](openspec/changes/archive/2026-11-02-crud-entradas/proposal.md), [spec.md](openspec/specs/entradas/spec.md), [spec.md](openspec/specs/cuentas/spec.md).


#### Parseo y validación de specs (gotcha)

OpenSpec parsea los artefactos con tokens estructurales fijos en inglés. Traducirlos produce un archivo que se lee bien pero que el CLI no puede interpretar [AGENTS.md](AGENTS.md).

- **Tokens intocables:** `## Purpose` y `## Requirements` en la spec principal, `## ADDED Requirements` en el delta, requisitos `### Requirement: <nombre>`, escenarios `#### Scenario: <nombre>` con exactamente 4 `#`, pasos `**WHEN**` / `**THEN**` [spec.md](openspec/specs/movies/spec.md), [spec delta](openspec/changes/archive/2026-10-31-crud-peliculas/specs/movies/spec.md).
- **Fallo silencioso:** sin `## ADDED Requirements`, `openspec validate` reporta `No delta sections found` / `Change must have at least one delta`, y el archive completa sin escribir nada en `openspec/specs/`. Marcar todas las tareas no protege de esto: un change con 19 de 19 tareas completas puede archivar sin producir la spec [AGENTS.md](AGENTS.md), [tasks.md](openspec/changes/archive/2026-10-31-crud-peliculas/tasks.md).
- **RFC 2119 literal:** `--strict` busca las palabras `SHALL` / `MUST`; `DEBE` / `DEBEN` falla la validación. Convención adoptada: prosa en español con las keywords normativas en inglés [AGENTS.md](AGENTS.md).
- **Mapeo normativo del proyecto:** `SHALL` describe la capacidad que el sistema provee; `MUST` marca obligaciones y condiciones de error (404 en identificadores inexistentes, rechazo de título duplicado, reemplazo de la imagen anterior, bloqueo del borrado con funciones asociadas) [spec.md](openspec/specs/movies/spec.md).
- **Puerta de verificación:** `openspec validate --specs --strict` con exit 0 y cero warnings es obligatorio antes de archivar; es la única señal de que la spec va a llegar efectivamente a la fuente de verdad [AGENTS.md](AGENTS.md).
- **Separación spec / design:** la spec describe solo comportamiento observable; las restricciones de implementación (tipos de campo derivados del DDL, `ImageField`, delegación a `services.py`, templates HTML puro sin CSS/JS, bloque comentado de `funciones`) permanecen en el design del change [design.md](openspec/changes/archive/2026-10-31-crud-peliculas/design.md).


## 2. Casos de uso (10 canónicos)

**Fuente:** [AGENTS.md](AGENTS.md) - Mirror exacto de AGENTS.md. No se agregan, eliminan ni reformulan casos de uso.

### Cliente (4 casos de uso)
1. Comprar entradas (selección de asientos + pago con Mercado Pago) [AGENTS.md](AGENTS.md)
2. Consultar y gestionar entradas desde la cuenta [AGENTS.md](AGENTS.md)
3. Reembolsar entradas [AGENTS.md](AGENTS.md)
4. Vincular cuenta de Google [AGENTS.md](AGENTS.md)

### Administrador/Empleado (6 casos de uso)
5. Gestionar películas (CRUD) [AGENTS.md](AGENTS.md)
6. Gestionar funciones (CRUD) [AGENTS.md](AGENTS.md)
7. Gestionar salas (CRUD) [AGENTS.md](AGENTS.md)
8. Gestionar ventas (CRUD) [AGENTS.md](AGENTS.md)
9. Consultar métricas de ventas [AGENTS.md](AGENTS.md)
10. Validar entradas mediante código [AGENTS.md](AGENTS.md)


## 3. Justificación de Ingeniería con IA

**Fuente:** [AGENTS.md](AGENTS.md), [readme-maintainer.md](.opencode/agent/readme-maintainer.md), [opencode.json](C:/Users/anlle/.config/opencode/opencode.json), [.opencode/agent/](.opencode/agent/), [.opencode/skills/](.opencode/skills/), [.opencode/commands/](.opencode/commands/)

### 3.1 Estructura de instrucciones del sistema
La directiva de IA está organizada de forma modular con las siguientes capas:

- **AGENTS.md (raíz)**: Define el contexto del proyecto, stack, arquitectura, convenciones, casos de uso, flujo de trabajo OpenSpec, y agentes definidos. Actúa como fuente de verdad para el proyecto [AGENTS.md](AGENTS.md).
- **Agentes subagentes (.opencode/agent/)**: Definen comportamientos especializados. Específicamente `readme-maintainer.md` define un agente con permisos restrictivos (solo puede editar `README.md`, otros permisos requieren confirmación), un protocolo estricto de edición con puerta de confirmación `ok`, y la convención de cita obligatoria del registro: `[FILENAME](PATH)`, sin números de línea en el texto del enlace, sin anclas `#L...` en la URL y sin citar dos veces el mismo archivo en una misma línea [readme-maintainer.md](.opencode/agent/readme-maintainer.md).
- **Skills (.opencode/skills/)**: Capacidades reutilizables activables por disparadores. Los skills `openspec-*` implementan los flujos de OpenSpec (explorar, proponer, aplicar, archivar, sincronizar, actualizar el plan) [.opencode/skills/](.opencode/skills/). Skills específicas del proyecto:
  - **`django-app-creator`** — Trigger: `crea app [nombre]`. Automatiza la creación de apps Django con estructura completa: ejecuta `python manage.py startapp <nombre>` desde `movie_up/`, registra la app en `INSTALLED_APPS` de [settings.py](movie_up/core/settings.py), crea estructura de templates con namespacing doble (`templates/<nombre>/`) para evitar colisiones, crea `urls.py` con imports base, crea `services.py` para institucionalizar el Service Layer como convención oficial (toda app nueva nace con lógica de negocio separada de las vistas, consistente con AGENTS.md), y mantiene la documentación del proyecto actualizada (`.opencode/skills/django-app-creator/SKILL.md`). **Convenciones de mantenimiento documental:** tras crear la app, actualiza las secciones `## Estructura del Proyecto` en `AGENTS.md` y `README.md` con orden `manage.py` → apps (alfabético) → `core/`. Si es la primera app (distinta de `core/`): incluye comentario horizontal detallando todos los archivos (`__init__.py`, `admin.py`, `apps.py`, `models.py`, `views.py`, `tests.py`, `migrations/`, `templates/`, `urls.py`, `services.py`). Si ya existen otras apps: agrega solo el nombre de la carpeta sin comentario. Registrada en [AGENTS.md](AGENTS.md) bajo `## Skills`.
  - **`crud-conventions`** — Trigger: `planificar spec CRUD`, `planificar la spec de un CRUD`, `nueva spec CRUD`, `empezar CRUD`. Institucionaliza como skill las convenciones genéricas aprendidas de los dos CRUDs ya construidos (`peliculas`, `salas`) para aplicarlas a la spec de cualquier CRUD futuro, sin incluir detalles propios de esas apps: Service Layer con vistas delgadas, revalidación siempre en el servidor, contrato de errores `ValueError` → formulario / `Http404` → 404 sin capturas amplias, update parcial (campo ausente = no modificar; `False`/`0` explícitos sí aplican), unicidad y datos derivados en el servicio, guards de apps inexistentes como bloques comentados con TODO y tests por operación. Su Activation Contract la acota a la fase de planificación: se carga al redactar proposal y specs de un CRUD nuevo, no al implementar uno ya especificado (ahí manda su spec). Incluye Decision Gates, Execution Steps que cierran con `openspec validate --specs --strict`, Output Contract y como referencias los `services.py` de `peliculas` y `salas` más `django-app-creator`. Complementa a `django-app-creator` sin superponerse: él genera el esqueleto de la app, esta gobierna el contenido de la spec [crud-conventions SKILL.md](.opencode/skills/crud-conventions/SKILL.md), [AGENTS.md](AGENTS.md).
  - **`ui-design`** — Trigger: `cambiar colores, CSS, estilos, interfaz, paleta, botón, centrar, tipografía, hover, tema` (toda tarea visual de la página). Pilar de diseño visual de MovieUp: en sus Hard Rules fija la paleta cerrada de 12 tokens (cada uno con su par de texto y contraste AA mínimo), la proporción 60% crema / 25% ink / 10% rojo / 5% dorado, hover por opacidad del mismo token (nunca un color nuevo), sombras suaves con ring de 1px en el borde, un máximo de dos familias tipográficas (Playfair Display en títulos, Inter en texto), reglas de botón (min-height 40px, max-height 56px, padding-x 16–32px, texto 14–18px; CTA principal max-width 320px en desktop y full-width solo en móvil) y de centrado (solo hero, encabezados de página, estados vacíos y confirmaciones; listados, tarjetas, formularios, tablas y textos largos a la izquierda). Su protocolo de desviación obliga a una pregunta sí/no bloqueante antes de aplicar un color fuera de la paleta. Incluye Activation Contract (cargar ante cualquier elemento visual, no ante cambios sin componente visual), Decision Gates, Execution Steps que cierran con verificación en navegador real vía Playwright, Output Contract y como referencia la spec completa de color en [palette.md](.opencode/skills/ui-design/references/palette.md) [ui-design SKILL.md](.opencode/skills/ui-design/SKILL.md), [AGENTS.md](AGENTS.md).
- **Comandos (.opencode/commands/)**: Comandos slash para flujos OpenSpec (`/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:archive`, `/opsx:sync`, `/opsx:update`) que implementan workflows con restricciones de planificación vs implementación [opsx-propose.md](.opencode/commands/opsx-propose.md).
- **Config global (opencode.json)**: Define agentes del sistema, MCPs habilitados y permisos por agente [opencode.json](C:/Users/anlle/.config/opencode/opencode.json).

### 3.2 Prompts clave
[PENDIENTE: No se han registrado prompts específicos ejecutados para construir el sistema en fuentes disponibles (AGENTS.md, .opencode, código). No se inventará contenido.]

### 3.3 Metodología de iteración
- **Desarrollo dirigido por especificaciones (Spec-Driven Development)**: Uso obligatorio de OpenSpec. Las specs (`openspec/specs/`) son fuente de verdad; los cambios pasan por artefactos estructurados (proposal, specs, design, tasks) antes de implementar [AGENTS.md](AGENTS.md).
- **Iteración del change `login-google`:** OpenSpec organizó el trabajo en lotes secuenciales: modelo, configuración y migración; alta social, mapeo del perfil y bootstrap; luego administración, guard y cierre. La prueba manual con Google quedó como puerta final y no se reemplazó por el callback automatizado simulado [tasks.md](openspec/changes/archive/2026-11-02-login-google/tasks.md), [design.md](openspec/changes/archive/2026-11-02-login-google/design.md).
- **Mantenimiento controlado de README**: El agente `readme-maintainer` se activa automáticamente tras cada creación o modificación de archivos, evalúa si el cambio aporta al registro de ingeniería, y si es relevante presenta todos los cambios propuestos de una sola vez (sección, texto, tipo: fusionar/reemplazar/agregar) esperando `ok` antes de editar [AGENTS.md](AGENTS.md), [readme-maintainer.md](.opencode/agent/readme-maintainer.md).
- **Verificación de UI en navegador real (directiva AGENTS.md)**: Antes de dar por hecha una vista, verificarla en navegador real vía Playwright MCP (levantar con `docker compose up --build` y navegar `http://localhost:8000/`). La referencia de configuración de MCPs vive en README.md sección 4 [AGENTS.md](AGENTS.md).
- **Arquitectura containerizada desde el inicio**: Setup Docker con multi-stage build, healthcheck, entrypoint con espera de DB y migraciones automáticas [Dockerfile](Dockerfile), [docker-entrypoint.sh](docker-entrypoint.sh), [AGENTS.md](AGENTS.md).
- **Institucionalización de decisiones arquitectónicas vía skills**: las decisiones arquitectónicas no quedan solo como directiva textual; se formalizan en skills ejecutables. Ejemplo: la adopción de **Service Layer** como patrón oficial (lógica de negocio en `services.py`, vistas delgadas `request → service → response`) se documentó en [AGENTS.md](AGENTS.md) y se hizo cumplir automáticamente mediante el skill `django-app-creator`, que genera `services.py` en cada app nueva [AGENTS.md](AGENTS.md), [django-app-creator SKILL.md](.opencode/skills/django-app-creator/SKILL.md). Así, la convención no depende de que el agente "se acuerde": el skill la garantiza estructuralmente. Segundo ejemplo, de naturaleza distinta: `crud-conventions` no genera código sino que institucionaliza **convenciones de diseño de specs**, capturando en Decision Gates y Hard Rules lo aprendido en `peliculas` y `salas` para que los próximos CRUDs del catálogo (funciones, ventas) no tengan que rederivar esas convenciones desde cero en cada planificación [crud-conventions SKILL.md](.opencode/skills/crud-conventions/SKILL.md).
Tercer ejemplo, de naturaleza visual: `ui-design` institucionaliza **decisiones de diseño de interfaz** —paleta cerrada de 12 tokens con sus pares de texto, proporciones, tipografía de dos familias y reglas de botón y centrado— en Hard Rules y Decision Gates, de modo que toda tarea visual respete el sistema sin depender de la memoria de la sesión, y su protocolo de desviación fuerza una pregunta sí/no antes de aplicar un color fuera de la paleta [ui-design SKILL.md](.opencode/skills/ui-design/SKILL.md).

### 3.4 Bucles de autocorrección automatizados
[PENDIENTE: No se identifican bucles de autocorrección automatizados explícitos (loops de auto-corrección con ejecución iterativa) documentados en las fuentes consultadas (AGENTS.md, skills, commands, agent configs). Solo se identifican mecanismos de control/validación (puerta de confirmación para README, workflow OpenSpec estructurado).]

**Mecanismo de corrección observado:** el único ciclo de corrección registrado no es automático, sino de validación por herramienta. Un change con las 19 tareas marcadas como completas en `tasks.md` puede tener un spec no parseable, y en ese caso es `openspec validate` —no la revisión del contenido— el que detecta el problema y fuerza la reescritura del artefacto con los tokens estructurales en inglés. El detalle técnico está en la sección 1 [tasks.md](openspec/changes/archive/2026-10-31-crud-peliculas/tasks.md), [AGENTS.md](AGENTS.md).

### 3.5 Estructura de instrucciones (resumen)
La estructura sigue un enfoque jerárquico y restrictivo: instrucciones a nivel proyecto (AGENTS.md), políticas de agentes (agent/*.md con permisos), habilidades especializadas (skills con triggers), comandos operativos (commands con workflows), y configuración de runtime (opencode.json con MCPs y permisos). Esto permite dirigir la construcción con IA de forma controlada, trazable y con puntos de confirmación explícitos. [Fuentes: AGENTS.md, .opencode/*, opencode.json]


## 4. Configuración de servidores MCP

**Fuente:** [readme-maintainer.md](.opencode/agent/readme-maintainer.md), [opencode.json](C:/Users/anlle/.config/opencode/opencode.json)

Según las especificaciones del agente `readme-maintainer` y la configuración real en OpenCode:

### 4.1 context7
- **Tipo:** remoto [opencode.json](C:/Users/anlle/.config/opencode/opencode.json)
- **URL:** `https://mcp.context7.com/mcp` [opencode.json](C:/Users/anlle/.config/opencode/opencode.json), [readme-maintainer.md](.opencode/agent/readme-maintainer.md)
- **Propósito:** Servidor MCP remoto para acceder a documentación actualizada de bibliotecas/frameworks/SDKs/APIs/CLIs/servicios cloud (Context7). Habilitado en la configuración global de OpenCode [opencode.json](C:/Users/anlle/.config/opencode/opencode.json).
- **Rol en desarrollo:** Facilita consulta de documentación actualizada durante el desarrollo (instrucciones de setup, sintaxis API, migraciones, debugging específico de librerías) [contexto de opencode.json/mcp].

### 4.2 engram
- **Tipo:** local [opencode.json](C:/Users/anlle/.config/opencode/opencode.json)
- **Comando:** `C:\Users\anlle\AppData\Local\engram\bin\engram.exe mcp --tools=agent` [opencode.json](C:/Users/anlle/.config/opencode/opencode.json), [readme-maintainer.md](.opencode/agent/readme-maintainer.md)
- **Propósito:** Servidor MCP local para memoria persistente (Engram). Habilitado con tools=agent [opencode.json](C:/Users/anlle/.config/opencode/opencode.json).
- **Rol en desarrollo:** Proporciona memoria persistente entre sesiones para guardar decisiones, descubrimientos, bugs, convenciones y contexto del proyecto [según instrucciones de Engram en el sistema]. 

### 4.3 playwright
- **Tipo:** local [opencode.json](C:/Users/anlle/.config/opencode/opencode.json)
- **Comando:** `npx -y @playwright/mcp@latest --browser msedge` (timeout 60000) [opencode.json](C:/Users/anlle/.config/opencode/opencode.json)
- **Propósito:** Servidor MCP local de Microsoft (`@playwright/mcp`) para que el agente verifique los flujos de UI de MovieUp en un navegador real (selección de asientos, checkout, vistas de administrador).
- **Rol en desarrollo:** Validación automatizada de la interfaz contra el stack Docker real, complementando la verificación por código/tests con evidencia visual y funcional en navegador. Además ejecuta la directiva de AGENTS.md: antes de dar por hecha una vista, verificarla en navegador real vía Playwright MCP (levantar con `docker compose up --build` y navegar `http://localhost:8000/`); la referencia de configuración de MCPs vive en README.md sección 4 [AGENTS.md](AGENTS.md).
- **Decisiones no obvias:**
  - Se usa `--browser msedge` porque la máquina de desarrollo no tiene Chrome instalado, solo Edge.
  - Se mantuvo deliberadamente la forma plana V1 del bloque `mcp` tras revisar la guía de migración de OpenCode: migrar a la forma V2 no era necesario y la forma V1 evita riesgos de rotura de configuración.
  - Se creó backup previo en `opencode.json.bak`.

**Nota de configuración:** No se copian valores secretos. Solo se describe forma/configuración y rol, tal como se indica en [readme-maintainer.md](.opencode/agent/readme-maintainer.md). 


## 5. Pending inputs
[PENDIENTE: No existen fuentes para determinar prompts específicos clave ejecutados durante la construcción del sistema, ni bucles de autocorrección automatizados explícitos con detalles de implementación. Estos elementos requerirían logs de ejecución/iteración con IA que no están presentes en AGENTS.md, .opencode, código o configuración MCP.]

[PENDIENTE: Registro de la verificación en navegador del flujo CRUD de películas vía Playwright MCP. AGENTS.md la exige antes de dar por hecha una vista, pero los artefactos disponibles en [.playwright-mcp/](.playwright-mcp/) son del 18/10/2026 (anteriores al change, creado el 30/10 según `.openspec.yaml`) y no incluyen ninguna navegación a `/peliculas/`.]
