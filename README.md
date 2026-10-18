# MovieUp - Log de Ingeniería

## 1. Visión general y arquitectura del sistema

**Fuente:** [AGENTS.md](AGENTS.md#L1-L14), [core/settings.py](core/settings.py), [core/urls.py](core/urls.py), [movie_up/](movie_up/), [requirements.txt](requirements.txt), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)

### Propósito del proyecto
MovieUp es un sistema web para la gestión y comercialización de entradas de cine. Permite a los usuarios comprar entradas, gestionar sus compras, y a los administradores gestionar películas, salas, funciones y ventas. [AGENTS.md:12-13](AGENTS.md#L12-L13)

### Stack tecnológico
- **Backend:** Python 3.14.7 con Django 6.1.1 y LangChain 1.4.0 [AGENTS.md:3-4](AGENTS.md#L3-L4), [requirements.txt](requirements.txt), [Dockerfile:5,33](Dockerfile#L5)
- **Frontend:** HTML (Living Standard), CSS3 (Snapshot 2023) y JavaScript (ES2025) [AGENTS.md:5](AGENTS.md#L5)
- **Base de datos:** MySQL 9.7.2 LTS [AGENTS.md:6](AGENTS.md#L6), [docker-compose.yml:3](docker-compose.yml#L3), [core/settings.py:80-89](core/settings.py#L80-L89)
- **Pasarela de pagos:** Mercado Pago SDK Python 3.5.0 [AGENTS.md:7](AGENTS.md#L7), [requirements.txt:4](requirements.txt#L4)
- **Control de versiones:** Git + GitHub [AGENTS.md:8](AGENTS.md#L8)
- **Containerización:** Docker 29.8.0 [AGENTS.md:9](AGENTS.md#L9), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)
- **Versiones exactas:** definidas en `requirements.txt`, `Dockerfile` y `docker-compose.yml` [AGENTS.md:10](AGENTS.md#L10)

### Arquitectura (Patrón MVT de Django)
El proyecto sigue el patrón **Modelo-Vista-Template (MVT)** de Django como arquitectura base [AGENTS.md:32-34](AGENTS.md#L32-L34), [LogsMD.txt:23-24,49-52](LogsMD.txt#L23-L52).

- **Modelo (Model):** Define la estructura de datos y la persistencia en MySQL mediante `models.py`. Actualmente sin modelos definidos - estado inicial del proyecto [movie_up/models.py:1-3](movie_up/models.py#L1-L3).
- **Vista (View):** Contiene la lógica de negocio en `views.py`, enrutada desde `urls.py` [LogsMD.txt:50](LogsMD.txt#L50). Actualmente sin vistas implementadas [movie_up/views.py:1-3](movie_up/views.py#L1-L3).
- **Template:** Presentación mediante el motor de plantillas de Django con HTML/CSS/JS [LogsMD.txt:51](LogsMD.txt#L51).
- **Flujo de petición:** `urls.py` → `views.py` → `models.py` → `templates/` [LogsMD.txt:52](LogsMD.txt#L52).

### Estructura del proyecto
- `core/` — configuración del proyecto Django (settings, urls, wsgi/asgi) [AGENTS.md:16](AGENTS.md#L16), [core/](core/)
- `movie_up/` — app Django principal (models, views, admin, migrations) [AGENTS.md:17](AGENTS.md#L17), [movie_up/](movie_up/)
- `manage.py` — utilidad de línea de comandos de Django [AGENTS.md:18](AGENTS.md#L18)
- `openspec/` — especificaciones (`specs/`) y cambios (`changes/`) para desarrollo dirigido por especificaciones [AGENTS.md:19](AGENTS.md#L19), [openspec/](openspec/)
- `requirements.txt` — dependencias Python (fuente de verdad de versiones) [AGENTS.md:20](AGENTS.md#L20)
- `Dockerfile`, `docker-compose.yml`, `docker-entrypoint.sh` — entorno Docker [AGENTS.md:21](AGENTS.md#L21)
- `.env` — variables de entorno (NO versionar) [AGENTS.md:22](AGENTS.md#L22)
- `.opencode/` — configuración de agentes, comandos, skills y MCP [opencode.json](C:/Users/anlle/.config/opencode/opencode.json), [.opencode/](.opencode/)
- `LogsMD.txt` — registro de cambios a AGENTS.md [AGENTS.md:76](AGENTS.md#L76)

### Configuración y despliegue con Docker
**Fuentes:** [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), [docker-entrypoint.sh](docker-entrypoint.sh), [core/settings.py:80-89](core/settings.py#L80-L89)

- **Multi-stage build** (builder/runtime): el builder compila dependencias como wheels usando `python:3.14.7-slim-trixie`, el runtime instala únicamente wheels precompilados con usuario no privilegiado (`appuser`) [Dockerfile:3-6,31-34,49-71](Dockerfile#L3-L71)
- **Servicios**: `db` (MySQL 9.7.2) y `web` (Django app) [docker-compose.yml:1-26](docker-compose.yml#L1-L26)
- **Variables de entorno**: inyectadas via `.env` y `env_file`; `DB_HOST=db`, `DB_PORT` se sobreescriben para el contenedor web [docker-compose.yml:4-24](docker-compose.yml#L4-L24)
- **Punto de entrada**: `docker-entrypoint.sh` espera a que la base de datos responda vía TCP, luego ejecuta `python manage.py migrate --noinput` automáticamente [docker-entrypoint.sh:1-37](docker-entrypoint.sh#L1-L37), [AGENTS.md:26](AGENTS.md#L26)
- **Healthcheck**: verifica respuesta HTTP en puerto 8000 cada 30s [Dockerfile:77-78](Dockerfile#L77-L78)

**Cómo ejecutar (según AGENTS.md):**
- Levantar todo: `docker compose up --build` [AGENTS.md:25](AGENTS.md#L25)
- Migraciones: se aplican automáticamente al arrancar (docker-entrypoint.sh) [AGENTS.md:26](AGENTS.md#L26)
- Migraciones manuales: `docker compose exec web python manage.py migrate` [AGENTS.md:27](AGENTS.md#L27)
- Crear superusuario: `docker compose exec web python manage.py createsuperuser` [AGENTS.md:28](AGENTS.md#L28)
- Correr tests: `docker compose exec web python manage.py test` [AGENTS.md:29](AGENTS.md#L29)
- App: http://localhost:8000/ (usar `localhost`, NO `0.0.0.0`) [AGENTS.md:30](AGENTS.md#L30)

### Configuración Django
- **DEBUG/SECRET_KEY** desde variables de entorno [core/settings.py:24,27](core/settings.py#L24-L27)
- **ALLOWED_HOSTS** incluye `localhost`, `0.0.0.0`, `127.0.0.1` [core/settings.py:29-33](core/settings.py#L29-L33)
- **Base de datos MySQL** configurada con credenciales desde `.env` [core/settings.py:80-89](core/settings.py#L80-L89)
- **Apps instaladas:** `django.contrib.*` únicamente (sin `movie_up` aún registrada) [core/settings.py:38-46](core/settings.py#L38-L46)
- **EMAIL_BACKEND:** `console.EmailBackend` (configuración para desarrollo) [core/settings.py:132-136](core/settings.py#L132-L136)

### Convenciones
- Artefactos (código, identificadores, UI, comentarios): inglés [AGENTS.md:37](AGENTS.md#L37)
- Documentación (AGENTS.md, OpenSpec): español [AGENTS.md:38](AGENTS.md#L38)
- Commits: conventional commits, sin atribución a IA [AGENTS.md:39](AGENTS.md#L39)
- Tests: en `<app>/tests.py`, ejecutados con `python manage.py test` [AGENTS.md:50](AGENTS.md#L50)

### Autenticación y roles
- Roles: Cliente y Administrador/Empleado [AGENTS.md:54](AGENTS.md#L54)
- Login local de Django; (planificado) Google OAuth [AGENTS.md:55](AGENTS.md#L55)
- (A definir): cómo se otorga el rol admin — `is_staff` [AGENTS.md:56](AGENTS.md#L56)

### Desarrollo dirigido por especificaciones (OpenSpec)
**Fuentes:** [AGENTS.md:58-64](AGENTS.md#L58-L64), [openspec/](openspec/), [openspec/config.yaml](openspec/config.yaml), [opsx-propose.md](.opencode/commands/opsx-propose.md)

- El proyecto usa **OpenSpec** para desarrollo dirigido por especificaciones (spec-driven development) [AGENTS.md:59](AGENTS.md#L59)
- Especificaciones de verdad en `openspec/specs/` (organizadas por dominio) y cambios propuestos en `openspec/changes/` [AGENTS.md:60](AGENTS.md#L60)
- Cada cambio incluye `proposal.md` (por qué), `specs/` (qué cambia), `design.md` (cómo) y `tasks.md` (pasos) [AGENTS.md:61](AGENTS.md#L61)
- Flujo de trabajo: `/opsx:explore` → `/opsx:propose` → `/opsx:apply` → `/opsx:archive` [AGENTS.md:62](AGENTS.md#L62)
- Comandos adicionales: `/opsx:sync` (sincronizar specs), `/opsx:update` (revisar el plan) [AGENTS.md:63](AGENTS.md#L63)
- Definir specs antes de implementar cualquier nueva funcionalidad [AGENTS.md:64](AGENTS.md#L64)
- Estado actual: `openspec/specs/` y `openspec/changes/archive/` contienen `.gitkeep` (sin specs/cambios activos) [openspec/specs/.gitkeep](openspec/specs/.gitkeep), [openspec/changes/archive/.gitkeep](openspec/changes/archive/.gitkeep)


## 2. Casos de uso (10 canónicos)

**Fuente:** [AGENTS.md:78-92](AGENTS.md#L78-L92) - Mirror exacto de AGENTS.md. No se agregan, eliminan ni reformulan casos de uso.

### Cliente (4 casos de uso)
1. Comprar entradas (selección de asientos + pago con Mercado Pago) [AGENTS.md:81](AGENTS.md#L81)
2. Consultar y gestionar entradas desde la cuenta [AGENTS.md:82](AGENTS.md#L82)
3. Reembolsar entradas [AGENTS.md:83](AGENTS.md#L83)
4. Vincular cuenta de Google [AGENTS.md:84](AGENTS.md#L84)

### Administrador/Empleado (6 casos de uso)
5. Gestionar películas (CRUD) [AGENTS.md:87](AGENTS.md#L87)
6. Gestionar funciones (CRUD) [AGENTS.md:88](AGENTS.md#L88)
7. Gestionar salas (CRUD) [AGENTS.md:89](AGENTS.md#L89)
8. Gestionar ventas (CRUD) [AGENTS.md:90](AGENTS.md#L90)
9. Consultar métricas de ventas [AGENTS.md:91](AGENTS.md#L91)
10. Validar entradas mediante código [AGENTS.md:92](AGENTS.md#L92)


## 3. Justificación de Ingeniería con IA

**Fuente:** [AGENTS.md](AGENTS.md), [readme-maintainer.md](.opencode/agent/readme-maintainer.md), [log-agents-changes/SKILL.md](.opencode/skills/log-agents-changes/SKILL.md), [opencode.json](C:/Users/anlle/.config/opencode/opencode.json), [.opencode/agent/](.opencode/agent/), [.opencode/skills/](.opencode/skills/), [.opencode/commands/](.opencode/commands/)

### 3.1 Estructura de instrucciones del sistema
La directiva de IA está organizada de forma modular con las siguientes capas:

- **AGENTS.md (raíz)**: Define el contexto del proyecto, stack, arquitectura, convenciones, casos de uso, flujo de trabajo OpenSpec, y agentes definidos. Actúa como fuente de verdad para el proyecto [AGENTS.md](AGENTS.md).
- **Agentes subagentes (.opencode/agent/)**: Definen comportamientos especializados. Específicamente `readme-maintainer.md` define un agente con permisos restrictivos (solo puede editar `README.md`, otros permisos requieren confirmación) y un protocolo estricto de edición con puerta de confirmación `ok` [readme-maintainer.md:1-73](.opencode/agent/readme-maintainer.md#L1-L73).
- **Skills (.opencode/skills/)**: Capacidades reutilizables activables por disparadores. Por ejemplo `log-agents-changes` obliga a registrar cualquier modificación a AGENTS.md en `LogsMD.txt` con número de modificación, fecha, línea nueva y anterior [log-agents-changes/SKILL.md:1-49](.opencode/skills/log-agents-changes/SKILL.md#L1-L49).
- **Comandos (.opencode/commands/)**: Comandos slash para flujos OpenSpec (`/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:archive`, `/opsx:sync`, `/opsx:update`) que implementan workflows con restricciones de planificación vs implementación [opsx-propose.md:5-10](.opencode/commands/opsx-propose.md#L5-L10).
- **Config global (opencode.json)**: Define agentes del sistema, MCPs habilitados y permisos por agente [opencode.json](C:/Users/anlle/.config/opencode/opencode.json).

### 3.2 Prompts clave
[PENDIENTE: No se han registrado prompts específicos ejecutados para construir el sistema en fuentes disponibles (AGENTS.md, LogsMD.txt, .opencode, código). No se inventará contenido.]

### 3.3 Metodología de iteración
- **Desarrollo dirigido por especificaciones (Spec-Driven Development)**: Uso obligatorio de OpenSpec. Las specs (`openspec/specs/`) son fuente de verdad; los cambios pasan por artefactos estructurados (proposal, specs, design, tasks) antes de implementar [AGENTS.md:58-64](AGENTS.md#L58-L64).
- **Registro trazable de cambios**: Toda edición de AGENTS.md se registra en `LogsMD.txt` con header de modificación (M[n], fecha DD/MM/YYYY), número de línea, nuevo contenido y contenido anterior [AGENTS.md:76](AGENTS.md#L76), [log-agents-changes/SKILL.md:12-31](.opencode/skills/log-agents-changes/SKILL.md#L12-L31). Se observan 4 modificaciones registradas (M1-M4) en [LogsMD.txt](LogsMD.txt).
- **Mantenimiento controlado de README**: El agente `readme-maintainer` se activa automáticamente tras cada creación o modificación de archivos, evalúa si el cambio aporta al registro de ingeniería, y si es relevante presenta todos los cambios propuestos de una sola vez (sección, texto, tipo: fusionar/reemplazar/agregar) esperando `ok` antes de editar [AGENTS.md:68-74](AGENTS.md#L68-L74), [readme-maintainer.md:62-67](.opencode/agent/readme-maintainer.md#L62-L67).
- **Arquitectura containerizada desde el inicio**: Setup Docker con multi-stage build, healthcheck, entrypoint con espera de DB y migraciones automáticas [Dockerfile](Dockerfile), [docker-entrypoint.sh](docker-entrypoint.sh), [AGENTS.md:26](AGENTS.md#L26).

### 3.4 Bucles de autocorrección automatizados
[PENDIENTE: No se identifican bucles de autocorrección automatizados explícitos (loops de auto-corrección con ejecución iterativa) documentados en las fuentes consultadas (AGENTS.md, skills, commands, agent configs). Solo se identifican mecanismos de control/validación (registro de cambios, puerta de confirmación para README, workflow OpenSpec estructurado).]

### 3.5 Estructura de instrucciones (resumen)
La estructura sigue un enfoque jerárquico y restrictivo: instrucciones a nivel proyecto (AGENTS.md), políticas de agentes (agent/*.md con permisos), habilidades especializadas (skills con triggers), comandos operativos (commands con workflows), y configuración de runtime (opencode.json con MCPs y permisos). Esto permite dirigir la construcción con IA de forma controlada, trazable y con puntos de confirmación explícitos. [Fuentes: AGENTS.md, .opencode/*, opencode.json]


## 4. Configuración de servidores MCP

**Fuente:** [readme-maintainer.md:34-38](.opencode/agent/readme-maintainer.md#L34-L38), [opencode.json:168-184](C:/Users/anlle/.config/opencode/opencode.json#L168-L184)

Según las especificaciones del agente `readme-maintainer` y la configuración real en OpenCode:

### 4.1 context7
- **Tipo:** remoto [opencode.json:171](C:/Users/anlle/.config/opencode/opencode.json#L171)
- **URL:** `https://mcp.context7.com/mcp` [opencode.json:172](C:/Users/anlle/.config/opencode/opencode.json#L172), [readme-maintainer.md:35](.opencode/agent/readme-maintainer.md#L35)
- **Propósito:** Servidor MCP remoto para acceder a documentación actualizada de bibliotecas/frameworks/SDKs/APIs/CLIs/servicios cloud (Context7). Habilitado en la configuración global de OpenCode [opencode.json:169-173](C:/Users/anlle/.config/opencode/opencode.json#L169-L173).
- **Rol en desarrollo:** Facilita consulta de documentación actualizada durante el desarrollo (instrucciones de setup, sintaxis API, migraciones, debugging específico de librerías) [contexto de opencode.json/mcp].

### 4.2 engram
- **Tipo:** local [opencode.json:180](C:/Users/anlle/.config/opencode/opencode.json#L180)
- **Comando:** `C:\Users\anlle\AppData\Local\engram\bin\engram.exe mcp --tools=agent` [opencode.json:175-179](C:/Users/anlle/.config/opencode/opencode.json#L175-L179), [readme-maintainer.md:36](.opencode/agent/readme-maintainer.md#L36)
- **Propósito:** Servidor MCP local para memoria persistente (Engram). Habilitado con tools=agent [opencode.json:178](C:/Users/anlle/.config/opencode/opencode.json#L178).
- **Rol en desarrollo:** Proporciona memoria persistente entre sesiones para guardar decisiones, descubrimientos, bugs, convenciones y contexto del proyecto [según instrucciones de Engram en el sistema]. 

**Nota de configuración:** No se copian valores secretos. Solo se describe forma/configuración y rol, tal como se indica en [readme-maintainer.md:30-31,37](.opencode/agent/readme-maintainer.md#L30-L31,L37). 


## 5. Pending inputs
[PENDIENTE: No existen fuentes para determinar prompts específicos clave ejecutados durante la construcción del sistema, ni bucles de autocorrección automatizados explícitos con detalles de implementación. Estos elementos requerirían logs de ejecución/iteración con IA que no están presentes en AGENTS.md, LogsMD.txt, .opencode, código o configuración MCP.]
