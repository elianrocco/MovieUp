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
- `core/` — configuración del proyecto Django (settings, urls, wsgi/asgi)
- `movieUp/` — app Django principal (models, views, admin, migrations)
- `manage.py` — utilidad de línea de comandos de Django
- `openspec/` — especificaciones (`specs/`) y cambios (`changes/`)
- `requirements.txt` — dependencias Python (fuente de verdad de versiones)
- `Dockerfile`, `docker-compose.yml`, `docker-entrypoint.sh` — entorno Docker
- `.env` — variables de entorno (NO versionar)

## Cómo Ejecutar
- Levantar todo: `docker compose up --build`
- Migraciones: se aplican automáticamente al arrancar (docker-entrypoint.sh)
- Migraciones manuales (tras crear una migración sin reiniciar): `docker compose exec web python manage.py migrate`
- Crear superusuario: `docker compose exec web python manage.py createsuperuser`
- Correr tests: `docker compose exec web python manage.py test`
- App: http://localhost:8000/ (usar `localhost`, NO `0.0.0.0`)

## Arquitectura (MVT de Django)
- Patrón **Modelo-Vista-Template** de Django: los datos viven en `models.py`, la lógica en `views.py` y la presentación en templates.
- El código se organiza en apps de Django (hoy: `movieUp`); se agregarán apps por dominio a medida que crezca.

## Convenciones
- Artefactos (código, identificadores, UI, comentarios): inglés
- Documentación (AGENTS.md, OpenSpec): español
- Commits: conventional commits, sin atribución a IA

## Variables de Entorno
Definidas en `.env` (nunca versionar):
- `SECRET_KEY` — clave secreta de Django
- `DEBUG` — modo depuración
- `DB_ROOT_PASSWORD`, `DB_NAME` — credenciales y nombre de MySQL
- `DB_LOCAL_PORT`, `DB_DOCKER_PORT` — puertos expuesto/interno de MySQL
- `DB_HOST`, `DB_PORT` — inyectadas por docker-compose al servicio web

## Testing
- Los tests de Django van en `<app>/tests.py` y se corren con `python manage.py test`.
- (A definir: cobertura esperada y convenciones)

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

## Registro de Cambios en AGENTS.md
- Toda edición de este archivo se registra en `LogsMD.txt` (leer `.opencode\skills\log-agents-changes\SKILL.md`).

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
