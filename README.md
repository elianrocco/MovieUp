# MovieUp - Log de Ingeniería

## 1. Visión general y arquitectura del sistema

**Fuente:** [AGENTS.md](AGENTS.md), [core/settings.py](core/settings.py), [core/urls.py](core/urls.py), [movie_up/](movie_up/), [requirements.txt](requirements.txt), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)

### Propósito del proyecto
MovieUp es un sistema web para la gestión y comercialización de entradas de cine. Permite a los usuarios comprar entradas, gestionar sus compras, y a los administradores gestionar películas, salas, funciones y ventas. [AGENTS.md](AGENTS.md)

### Stack tecnológico
- **Backend:** Python 3.14.7 con Django 6.1.1 y LangChain 1.4.0 [AGENTS.md](AGENTS.md), [requirements.txt](requirements.txt), [Dockerfile](Dockerfile)
- **Frontend:** HTML (Living Standard), CSS3 (Snapshot 2023) y JavaScript (ES2025) [AGENTS.md](AGENTS.md)
- **Base de datos:** MySQL 9.7.2 LTS [AGENTS.md](AGENTS.md), [docker-compose.yml](docker-compose.yml), [core/settings.py](core/settings.py)
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
│   └── skills/
│       ├── django-app-creator/
│       │   └── SKILL.md
│       └── openspec-*/           # 6 skills (explore, propose, apply, archive, sync, update)
│           └── SKILL.md
├── .playwright-mcp/              # logs de Playwright
├── movie_up/
│   ├── manage.py
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
    │       └── 2026-10-31-crud-peliculas/
    │           ├── .openspec.yaml
    │           ├── design.md
    │           ├── proposal.md
    │           ├── specs/
    │           │   └── movies/
    │           │       └── spec.md
    │           └── tasks.md
    └── specs/
        ├── .gitkeep
        └── movies/
            └── spec.md
```

### Configuración y despliegue con Docker
**Fuentes:** [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), [docker-entrypoint.sh](docker-entrypoint.sh), [core/settings.py](core/settings.py)

- **Multi-stage build** (builder/runtime): el builder compila dependencias como wheels usando `python:3.14.7-slim-trixie`, el runtime instala únicamente wheels precompilados con usuario no privilegiado (`appuser`) [Dockerfile](Dockerfile)
- **Servicios**: `db` (MySQL 9.7.2) y `web` (Django app) [docker-compose.yml](docker-compose.yml)
- **Variables de entorno**: inyectadas via `.env` y `env_file`; `DB_HOST=db`, `DB_PORT` se sobreescriben para el contenedor web [docker-compose.yml](docker-compose.yml)
- **Punto de entrada**: `docker-entrypoint.sh` espera a que la base de datos responda vía TCP, luego ejecuta `python movie_up/manage.py migrate --noinput` automáticamente [docker-entrypoint.sh](docker-entrypoint.sh), [AGENTS.md](AGENTS.md)
- **Healthcheck**: verifica respuesta HTTP en puerto 8000 cada 30s [Dockerfile](Dockerfile)

**Cómo ejecutar (según AGENTS.md):**
- Levantar todo: `docker compose up --build` [AGENTS.md](AGENTS.md)
- Migraciones: se aplican automáticamente al arrancar (docker-entrypoint.sh) [AGENTS.md](AGENTS.md)
- Migraciones manuales: `docker compose exec web python movie_up/manage.py migrate` [AGENTS.md](AGENTS.md)
- Crear superusuario: `docker compose exec web python movie_up/manage.py createsuperuser` [AGENTS.md](AGENTS.md)
- Correr tests: `docker compose exec web python movie_up/manage.py test` [AGENTS.md](AGENTS.md)
- App: http://localhost:8000/ (usar `localhost`, NO `0.0.0.0`) [AGENTS.md](AGENTS.md)
- **Estado verificado (smoke test vía Docker + Playwright):** `docker compose up --build` levanta correctamente; `http://localhost:8000/` sirve la página DEBUG por defecto de Django (aún no hay URLs raíz configuradas — `movie_up` no está en `INSTALLED_APPS`), mientras `/admin/login/` renderiza correctamente. Playwright genera artefactos de snapshot en `.playwright-mcp/` en la raíz del proyecto (sin versionar).
- **Gotcha crítica resuelta (2026-10-30):** La estructura del proyecto coloca `manage.py` en `movie_up/manage.py` (no en la raíz), lo cual es atípico en Django. Un bug inicial en [Dockerfile](Dockerfile) y [docker-entrypoint.sh](docker-entrypoint.sh) usaba rutas incorrectas (`manage.py` en vez de `movie_up/manage.py`), causando que el contenedor web no iniciara y las migraciones automáticas no se ejecutaran (bug silencioso). Todos los comandos `docker compose exec` y el entrypoint fueron actualizados consistentemente para usar la ruta correcta. **Lección:** En proyectos Django con estructura no estándar, verificar siempre la ruta relativa de `manage.py` en Dockerfile, entrypoint y documentación.

