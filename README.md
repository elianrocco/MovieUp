# MovieUp - Log de Ingeniería

## 1. Visión general y arquitectura del sistema

**Fuente:** [AGENTS.md](AGENTS.md), [core/settings.py](movie_up/core/settings.py), [core/urls.py](movie_up/core/urls.py), [movie_up/](movie_up/), [requirements.txt](requirements.txt), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)

### Propósito del proyecto
MovieUp es un sistema web de cine para consultar la cartelera, comprar entradas mediante selección de asientos, consultar las entradas propias y solicitar reembolsos [spec.md](openspec/specs/compras/spec.md), [spec.md](openspec/specs/entradas/spec.md).

El personal gestiona películas, salas y funciones, administra cuentas y permisos, valida entradas y consulta métricas [spec.md](openspec/specs/movies/spec.md), [spec.md](openspec/specs/salas/spec.md), [spec.md](openspec/specs/funciones/spec.md), [spec.md](openspec/specs/cuentas/spec.md), [spec.md](openspec/specs/estadisticas/spec.md). El sitio también ofrece un chatbot de ayuda [spec.md](openspec/specs/chatbot/spec.md).

La compra actual confirma las entradas sin procesar un cobro: el paso de pago no está integrado [spec.md](openspec/specs/compras/spec.md).

### Stack tecnológico
- **Backend:** Python 3.14.7 con Django 6.1.1 y LangChain 1.4.0 [AGENTS.md](AGENTS.md), [requirements.txt](requirements.txt), [Dockerfile](Dockerfile)
- **Frontend:** HTML (Living Standard), CSS3 (Snapshot 2023) y JavaScript (ES2025) [AGENTS.md](AGENTS.md)
- **Base de datos:** MySQL 9.7.2 LTS [AGENTS.md](AGENTS.md), [docker-compose.yml](docker-compose.yml), [core/settings.py](movie_up/core/settings.py)
- **SDK de pagos:** `mercadopago==3.5.0` está instalado, pero el checkout no lo invoca ni realiza cobros; la compra avanza sin un paso de pago [requirements.txt](requirements.txt), [spec.md](openspec/specs/compras/spec.md), [services.py](movie_up/compras/services.py)
- **Control de versiones:** Git + GitHub [AGENTS.md](AGENTS.md)
- **Containerización:** Docker 29.8.0 [AGENTS.md](AGENTS.md), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)
- **Versiones exactas:** definidas en `requirements.txt`, `Dockerfile` y `docker-compose.yml` [AGENTS.md](AGENTS.md)

### Arquitectura (Patrón MVT de Django)
El proyecto sigue el patrón **Modelo-Vista-Template (MVT)** de Django como arquitectura base, extendido con **Service Layer** [AGENTS.md](AGENTS.md).

- **Modelo (Model):** Define la estructura de datos y la persistencia en MySQL mediante `models.py`. La app `peliculas` contiene el modelo `Pelicula` con 9 campos (título, género, duración, descripción, clasificación, fecha de estreno, URL del tráiler, imagen de portada, en cartelera) [models.py](movie_up/peliculas/models.py).
- **Vista (View):** Lógica HTTP delgada en `views.py` (request → service → response), enrutada desde `urls.py`. La app `peliculas` implementa 5 vistas funcionales: list, detail, create, update y delete [views.py](movie_up/peliculas/views.py).
- **Template:** Presentación mediante el motor de plantillas de Django con HTML/CSS/JS.
- **Service Layer:** Lógica de negocio concentrada en `services.py`; las vistas delegan en él y quedan delgadas (request → service → response). La convención aplica a toda app de dominio, que se crea con su `services.py` para mantener consistencia entre apps. `core` es la excepción: es la app de configuración del proyecto y concentra su lógica compartida en sus propios módulos, sin `services.py` [AGENTS.md](AGENTS.md), [decorators.py](movie_up/core/decorators.py).

### Estructura del proyecto
Según [AGENTS.md](AGENTS.md), la estructura completa del proyecto es:

```
MovieUp/
├── .dockerignore
├── .env                          # NO versionar
├── .env_ejemplo                  # Plantilla versionada de variables
├── .gitignore
├── AGENTS.md
├── chat.py                      # CLI del chatbot
├── docker-compose.yml
├── docker-entrypoint.sh
├── Dockerfile
├── ingest.py                    # Ingesta de la base de conocimiento
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
│   ├── chatbot/
│   ├── compras/
│   ├── cuentas/
│   ├── entradas/
│   ├── estadisticas/
│   ├── funciones/
│   ├── peliculas/              # __init__.py, admin.py, apps.py, models.py, views.py, tests.py, migrations/, templates/, urls.py, services.py
│   ├── salas/
│   ├── static/                 # CSS, JS e imágenes compartidas
│   ├── templates/              # base.html, home.html, gestion.html e includes
│   ├── imgs/                   # Imágenes subidas en local; ignorado por Git
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
    │       ├── 2026-11-06-estadisticas-gestion/
    │       ├── 2026-11-06-estetica-compra-entradas/
    │       ├── 2026-11-07-chatbot-rag/
    │       ├── 2026-11-07-fondo-decorativo/
    │       ├── 2026-11-07-ui-validar-entradas/
    │       ├── 2026-11-09-estetica-hero-entradas-compra/
    │       └── 2026-11-10-gestion-cuentas-y-bloqueos/
    └── specs/
        ├── .gitkeep
        ├── chatbot/
        ├── compras/
        ├── cuentas/
        ├── entradas/
        ├── estadisticas/
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
- **Healthcheck:** ejecuta `curl -fsS http://localhost:8000/` cada 30 s. La ruta `/` está configurada hacia `views.home`; una petición anónima renderiza la portada, por lo que no falla por una ruta inexistente [Dockerfile](Dockerfile), [urls.py](movie_up/core/urls.py), [views.py](movie_up/core/views.py).

