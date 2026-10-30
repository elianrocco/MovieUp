---
name: django-app-creator
description: "Trigger: crea app [nombre]. Crea una nueva app Django con estructura completa (startapp, INSTALLED_APPS, templates, urls.py)."
license: Apache-2.0
metadata:
  author: "Elian"
  version: "1.0"
---

# django-app-creator

## Activation Contract

Cargar esta skill cuando el usuario escriba "crea app" seguido de un nombre de app. Por ejemplo: `crea app billing`.

## Hard Rules

- El comando `startapp` SIEMPRE se ejecuta desde `movie_up/` (donde vive `manage.py`).
- La app se registra en `INSTALLED_APPS` como string simple: `'<nombre>',` (sin prefijo de paquete).
- La carpeta de templates usa nombrespacing doble: `templates/<nombre_app>/` para evitar colisiones.
- El `.gitkeep` va completamente vacío.
- Los imports en `urls.py` son `from django.urls import path` y `from . import views` (NUNCA incluir `.py` en imports).
- Verificar que la app no exista ya antes de crearla.
- Después de crear la app, SIEMPRE actualizar la sección `## Estructura del Proyecto` en `AGENTS.md` y `README.md`.
- Orden del árbol en `movie_up/`: `manage.py` → apps (alfabético) → `core/`.
- Si es la primera app (distinta de `core/`): incluir comentario horizontal con TODOS los archivos.
- Si ya existen otras apps: agregar solo el nombre de la carpeta (sin comentario).

## Execution Steps

1. **Validar nombre**: verificar que el nombre sea válido (snake_case, sin caracteres especiales, no exista ya en `movie_up/`).
2. **Crear app**: ejecutar `python manage.py startapp <nombre>` desde `movie_up/`.
3. **Registrar en settings**: editar `movie_up/core/settings.py`, agregar `'<nombre>',` en la lista `INSTALLED_APPS` después de las apps de Django.
4. **Crear estructura de templates**: crear directorio `movie_up/<nombre>/templates/<nombre>/` y colocar `.gitkeep` vacío dentro.
5. **Crear urls.py**: crear `movie_up/<nombre>/urls.py` con el contenido base (ver Output Contract).
6. **Actualizar AGENTS.md y README.md**: editar la sección `## Estructura del Proyecto` en ambos archivos para incluir la nueva app en el árbol de `movie_up/`.
   - Orden: `manage.py` → apps (alfabético) → `core/`.
   - Si es la primera app (no hay otras apps además de `core/`): agregar línea `├── <nombre>/              # __init__.py, admin.py, apps.py, models.py, views.py, tests.py, migrations/, templates/, urls.py`.
   - Si ya existen otras apps: agregar línea `├── <nombre>/` (sin comentario).
   - Ajustar conectores del árbol: cambiar `└── core/` a `├── core/` si había `core/` como último elemento, y mantener `└──` para el último elemento después de agregar la app.
7. **Confirmar**: mostrar al usuario los archivos creados, el cambio en settings.py, y la actualización del árbol en AGENTS.md/README.md.

## Output Contract

Después de crear la app, reportar:
- Ruta de la app creada
- Línea agregada en `INSTALLED_APPS`
- Archivos/directorios creados (templates con .gitkeep, urls.py)
- Cambio realizado en el árbol de `AGENTS.md` y `README.md` (sección `movie_up/`)
- Estructura final de la app

## Ejemplo

Usuario: `crea app billing`

**Escenario 1: Primera app creada** (no hay otras apps además de `core/`)

Árbol en AGENTS.md/README.md después de crear `billing/`:
```
├── movie_up/
│   ├── manage.py
│   ├── billing/              # __init__.py, admin.py, apps.py, models.py, views.py, tests.py, migrations/, templates/, urls.py
│   └── core/
│       ├── __init__.py
│       ├── asgi.py
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
```

**Escenario 2: Segunda app creada** (ya existe `billing/`)

Usuario: `crea app payments`

Árbol en AGENTS.md/README.md después de crear `payments/`:
```
├── movie_up/
│   ├── manage.py
│   ├── billing/              # __init__.py, admin.py, apps.py, models.py, views.py, tests.py, migrations/, templates/, urls.py
│   ├── payments/
│   └── core/
│       ├── __init__.py
│       ├── asgi.py
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
```

`urls.py` contiene:
```python
from django.urls import path
from . import views

urlpatterns = [
]
```

`INSTALLED_APPS` ahora incluye `'billing',` y `'payments',`.