### Configuración Django
- **DEBUG/SECRET_KEY** desde variables de entorno [settings.py](movie_up/core/settings.py)
- **ALLOWED_HOSTS** incluye `localhost`, `0.0.0.0`, `127.0.0.1` [settings.py](movie_up/core/settings.py)
- **Base de datos MySQL** configurada con credenciales desde `.env` [settings.py](movie_up/core/settings.py)
- **Apps instaladas:** `django.contrib.*`, `peliculas` [settings.py](movie_up/core/settings.py)
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
- Roles: Cliente y Administrador/Empleado [AGENTS.md](AGENTS.md)
- Login local de Django; (planificado) Google OAuth [AGENTS.md](AGENTS.md)
- (A definir): cómo se otorga el rol admin — `is_staff` [AGENTS.md](AGENTS.md)

### Desarrollo dirigido por especificaciones (OpenSpec)
**Fuentes:** [AGENTS.md](AGENTS.md), [openspec/](openspec/), [openspec/config.yaml](openspec/config.yaml), [opsx-propose.md](.opencode/commands/opsx-propose.md)

- El proyecto usa **OpenSpec** para desarrollo dirigido por especificaciones (spec-driven development) [AGENTS.md](AGENTS.md)
- Especificaciones de verdad en `openspec/specs/` (organizadas por dominio) y cambios propuestos en `openspec/changes/` [AGENTS.md](AGENTS.md)
- Cada cambio incluye `proposal.md` (por qué), `specs/` (qué cambia), `design.md` (cómo) y `tasks.md` (pasos) [AGENTS.md](AGENTS.md)
- Flujo de trabajo: `/opsx:explore` → `/opsx:propose` → `/opsx:apply` → `/opsx:archive` [AGENTS.md](AGENTS.md)
- Comandos adicionales: `/opsx:sync` (sincronizar specs), `/opsx:update` (revisar el plan) [AGENTS.md](AGENTS.md)
- Definir specs antes de implementar cualquier nueva funcionalidad [AGENTS.md](AGENTS.md)
- Estado actual: el primer change implementado fue `crud-peliculas` (CRUD completo de películas con Service Layer), archivado en `openspec/changes/archive/2026-10-31-crud-peliculas/` con todos sus artefactos (proposal, specs, design, tasks) [proposal.md](openspec/changes/archive/2026-10-31-crud-peliculas/proposal.md). El archive escribió la primera spec de verdad del proyecto en `openspec/specs/movies/spec.md`: 5 requisitos (listar, detalle, crear, actualizar, eliminar) y 12 escenarios [spec.md](openspec/specs/movies/spec.md). Con el change archivado, `openspec list` devuelve `changes: []` y `openspec validate --specs --strict` pasa con exit 0 y cero warnings.


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
  - **`django-app-creator`** — Trigger: `crea app [nombre]`. Automatiza la creación de apps Django con estructura completa: ejecuta `python manage.py startapp <nombre>` desde `movie_up/`, registra la app en `INSTALLED_APPS` de [settings.py](core/settings.py), crea estructura de templates con namespacing doble (`templates/<nombre>/`) para evitar colisiones, crea `urls.py` con imports base, crea `services.py` para institucionalizar el Service Layer como convención oficial (toda app nueva nace con lógica de negocio separada de las vistas, consistente con AGENTS.md), y mantiene la documentación del proyecto actualizada (`.opencode/skills/django-app-creator/SKILL.md`). **Convenciones de mantenimiento documental:** tras crear la app, actualiza las secciones `## Estructura del Proyecto` en `AGENTS.md` y `README.md` con orden `manage.py` → apps (alfabético) → `core/`. Si es la primera app (distinta de `core/`): incluye comentario horizontal detallando todos los archivos (`__init__.py`, `admin.py`, `apps.py`, `models.py`, `views.py`, `tests.py`, `migrations/`, `templates/`, `urls.py`, `services.py`). Si ya existen otras apps: agrega solo el nombre de la carpeta sin comentario. Registrada en [AGENTS.md](AGENTS.md) bajo `## Skills`.
