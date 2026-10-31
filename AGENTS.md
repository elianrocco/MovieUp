# AGENTS.md - MovieUp

## Stack Tecnológico
- **Backend:** Python con Django y LangChain
- **Frontend:** HTML (Living Standard), CSS3 (Snapshot 2023) y JavaScript (ES2025)
- **Base de datos:** MySQL LTS
- **Pasarela de pagos:** Mercado Pago (SDK Python)
- **Control de versiones:** Git + GitHub
- **Containerización:** Docker
- **Versiones exactas:** en `requirements.txt`, `Dockerfile` y `docker-compose.yml`

## Descripción del Proyecto
Sistema web para gestión y comercialización de entradas de cine. Permite a los usuarios comprar entradas, gestionar sus compras, y a los administradores gestionar películas, salas, funciones y ventas.

## Estructura del Proyecto

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

## Cómo Ejecutar
- Levantar todo: `docker compose up --build`
- Migraciones: se aplican automáticamente al arrancar (docker-entrypoint.sh)
- Migraciones manuales (tras crear una migración sin reiniciar): `docker compose exec web python movie_up/manage.py migrate`
- Crear superusuario: `docker compose exec web python movie_up/manage.py createsuperuser`
- Correr tests: `docker compose exec web python movie_up/manage.py test`
- App: http://localhost:8000/ (usar `localhost`, NO `0.0.0.0`)

## Arquitectura (MVT de Django)
- Patrón **Modelo-Vista-Template** de Django: los datos viven en `models.py`, la presentación en templates.
- **Service Layer**: la lógica de negocio se concentra en `services.py`. Las vistas (`views.py`) delegan la lógica a los services, manteniéndose delgadas (request → service → response).
- **Convención**: toda app debe incluir `services.py`. Usarlo siempre que sea posible para mantener consistencia entre las apps.
- El código se organiza en apps de Django (hoy: `movie_up`); se agregarán apps por dominio a medida que crezca.

## Convenciones
- Artefactos (código, identificadores, UI, comentarios): inglés
- Documentación (AGENTS.md, OpenSpec, skills, agents): español — en OpenSpec el texto va en español y las palabras clave de formato quedan en inglés (ver sección OpenSpec)

### Reglas de Git (obligatorio)
- **PROHIBIDO** hacer `git add`, `git commit`, `git push` o cualquier operación de staging/commit sin consultar primero al usuario.
- El agente SIEMPRE debe mostrar los cambios pendientes y esperar confirmación explícita antes de ejecutar cualquier operación de Git.
- Commits: conventional commits, sin atribución a IA.

## Variables de Entorno
Definidas en `.env` (nunca versionar):
- `SECRET_KEY` — clave secreta de Django
- `DEBUG` — modo depuración
- `DB_ROOT_PASSWORD`, `DB_NAME` — credenciales y nombre de MySQL
- `DB_LOCAL_PORT`, `DB_DOCKER_PORT` — puertos expuesto/interno de MySQL
- `DB_HOST`, `DB_PORT` — inyectadas por docker-compose al servicio web

## Testing
- Los tests de Django van en `<app>/tests.py` y se corren con `python movie_up/manage.py test`.
- (A definir: cobertura esperada y convenciones)

## Utilización de MCPs
### Verificación de UI
- Antes de dar por hecha una vista, verificarla en navegador real vía Playwright MCP (levantar con `docker compose up --build` y navegar `http://localhost:8000/`)
- La referencia de configuración de MCPs vive en README.md sección 4

### Consulta de Documentación
- Consultar docs actualizadas de librerías/APIs vía Context7 antes de asumir firmas o flags

## Autenticación y Roles
- Roles: Cliente y Administrador/Empleado
- Login local de Django; (planificado) Google OAuth
- (A definir: cómo se otorga el rol admin — `is_staff`)
    
## OpenSpec
- El proyecto usa **OpenSpec** para desarrollo dirigido por especificaciones (spec-driven development)
- Especificaciones de verdad en `openspec/specs/` (organizadas por dominio) y cambios propuestos en `openspec/changes/`
- Cada cambio incluye proposal.md (por qué), specs/ (qué cambia), design.md (cómo) y tasks.md (pasos)
- Flujo de trabajo: /opsx:explore -> /opsx:propose -> /opsx:apply -> /opsx:archive
- Comandos adicionales: /opsx:sync (sincronizar specs), /opsx:update (revisar el plan)
- Definir specs antes de implementar cualquier nueva funcionalidad

### Idioma de los artefactos OpenSpec
- El texto (propósito, requisitos, escenarios, decisiones, tareas) se escribe en español.
- Las palabras clave que OpenSpec parsea y valida se escriben en inglés, sin traducir ni cambiar mayúsculas:
  - Secciones: `## Purpose`, `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements`
  - Requisitos: `### Requirement: <nombre>`
  - Escenarios: `#### Scenario: <nombre>` (exactamente 4 `#`)
  - Pasos de escenario: `**WHEN**`, `**THEN**`
  - Normativos RFC 2119: `SHALL`, `MUST`, `SHOULD`, `MAY`
- Traducir estas palabras clave rompe el parseo: sin `## ADDED Requirements` el CLI reporta "No delta sections found" y el archive termina sin escribir nada en `openspec/specs/`.
- Verificación obligatoria antes de archivar un cambio: `openspec validate --specs --strict`

## Skills

### django-app-creator
- **Trigger:** `crea app [nombre]`
- **Ubicación:** `.opencode/skills/django-app-creator/SKILL.md`
- **Qué hace:**
  - Ejecuta `python manage.py startapp <nombre>` desde `movie_up/`
  - Registra la app en `INSTALLED_APPS` de `movie_up/core/settings.py`
  - Crea estructura de templates con namespacing: `templates/<nombre>/.gitkeep`
  - Crea `urls.py` con imports base (`from django.urls import path`, `from . import views`)

## Agentes

### readme-maintainer — activación automática
- **Cuándo se activa:** automáticamente después de crear o modificar cualquier archivo del proyecto. No requiere que el usuario lo pida.
- **Quién lo dispara:** el agente principal de la sesión lo invoca tras cada creación o edición de archivos (es un subagente de OpenCode).
- **Evaluación propia:** el agente lee el cambio realizado y el README, y decide si vale la pena registrarlo. Si no aporta al registro de ingeniería, responde "sin cambios" y no escribe nada.
- **Si hay información relevante:** presenta todos los cambios propuestos de una sola vez (sección destino, texto propuesto y tipo: fusionar / reemplazar / agregar) y espera `ok` antes de tocar README.md.
- **Permisos:** solo puede editar `README.md`.

## Casos de Uso

### Cliente
- Comprar entradas (selección de asientos + pago con Mercado Pago)
- Consultar y gestionar entradas desde la cuenta
- Reembolsar entradas
- Vincular cuenta de Google

### Administrador/Empleado
- Gestionar películas (CRUD)
- Gestionar funciones (CRUD)
- Gestionar salas (CRUD)
- Gestionar ventas (CRUD)
- Consultar métricas de ventas
- Validar entradas mediante código
