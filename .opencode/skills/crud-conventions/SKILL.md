---
name: crud-conventions
description: "Trigger: planificar spec CRUD, planificar la spec de un CRUD, nueva spec CRUD, empezar CRUD. Aplica las convenciones genéricas de MovieUp al diseñar la spec de cualquier CRUD."
license: Apache-2.0
metadata:
  author: "Elian"
  version: "1.0"
---

# crud-conventions

## Activation Contract

Cargar esta skill cuando el usuario pida empezar a planificar la spec de un CRUD en OpenSpec (p. ej. "planifiquemos la spec del CRUD de funciones"). Aplicar sus reglas al redactar proposal y specs. No cargarla para implementar o corregir un CRUD ya especificado: ahí manda su spec.

## Hard Rules

- Toda operación (list, get, create, update, delete) vive en `services.py`; las vistas delegan y quedan delgadas (request → servicio → respuesta).
- El servidor SIEMPRE revalida todo. `required`, `maxlength`, `min`/`max` en HTML son solo UX; el contrato de validación vive en el servicio.
- Contrato de errores: el servicio lanza `ValueError` con mensaje en español apto para el usuario y la vista lo captura re-renderizando el formulario con el error (sin 500). Registro inexistente: `Http404` desde `DoesNotExist`, sin capturarlo en la vista. Capturas amplias (`except Exception`) prohibidas.
- Update parcial: campo ausente o vacío = no modificar; valor explícito (incluso `False`, `0` o estructura completa de reemplazo) SÍ se aplica. Nunca decidir omisión por truthiness.
- Unicidad: validada en el servicio antes del `save()`, excluyendo el propio registro en update.
- Todo dato derivado se calcula en el servicio; el formulario nunca lo dicta.
- Normalizar entradas (trim, mayúsculas) antes de unicidad, igualdad o detección de cambios.
- Guard que depende de una app que todavía no existe: bloque condicional comentado con TODO, nunca un import roto.
- Cada operación se cubre con tests en `tests.py` (servicio y flujo de vista).

## Decision Gates

| Pregunta al planificar | Acción |
|---|---|
| ¿Cuáles son los campos y validaciones del dominio? | Definirlos en la spec; no copiarlos de otras apps. |
| ¿Hay dependencias entre apps? | Agregar el guard como requisito; si la app aún no existe, marcarlo condicional con TODO. |
| ¿Un valor se deriva de otros? | Exigirlo calculado en el servicio y ausente del formulario. |
| ¿La vista es visible en navegador? | Exigir verificación con navegador real antes de darla por hecha. |

## Execution Steps

1. Revisar el alcance del CRUD y listar sus operaciones (mínimo: listado, detalle, creación, actualización, eliminación).
2. Redactar cada requisito con las reglas anteriores implícitas; dejar explícito en la spec el contrato de errores y el comportamiento del update.
3. Separar lo que varía por dominio (campos, guards, unicidad) de lo fijo (convenciones de esta skill).
4. Correr `openspec validate --specs --strict` y reportar el resultado.

## Output Contract

Reportar: operaciones cubiertas, validaciones de dominio detectadas, guards pendientes por app inexistente, decisiones de update no triviales y resultado de `openspec validate --specs --strict`.

## References

- `movie_up/peliculas/services.py` — implementación de referencia con archivos adjuntos.
- `movie_up/salas/services.py` — implementación de referencia con validación compleja y datos derivados.
- `.opencode/skills/django-app-creator/SKILL.md` — creación del esqueleto de la app.