- **Comandos (.opencode/commands/)**: Comandos slash para flujos OpenSpec (`/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:archive`, `/opsx:sync`, `/opsx:update`) que implementan workflows con restricciones de planificación vs implementación [opsx-propose.md](.opencode/commands/opsx-propose.md).
- **Config global (opencode.json)**: Define agentes del sistema, MCPs habilitados y permisos por agente [opencode.json](C:/Users/anlle/.config/opencode/opencode.json).

### 3.2 Prompts clave
[PENDIENTE: No se han registrado prompts específicos ejecutados para construir el sistema en fuentes disponibles (AGENTS.md, .opencode, código). No se inventará contenido.]

### 3.3 Metodología de iteración
- **Desarrollo dirigido por especificaciones (Spec-Driven Development)**: Uso obligatorio de OpenSpec. Las specs (`openspec/specs/`) son fuente de verdad; los cambios pasan por artefactos estructurados (proposal, specs, design, tasks) antes de implementar [AGENTS.md](AGENTS.md).
- **Mantenimiento controlado de README**: El agente `readme-maintainer` se activa automáticamente tras cada creación o modificación de archivos, evalúa si el cambio aporta al registro de ingeniería, y si es relevante presenta todos los cambios propuestos de una sola vez (sección, texto, tipo: fusionar/reemplazar/agregar) esperando `ok` antes de editar [AGENTS.md](AGENTS.md), [readme-maintainer.md](.opencode/agent/readme-maintainer.md).
- **Verificación de UI en navegador real (directiva AGENTS.md)**: Antes de dar por hecha una vista, verificarla en navegador real vía Playwright MCP (levantar con `docker compose up --build` y navegar `http://localhost:8000/`). La referencia de configuración de MCPs vive en README.md sección 4 [AGENTS.md](AGENTS.md).
- **Arquitectura containerizada desde el inicio**: Setup Docker con multi-stage build, healthcheck, entrypoint con espera de DB y migraciones automáticas [Dockerfile](Dockerfile), [docker-entrypoint.sh](docker-entrypoint.sh), [AGENTS.md](AGENTS.md).
- **Institucionalización de decisiones arquitectónicas vía skills**: las decisiones arquitectónicas no quedan solo como directiva textual; se formalizan en skills ejecutables. Ejemplo: la adopción de **Service Layer** como patrón oficial (lógica de negocio en `services.py`, vistas delgadas `request → service → response`) se documentó en [AGENTS.md](AGENTS.md) y se hizo cumplir automáticamente mediante el skill `django-app-creator`, que genera `services.py` en cada app nueva [AGENTS.md](AGENTS.md), [django-app-creator SKILL.md](.opencode/skills/django-app-creator/SKILL.md). Así, la convención no depende de que el agente "se acuerde": el skill la garantiza estructuralmente.

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