**Cómo ejecutar (según AGENTS.md):**
- Levantar todo: `docker compose up --build` [AGENTS.md](AGENTS.md)
- Migraciones: se aplican automáticamente al arrancar (docker-entrypoint.sh) [AGENTS.md](AGENTS.md)
- Migraciones manuales: `docker compose exec web python movie_up/manage.py migrate` [AGENTS.md](AGENTS.md)
- Crear superusuario: `docker compose exec web python movie_up/manage.py createsuperuser` [AGENTS.md](AGENTS.md)
- Correr tests: `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas compras estadisticas chatbot core` — cada app nueva se suma a la lista, porque el discovery sin etiquetas no descubre nada [AGENTS.md](AGENTS.md)
- App: http://localhost:8000/ (usar `localhost`, NO `0.0.0.0`) [AGENTS.md](AGENTS.md)
- **Estado de la ruta raíz:** `/` está configurada hacia `views.home`; las visitas anónimas renderizan la portada y las cuentas `is_staff` se redirigen a `/gestion/`. 

#### Preparación de un clon nuevo
- **Requisitos previos:** Docker Desktop instalado y Docker Compose disponible [Docker Compose installation docs](https://docs.docker.com/compose/install/).
- **Entorno local:** copia `.env_ejemplo` a `.env`. Completa `DB_ROOT_PASSWORD` y `DB_NAME`; elige el puerto del host en `DB_LOCAL_PORT` y establece `DB_DOCKER_PORT=3306`. Si `3306` ya está ocupado en el host, puedes usar `DB_LOCAL_PORT=3307` y mantener `DB_DOCKER_PORT=3306`. `DB_USER` es opcional y, si se omite, Django usa `root`. Asigna a `SECRET_KEY` un valor privado local y configura `DEBUG=True` para desarrollo. Si vas a habilitar el chatbot, obtén `GROQ_API_KEY` en la [consola de Groq](https://console.groq.com/keys) y guárdala en `.env` [`.env_ejemplo`](.env_ejemplo), [docker-compose.yml](docker-compose.yml), [settings.py](movie_up/core/settings.py).
- **Google OAuth local:** crea en Google Cloud un cliente OAuth de tipo Web y agrega `http://localhost:8000/accounts/google/login/callback/` como URI de redirección autorizada. Guarda las credenciales obtenidas en `.env`, usando las variables de Google ya descritas en la subsección de integración [Google provider documentation](https://github.com/pennersr/django-allauth/blob/main/docs/socialaccount/providers/google.rst), [urls.py](movie_up/core/urls.py), [settings.py](movie_up/core/settings.py).
- **Catálogo inicial:** un volumen de base de datos nuevo no incluye películas, salas ni funciones de ejemplo. Cárgalas desde los paneles correspondientes de `/gestion/` [docker-compose.yml](docker-compose.yml), [gestion.html](movie_up/templates/gestion.html), [\_listado.html](movie_up/peliculas/templates/peliculas/_listado.html), [\_listado.html](movie_up/salas/templates/salas/_listado.html), [\_listado.html](movie_up/funciones/templates/funciones/_listado.html).
- **Ingesta y disponibilidad del chatbot:** ejecuta `docker compose exec web python ingest.py movie_up/chatbot/data/chatbot.md`. El comando crea la colección Chroma en `chroma_db/`, directorio ignorado por Git. La primera ingesta requiere acceso a la red desde el contenedor para descargar los embeddings; si falta `GROQ_API_KEY` o la colección no está ingerida, el endpoint devuelve `503` [docker-compose.yml](docker-compose.yml), [ingest.py](ingest.py), [.gitignore](.gitignore), [design.md](openspec/changes/archive/2026-11-07-chatbot-rag/design.md), [services.py](movie_up/chatbot/services.py), [views.py](movie_up/chatbot/views.py).

### Configuración Django
- **DEBUG/SECRET_KEY** desde variables de entorno [settings.py](movie_up/core/settings.py)
- **ALLOWED_HOSTS** incluye `localhost`, `0.0.0.0`, `127.0.0.1` [settings.py](movie_up/core/settings.py)
- **Base de datos MySQL** configurada con credenciales desde `.env` [settings.py](movie_up/core/settings.py)
- **Apps instaladas:** después de `django.contrib.*` y las apps de `django-allauth`, las apps del proyecto aparecen en este orden: `core`, `chatbot`, `compras`, `cuentas`, `entradas`, `estadisticas`, `funciones`, `peliculas`, `salas` [settings.py](movie_up/core/settings.py)
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
- Roles: Cliente y Administrador [AGENTS.md](AGENTS.md).
- El modelo de usuario es `cuentas.Cuenta` (`AUTH_USER_MODEL`), basado en `AbstractUser`, con `correo` único y `nombre`; no conserva `username`, `email`, `first_name` ni `last_name` [models.py](movie_up/cuentas/models.py), [settings.py](movie_up/core/settings.py).
- Las cuentas sociales ingresan solo con Google. El alta requiere que Google marque el correo como verificado. El nombre se obtiene del perfil, con respaldo en los nombres parciales y luego en la parte local del correo; los logins siguientes no reescriben los datos del perfil [adapters.py](movie_up/cuentas/adapters.py), [spec.md](openspec/changes/archive/2026-11-02-login-google/specs/cuentas/spec.md).
- La primera cuenta nueva se promueve a administradora completa; las posteriores quedan como cuentas comunes. La señal `user_signed_up` llama al servicio que serializa la promoción con `GET_LOCK`/`RELEASE_LOCK` de MySQL [signals.py](movie_up/cuentas/signals.py), [services.py](movie_up/cuentas/services.py).
- En Django Admin, `correo` y `nombre` son de solo lectura, no se permiten altas manuales y el indicador de administración sincroniza `is_staff` con `is_superuser`. Los guards de borrado individual y masivo están activos: bloquean la eliminación de cuentas con entradas asociadas. [admin.py](movie_up/cuentas/admin.py), [tasks.md](openspec/changes/archive/2026-11-02-crud-entradas/tasks.md). Además, `/gestion/` ofrece un listado de cuentas con correo, nombre y permisos, sin acciones de CRUD. El control llama a `cuentas.services.toggle_permisos`, que cambia el indicador de administrador de otra cuenta y sincroniza `is_staff` e `is_superuser` en un solo guardado; el servidor rechaza cambios sobre la cuenta propia [services.py](movie_up/cuentas/services.py). El acceso directo a `/admin/` se conserva; se quitó únicamente el enlace desde la pestaña Cuentas. [spec.md](openspec/specs/cuentas/spec.md), [spec.md](openspec/specs/ui/spec.md), [design.md](openspec/changes/archive/2026-11-10-gestion-cuentas-y-bloqueos/design.md)
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
- Entre los cinco changes archivados documentados inicialmente están `crud-peliculas` (CRUD completo de películas con Service Layer), `crud-salas` (CRUD de salas con editor de distribución en grilla), `crud-funciones` (CRUD de funciones con snapshot de la distribución de la sala y bloqueo de solapamientos serializado), `crud-entradas` (creación interna por compra, listado y detalle propios, validación por código y reembolso con límite de 24 horas) y `login-google` (identidad y login únicamente con Google vía django-allauth, modelo `Cuenta` y regla del primer administrador). Los cinco conservan sus artefactos (proposal, specs, design, tasks) [proposal.md](openspec/changes/archive/2026-10-31-crud-peliculas/proposal.md), [proposal.md](openspec/changes/archive/2026-11-01-crud-salas/proposal.md), [proposal.md](openspec/changes/archive/2026-11-01-crud-funciones/proposal.md), [proposal.md](openspec/changes/archive/2026-11-02-crud-entradas/proposal.md), [proposal.md](openspec/changes/archive/2026-11-02-login-google/proposal.md).
- **Estado actual:** hay 16 changes archivados y ninguno activo. El más reciente es `2026-11-10-gestion-cuentas-y-bloqueos`; sus 15 tareas están completas y se registran la suite completa, `makemigrations --check`, validación OpenSpec y verificación con Playwright [archive](openspec/changes/archive/), [changes](openspec/changes/), [tasks.md](openspec/changes/archive/2026-11-10-gestion-cuentas-y-bloqueos/tasks.md).
- Las nueve specs vigentes contienen: `movies` (7 requisitos, 21 escenarios), `salas` (13, 43), `funciones` (18, 37), `entradas` (26, 69), `cuentas` (14, 38), `compras` (17, 61), `estadisticas` (8, 14), `chatbot` (10, 21) y `ui` (25, 71) [spec.md](openspec/specs/movies/spec.md), [spec.md](openspec/specs/salas/spec.md), [spec.md](openspec/specs/funciones/spec.md), [spec.md](openspec/specs/entradas/spec.md), [spec.md](openspec/specs/cuentas/spec.md), [spec.md](openspec/specs/compras/spec.md), [spec.md](openspec/specs/estadisticas/spec.md), [spec.md](openspec/specs/chatbot/spec.md), [spec.md](openspec/specs/ui/spec.md).

`crud-entradas` fue archivado el 2026-11-02 en `openspec/changes/archive/2026-11-02-crud-entradas/` con su `.openspec.yaml` preservado y 29/29 tareas completadas; la sincronización de specs escribió `openspec/specs/entradas/spec.md` y actualizó en `openspec/specs/cuentas/spec.md` el requisito "Borrado bloqueado por entradas asociadas", que dejó de condicionar el guard a un `TODO` [tasks.md](openspec/changes/archive/2026-11-02-crud-entradas/tasks.md), [proposal.md](openspec/changes/archive/2026-11-02-crud-entradas/proposal.md), [spec.md](openspec/specs/entradas/spec.md), [spec.md](openspec/specs/cuentas/spec.md).

#### Change archivado `gestion-cuentas-y-bloqueos`

El change sincronizó cambios en las specs de `cuentas`, `movies`, `salas` y `ui` [spec.md](openspec/changes/archive/2026-11-10-gestion-cuentas-y-bloqueos/specs/cuentas/spec.md), [spec.md](openspec/changes/archive/2026-11-10-gestion-cuentas-y-bloqueos/specs/movies/spec.md), [spec.md](openspec/changes/archive/2026-11-10-gestion-cuentas-y-bloqueos/specs/salas/spec.md), [spec.md](openspec/changes/archive/2026-11-10-gestion-cuentas-y-bloqueos/specs/ui/spec.md).

La edición de una sala se rechaza si tiene funciones activas; el borrado, si tiene cualquier función asociada, incluso desactivada [spec.md](openspec/specs/salas/spec.md).

La pestaña Cuentas queda dentro de `/gestion/`. Los formularios de edición ofrecen `Guardar cambios` y `Cancelar`; cancelar muestra el detalle del registro [spec.md](openspec/specs/ui/spec.md).


#### Parseo y validación de specs (gotcha)

OpenSpec parsea los artefactos con tokens estructurales fijos en inglés. Traducirlos produce un archivo que se lee bien pero que el CLI no puede interpretar [AGENTS.md](AGENTS.md).

- **Tokens intocables:** `## Purpose` y `## Requirements` en la spec principal, `## ADDED Requirements` en el delta, requisitos `### Requirement: <nombre>`, escenarios `#### Scenario: <nombre>` con exactamente 4 `#`, pasos `**WHEN**` / `**THEN**` [spec.md](openspec/specs/movies/spec.md), [spec delta](openspec/changes/archive/2026-10-31-crud-peliculas/specs/movies/spec.md).
- **Fallo silencioso:** sin `## ADDED Requirements`, `openspec validate` reporta `No delta sections found` / `Change must have at least one delta`, y el archive completa sin escribir nada en `openspec/specs/`. Marcar todas las tareas no protege de esto: un change con 19 de 19 tareas completas puede archivar sin producir la spec [AGENTS.md](AGENTS.md), [tasks.md](openspec/changes/archive/2026-10-31-crud-peliculas/tasks.md).
- **RFC 2119 literal:** `--strict` busca las palabras `SHALL` / `MUST`; `DEBE` / `DEBEN` falla la validación. Convención adoptada: prosa en español con las keywords normativas en inglés [AGENTS.md](AGENTS.md).
- **Mapeo normativo del proyecto:** `SHALL` describe la capacidad que el sistema provee; `MUST` marca obligaciones y condiciones de error (404 en identificadores inexistentes, rechazo de título duplicado, reemplazo de la imagen anterior, bloqueo del borrado con funciones asociadas) [spec.md](openspec/specs/movies/spec.md).
- **Puerta de verificación:** `openspec validate --specs --strict` con exit 0 y cero warnings es obligatorio antes de archivar; es la única señal de que la spec va a llegar efectivamente a la fuente de verdad [AGENTS.md](AGENTS.md).
- **Separación spec / design:** la spec describe solo comportamiento observable; las restricciones de implementación (tipos de campo derivados del DDL, `ImageField`, delegación a `services.py`, templates HTML puro sin CSS/JS, bloque comentado de `funciones`) permanecen en el design del change [design.md](openspec/changes/archive/2026-10-31-crud-peliculas/design.md).


## 2. Casos de uso e implementacion

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

**Estado de ventas:** `Gestionar ventas (CRUD)` permanece en la lista como caso canónico, que se conserva como espejo de [AGENTS.md](AGENTS.md). Para el alcance actual que documenta este README, el CRUD está **descartado/no implementado**. No existe una app, modelo ni administración de ventas; `compras` expone el flujo de compra del cliente, y las estadísticas son una consulta, no un CRUD [urls.py](movie_up/compras/urls.py), [models.py](movie_up/compras/models.py), [admin.py](movie_up/compras/admin.py), [views.py](movie_up/core/views.py).

Las métricas semanales, mensuales y anuales calculan importes como `entradas_compradas * precio_entrada`, agrupados por película y género según la fecha de inicio de la función. Incluyen funciones activas e inactivas; son valores derivados de contadores, no pagos capturados [services.py](movie_up/estadisticas/services.py), [spec.md](openspec/specs/estadisticas/spec.md), [spec.md](openspec/specs/compras/spec.md).

**Aclaración sobre el caso canónico de compra:** aunque la lista conserva la referencia a Mercado Pago, el checkout actual confirma la compra sin mostrar un paso de pago ni procesar un cobro [requirements.txt](requirements.txt), [spec.md](openspec/specs/compras/spec.md).

### CRUD de peliculas (`crud-peliculas`)
**Contrapartida:** `False` y `0` se tratan como valores intencionales, así que un llamador debe omitir el campo —no enviarlo vacío— para dejarlo sin modificar [services.py](movie_up/peliculas/services.py).

El alta exige título, género, duración, descripción, clasificación, fecha de estreno, URL del tráiler y portada; el formulario usa límites HTML5 para título (150 caracteres), género (45), duración (mínimo 1), clasificación (10) y URL (255), además de `type=date`, `type=url` y `accept=image/*`. El checkbox `en_cartelera` es opcional y parte desmarcado. Estas restricciones se aplican en el navegador; las vistas no llaman a `full_clean()` para revalidar los campos en peticiones directas [\_form.html](movie_up/peliculas/templates/peliculas/_form.html), [models.py](movie_up/peliculas/models.py), [views.py](movie_up/peliculas/views.py).

El título es único en el modelo y el servicio comprueba duplicados [models.py](movie_up/peliculas/models.py), [services.py](movie_up/peliculas/services.py).

En edición, los campos son opcionales y una portada vacía conserva la actual; si se carga otra, el servicio guarda la nueva antes de borrar el archivo anterior [\_form.html](movie_up/peliculas/templates/peliculas/_form.html), [services.py](movie_up/peliculas/services.py).

Las rutas del CRUD están restringidas a personal: las visitas anónimas van al login y las cuentas comunes vuelven a la página principal [views.py](movie_up/peliculas/views.py), [decorators.py](movie_up/core/decorators.py).

Cuando hay funciones asociadas —activas o no— solo se permite cambiar `en_cartelera` y se rechaza el borrado; esta regla también queda resumida en la sección del change archivado [services.py](movie_up/peliculas/services.py), [spec.md](openspec/specs/movies/spec.md).

### CRUD de salas (`crud-salas`, lotes 1–3)
- **Lote 1 — modelo y Service Layer:** `Sala` persiste la distribución como JSON. El service valida y normaliza filas de hasta 100×100 con celdas `P`, `A` y `R`, deriva la capacidad contando `A` y `R`, y guarda dentro del JSON una versión que solo aumenta ante cambios reales de la distribución normalizada. Inicialmente, los guards para funciones quedaron comentados hasta que existiera la app `funciones`, evitando imports a módulos inexistentes [models.py](movie_up/salas/models.py), [services.py](movie_up/salas/services.py), [design.md](openspec/changes/archive/2026-11-01-crud-salas/design.md).
- **Implementación posterior de los guards:** en `salas/services.py`, `update_sala` rechaza actualizar una sala con funciones activas y `delete_sala` rechaza eliminarla si tiene cualquier función asociada, activa o no [services.py](movie_up/salas/services.py).
- **Lote 2 — interfaz y administración:** el CRUD web usa vistas y rutas con namespace, templates y registro en Django Admin. El editor JavaScript alterna `P` → `A` → `R` → `P` y permite redimensionar conservando la intersección; el detalle renderiza la misma distribución en modo de solo lectura [urls.py](movie_up/salas/urls.py), [views.py](movie_up/salas/views.py), [admin.py](movie_up/salas/admin.py), [grid.js](movie_up/salas/static/salas/js/grid.js), [salas.css](movie_up/salas/static/salas/css/salas.css), [design.md](openspec/changes/archive/2026-11-01-crud-salas/design.md).
- **Lote 3 — integración:** la verificación cubrió los tests de `peliculas` y `salas`, además del recorrido CRUD de salas en navegador real con Playwright [tasks.md](openspec/changes/archive/2026-11-01-crud-salas/tasks.md).

El alta requiere nombre, tipo de sala y tipo de sonido; cada campo admite hasta 45 caracteres. El nombre debe ser único: el servicio verifica duplicados tanto al crear como al actualizar, excluyendo la propia sala en una actualización. Las rutas de gestión están restringidas a personal; las visitas anónimas van al login y las cuentas comunes vuelven a la página principal [\_form.html](movie_up/salas/templates/salas/_form.html), [services.py](movie_up/salas/services.py), [views.py](movie_up/salas/views.py), [decorators.py](movie_up/core/decorators.py).

### CRUD de funciones (`crud-funciones`)
El Service Layer concentra esta lógica porque la función conserva un snapshot de la distribución de su sala y la validación de solapamientos debe ejecutarse de forma serializada [services.py](movie_up/funciones/services.py), [design.md](openspec/changes/archive/2026-11-01-crud-funciones/design.md).

El CRUD administra película, sala, inicio, idioma, subtítulos, precio y estado activa/inactiva. Al crear, estos datos son obligatorios; al editar, son opcionales. El fin se calcula con la duración de la película y cambiar la sala reemplaza la distribución y recalcula la disponibilidad [\_form.html](movie_up/funciones/templates/funciones/_form.html), [models.py](movie_up/funciones/models.py), [spec.md](openspec/specs/funciones/spec.md).

El servicio rechaza inicios pasados al crear o cambiar el horario, precios negativos o con más de dos decimales, la activación de funciones vencidas y los solapamientos en la misma sala, incluso con funciones inactivas. También rechaza actualizar o borrar desde el CRUD web cuando `entradas_compradas > 0` [services.py](movie_up/funciones/services.py), [spec.md](openspec/specs/funciones/spec.md).

Las rutas web están restringidas a personal [views.py](movie_up/funciones/views.py), [decorators.py](movie_up/core/decorators.py). `FuncionAdmin` solo declara `list_display` y no invoca los servicios del CRUD; por eso, el guard de entradas compradas no se comparte con esa vía [admin.py](movie_up/funciones/admin.py), [services.py](movie_up/funciones/services.py). `Entrada.funcion` usa `PROTECT` mientras haya entradas relacionadas, pero el barrido de vencidas elimina esas filas sin reiniciar el contador; esto no garantiza que Django Admin aplique la misma restricción [models.py](movie_up/entradas/models.py), [services.py](movie_up/compras/services.py).

La suite completa pasó 111/111 tests. En navegador se verificaron Create, Detail con cuadrícula, Update y Delete; el rechazo de solapamientos fue visible y la consola quedó limpia [tasks.md](openspec/changes/archive/2026-11-01-crud-funciones/tasks.md), [.playwright-mcp/](.playwright-mcp/).

- **Flujo de petición:** `urls.py` → `views.py` → `services.py` → `models.py` → `templates/`.

### Home, navegación y acceso por rol

La portada redirige a `/gestion/` a las cuentas `is_staff`. Para el resto muestra películas en cartelera: el hero toma hasta tres por fecha de estreno y, si hay al menos dos, las rota cada siete segundos; el grid incluye la cartelera [views.py](movie_up/core/views.py), [home.html](movie_up/templates/home.html), [hero-carousel.js](movie_up/static/js/hero-carousel.js).

El nav ofrece login con Google a visitantes; las cuentas autenticadas ven su perfil y `Logout`. Las cuentas comunes tienen `Mis entradas` y el personal, `Validar entradas` [site_nav.html](movie_up/templates/includes/site_nav.html).

El panel `/gestion/` contiene cinco pestañas —Películas, Funciones, Salas, Cuentas y Estadísticas— con paneles precargados; JavaScript alterna su visibilidad sin cambiar la URL [management_subnav.html](movie_up/templates/includes/management_subnav.html), [gestion.html](movie_up/templates/gestion.html), [management-tabs.js](movie_up/static/js/management-tabs.js).

### Compra, entradas y vencimientos

`/compras/<pelicula_id>/` está destinada a cuentas comunes autenticadas. Los visitantes van al login de Google con retorno a esa página y las cuentas `is_staff` se redirigen a `/gestion/`. El listado muestra funciones activas cuyo fin no pasó, ordenadas por inicio [views.py](movie_up/compras/views.py), [services.py](movie_up/compras/services.py), [spec.md](openspec/specs/compras/spec.md).

Al preparar el listado se ejecuta, dentro de la solicitud, un barrido atómico de funciones vencidas de esa película; no es un job de fondo. El barrido elimina las entradas asociadas y desactiva la función, pero conserva el contador de entradas, la disponibilidad y la distribución [services.py](movie_up/compras/services.py), [spec.md](openspec/specs/funciones/spec.md).

La confirmación valida de nuevo la función, la distribución y los asientos seleccionados, y crea una entrada por asiento dentro de una transacción. Rechaza selecciones vacías, duplicadas, obsoletas, ocupadas o que excedan la disponibilidad [services.py](movie_up/compras/services.py), [services.py](movie_up/entradas/services.py).

Las entradas se crean por el servicio de compra; cada código es único y cada cuenta solo consulta las propias. El personal puede validar una entrada activa una sola vez. El reembolso requiere una entrada activa y al menos 24 horas de anticipación —exactamente 24 horas se permite—; elimina la entrada y restaura el asiento y los contadores, pero no devuelve dinero [models.py](movie_up/entradas/models.py), [services.py](movie_up/entradas/services.py), [views.py](movie_up/entradas/views.py), [spec.md](openspec/specs/entradas/spec.md).

### Chatbot de ayuda (RAG)

#### Alcance y fuentes de respuesta
El asistente combina un documento de ayuda estático con un snapshot actual de la cartelera. Las preguntas sugeridas cubren tres temas dinámicos de cartelera y cinco temas de ayuda [spec.md](openspec/specs/chatbot/spec.md), [widget.html](movie_up/chatbot/templates/chatbot/widget.html).

- **Ayuda estática:** `movie_up/chatbot/data/chatbot.md` explica la frecuencia promedio de estrenos (2–4 películas al mes), cómo comprar entradas, cómo solicitar reembolsos y sus restricciones, cómo usar la entrada virtual y qué datos se guardan al registrarse con Google. La consulta sobre Google es información general; el servicio no consulta el perfil ni la cuenta individual [chatbot.md](movie_up/chatbot/data/chatbot.md), [services.py](movie_up/chatbot/services.py).
- **Cartelera actual:** en cada pregunta el servicio consulta las películas con `en_cartelera=True` y sus funciones activas cuyo fin todavía no pasó. El contexto incluye datos de películas, fechas, funciones, salas, horarios, idioma, subtítulos, precios y disponibilidad. “La película más nueva” se determina por fecha de estreno entre las películas actualmente en cartelera; estos datos no dependen de reingerir el documento [services.py](movie_up/chatbot/services.py).
- **Límite de la información de pago:** las instrucciones de compra y reembolso indican que describen el flujo previsto suponiendo que la pasarela de pago está integrada. Son orientación documental, no evidencia de que el chatbot procese pagos o reembolsos [chatbot.md](movie_up/chatbot/data/chatbot.md).

#### Ingesta, embeddings y almacenamiento
`ingest.py` carga un documento Markdown UTF-8 y lo divide con `RecursiveCharacterTextSplitter` en fragmentos de 500 caracteres con solapamiento de 50, priorizando separadores de encabezados [ingest.py](ingest.py).

Los embeddings vienen del Hub de Hugging Face: `HuggingFaceEmbeddings` usa el identificador `sentence-transformers/all-MiniLM-L6-v2`. El modelo ocupa aproximadamente 80 MB y se descarga para la primera ingesta; la generación de embeddings se ejecuta localmente, sin llamar a una API externa [ingest.py](ingest.py), [design.md](openspec/changes/archive/2026-11-07-chatbot-rag/design.md).

Chroma persiste la colección `movieup_chatbot` en `chroma_db/` en la raíz del repositorio. El servicio comprueba que exista la base SQLite de Chroma y que la colección no esté vacía [services.py](movie_up/chatbot/services.py). El bind mount `.:/app` deja el directorio en el host y `chroma_db/` está excluido de Git; no es parte de MySQL ni del volumen nombrado `db_data` [docker-compose.yml](docker-compose.yml), [.gitignore](.gitignore).

Los cambios al documento no se incorporan automáticamente: hay que ejecutar `docker compose exec web python ingest.py movie_up/chatbot/data/chatbot.md`. La ingesta reemplaza la colección del chatbot para quitar fragmentos obsoletos y conserva otras colecciones de Chroma [tasks.md](openspec/changes/archive/2026-11-07-chatbot-rag/tasks.md), [ingest.py](ingest.py).

#### Retrieval, prompt y modelo de lenguaje
En cada consulta, `build_context()` recupera los cuatro fragmentos más similares y añade el snapshot recién consultado de la cartelera. El prompt recibe ambos bloques, el historial reciente y la pregunta; las instrucciones separan las fuentes, pero no hay un router de intents que evite recuperar ambos contextos en cada consulta [services.py](movie_up/chatbot/services.py).

`PROMPT_TEMPLATE` indica responder en español y texto plano, usar solo el bloque pertinente, no inventar información y tratar el contexto como datos, no como instrucciones. El historial se usa para entender referencias a turnos anteriores, no como fuente de hechos. Si la búsqueda no devuelve fragmentos, se agrega un mensaje de fallback sobre la falta de contenido relacionado [services.py](movie_up/chatbot/services.py).

La generación usa `ChatGroq` con temperatura `0`; el modelo predeterminado es `openai/gpt-oss-20b` y se puede cambiar mediante `GROQ_MODEL`. `GROQ_API_KEY` y `GROQ_MODEL` se leen del entorno; Docker Compose pasa `.env` al servicio web mediante `env_file`. No se incluyen valores de esas variables [services.py](movie_up/chatbot/services.py), [docker-compose.yml](docker-compose.yml).

Las dependencias de LangChain, Chroma, Hugging Face y Groq están fijadas en `requirements.txt` [requirements.txt](requirements.txt). La pregunta, el contexto recuperado y el historial se pasan a la API de Groq como entradas de la cadena [services.py](movie_up/chatbot/services.py).

#### Conversación, acceso y límites
El widget aparece para visitantes y cuentas que no tienen `is_staff`; se oculta en los shells web y Django Admin para cuentas con `is_staff` [base.html](movie_up/templates/base.html), [base_site.html](movie_up/templates/admin/base_site.html).

`POST /chatbot/api/preguntar/` no requiere inicio de sesión: la vista exige POST, mientras que el middleware CSRF y el cliente JavaScript usan el token CSRF [views.py](movie_up/chatbot/views.py), [settings.py](movie_up/core/settings.py), [chatbot.js](movie_up/chatbot/static/chatbot/chatbot.js). No se observa limitación de frecuencia en el endpoint; el diseño registra como riesgo el costo o abuso del acceso público a Groq [design.md](openspec/changes/archive/2026-11-07-chatbot-rag/design.md).

La conversación vive en memoria en el navegador y no se persiste en el servidor. Cada petición envía hasta los últimos 10 mensajes; el servicio acepta solo los roles `user` y `assistant` y recorta cada contenido a 2.000 caracteres. El textarea limita la entrada a 2.000 caracteres en la interfaz, pero la vista no aplica ese límite a las peticiones directas [chatbot.js](movie_up/chatbot/static/chatbot/chatbot.js), [services.py](movie_up/chatbot/services.py), [widget.html](movie_up/chatbot/templates/chatbot/widget.html), [views.py](movie_up/chatbot/views.py).

La disponibilidad requiere `GROQ_API_KEY` y una colección Chroma utilizable. JSON inválido o una pregunta vacía produce `400`; una configuración incompleta o un fallo del servicio produce `503`. Las respuestas válidas se devuelven como `answer` en JSON [views.py](movie_up/chatbot/views.py), [services.py](movie_up/chatbot/services.py).

#### Verificación de extremo a extremo
En Playwright a 1280×900, al seleccionar la sugerencia “Películas en cartelera” se obtuvo una respuesta real de Groq. La captura muestra la pregunta y la lista de películas devuelta [chatbot-final-home.png](.playwright-mcp/chatbot-final-home.png). La tarea final de verificación está registrada en [tasks.md](openspec/changes/archive/2026-11-07-chatbot-rag/tasks.md).

El CLI raíz `chat.py` ofrece modo interactivo y `--question`, reutilizando el mismo servicio [chat.py](chat.py).


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

Las fuentes del proyecto conservan instrucciones reutilizables para dirigir al agente, pero no transcripciones de los mensajes de usuario empleados durante la construcción. `opsx:explore` delimita la exploración de la implementación y exige confirmación antes de escribir artefactos [opsx-explore.md](.opencode/commands/opsx-explore.md); `opsx:propose` restringe su flujo a la planificación [opsx-propose.md](.opencode/commands/opsx-propose.md); `opsx:apply` recorre tareas y se detiene ante errores o bloqueos [opsx-apply.md](.opencode/commands/opsx-apply.md), [SKILL.md](.opencode/skills/openspec-apply-change/SKILL.md); `opsx:archive` comprueba completitud y estado de sincronización antes de archivar [opsx-archive.md](.opencode/commands/opsx-archive.md).

El `PROMPT_TEMPLATE` de `movie_up/chatbot/services.py` es el prompt runtime del chatbot, no un prompt de ingeniería [services.py](movie_up/chatbot/services.py).


### 3.3 Metodología de iteración
- **Desarrollo dirigido por especificaciones (Spec-Driven Development)**: Uso obligatorio de OpenSpec. Las specs (`openspec/specs/`) son fuente de verdad; los cambios pasan por artefactos estructurados (proposal, specs, design, tasks) antes de implementar [AGENTS.md](AGENTS.md).
- **Iteración del change `login-google`:** OpenSpec organizó el trabajo en lotes secuenciales: modelo, configuración y migración; alta social, mapeo del perfil y bootstrap; luego administración, guard y cierre. La prueba manual con Google quedó como puerta final y no se reemplazó por el callback automatizado simulado [tasks.md](openspec/changes/archive/2026-11-02-login-google/tasks.md), [design.md](openspec/changes/archive/2026-11-02-login-google/design.md).
- **Iteración del change `chatbot-rag`:** las tareas se organizaron en cinco grupos: dependencias/configuración, documento e ingesta, service/endpoint/widget, CLI y verificación integral. La evidencia final incluye una consulta de Playwright sobre “Películas en cartelera” [tasks.md](openspec/changes/archive/2026-11-07-chatbot-rag/tasks.md), [chatbot-final-home.png](.playwright-mcp/chatbot-final-home.png).
- **Mantenimiento controlado de README**: El agente `readme-maintainer` se activa automáticamente tras cada creación o modificación de archivos, evalúa si el cambio aporta al registro de ingeniería, y si es relevante presenta todos los cambios propuestos de una sola vez (sección, texto, tipo: fusionar/reemplazar/agregar) esperando `ok` antes de editar [AGENTS.md](AGENTS.md), [readme-maintainer.md](.opencode/agent/readme-maintainer.md).
- **Verificación de UI en navegador real (directiva AGENTS.md)**: Antes de dar por hecha una vista, verificarla en navegador real vía Playwright MCP (levantar con `docker compose up --build` y navegar `http://localhost:8000/`). La referencia de configuración de MCPs vive en README.md sección 4 [AGENTS.md](AGENTS.md).
- **Arquitectura containerizada desde el inicio**: Setup Docker con multi-stage build, healthcheck, entrypoint con espera de DB y migraciones automáticas [Dockerfile](Dockerfile), [docker-entrypoint.sh](docker-entrypoint.sh), [AGENTS.md](AGENTS.md).
- **Institucionalización de decisiones arquitectónicas vía skills**: las decisiones arquitectónicas no quedan solo como directiva textual; se formalizan en skills ejecutables. Ejemplo: la adopción de **Service Layer** como patrón oficial (lógica de negocio en `services.py`, vistas delgadas `request → service → response`) se documentó en [AGENTS.md](AGENTS.md) y se hizo cumplir automáticamente mediante el skill `django-app-creator`, que genera `services.py` en cada app nueva [AGENTS.md](AGENTS.md), [django-app-creator SKILL.md](.opencode/skills/django-app-creator/SKILL.md). Así, la convención no depende de que el agente "se acuerde": el skill la garantiza estructuralmente. Segundo ejemplo, de naturaleza distinta: `crud-conventions` no genera código sino que institucionaliza **convenciones de diseño de specs**, capturando en Decision Gates y Hard Rules lo aprendido en `peliculas` y `salas` para que los próximos CRUDs del catálogo (funciones, ventas) no tengan que rederivar esas convenciones desde cero en cada planificación [crud-conventions SKILL.md](.opencode/skills/crud-conventions/SKILL.md).
Tercer ejemplo, de naturaleza visual: `ui-design` institucionaliza **decisiones de diseño de interfaz** —paleta cerrada de 12 tokens con sus pares de texto, proporciones, tipografía de dos familias y reglas de botón y centrado— en Hard Rules y Decision Gates, de modo que toda tarea visual respete el sistema sin depender de la memoria de la sesión, y su protocolo de desviación fuerza una pregunta sí/no antes de aplicar un color fuera de la paleta [ui-design SKILL.md](.opencode/skills/ui-design/SKILL.md).

### 3.4 Bucles de autocorrección automatizados
[PENDIENTE: en las fuentes versionadas no aparece un sistema autónomo de auto-reparación. No se puede afirmar si hubo hooks externos no versionados.]

**Loop guiado por el agente:** `/opsx:apply` recorre tareas pendientes y vuelve a consultar instrucciones/progreso; ante error o bloqueo, detiene la ejecución y reporta, en lugar de iniciar un ciclo autónomo de reparación [opsx-apply.md](.opencode/commands/opsx-apply.md), [SKILL.md](.opencode/skills/openspec-apply-change/SKILL.md).

**Validación como gate, no como auto-fix:** tests, `openspec validate` y Playwright verifican resultados; la corrección posterior requiere una acción del agente o del usuario. Por ejemplo, `openspec validate --specs --strict` detecta deltas no parseables, pero no los reescribe [AGENTS.md](AGENTS.md), [tasks.md](openspec/changes/archive/2026-10-31-crud-peliculas/tasks.md).

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
- **Rol en desarrollo:** proporciona memoria persistente entre sesiones [AGENTS.md](C:/Users/anlle/.config/opencode/AGENTS.md).

### 4.3 playwright
- **Tipo:** local [opencode.json](C:/Users/anlle/.config/opencode/opencode.json)
- **Comando:** `npx -y @playwright/mcp@latest --browser msedge` (timeout 60000) [opencode.json](C:/Users/anlle/.config/opencode/opencode.json)
- **Propósito:** Servidor MCP local de Microsoft (`@playwright/mcp`) para que el agente verifique los flujos de UI de MovieUp en un navegador real (selección de asientos, checkout, vistas de administrador).
- **Rol en desarrollo:** Validación automatizada de la interfaz contra el stack Docker real, complementando la verificación por código/tests con evidencia visual y funcional en navegador. Además ejecuta la directiva de AGENTS.md: antes de dar por hecha una vista, verificarla en navegador real vía Playwright MCP (levantar con `docker compose up --build` y navegar `http://localhost:8000/`); la referencia de configuración de MCPs vive en README.md sección 4 [AGENTS.md](AGENTS.md).
- **Decisiones no obvias:**
  - **Configuración verificable:** la configuración actual inicia Playwright con Edge (`--browser msedge`) y mantiene un bloque `mcp` plano con cada servidor declarado mediante `type` y `url` o `command` [opencode.json](C:/Users/anlle/.config/opencode/opencode.json).
  - Se creó backup previo en `opencode.json.bak`.

**Nota de configuración:** No se copian valores secretos. Solo se describe forma/configuración y rol, tal como se indica en [readme-maintainer.md](.opencode/agent/readme-maintainer.md). 