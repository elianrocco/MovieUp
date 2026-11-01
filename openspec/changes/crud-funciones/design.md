# Design

## Context

Ver `proposal.md` (Why). El estado actual: existen las apps `peliculas` (con `duracion_minutos`) y `salas` (con `distribucion` como JSON `{"version": n, "filas": [...]}` y `capacidad` derivada contando `A` + `R`), ambas con Service Layer, tests y CRUD verificado. `movie_up/core/settings.py` tiene `TIME_ZONE = 'America/Argentina/Buenos_Aires'` y `USE_TZ = True`. Los guards de `salas` y `peliculas` hacia funciones ya existen comentados con TODO. La spec `salas` ya contrata el formato de distribución y su versionado; esta change agrega la capacidad `funciones`.

Restricciones del alcance definido por el usuario: solo CRUD administrativo; sin CSS/JS nuevo salvo el reutilizado del detalle de salas; la desactivación automática por vencimiento, la compra de entradas y la validación de duración mínima de películas quedan para specs futuras.

## Goals / Non-Goals

**Goals:**

- Aplicar el contrato de la skill `crud-conventions` (Service Layer, validación en dos niveles, `ValueError` → formulario, `Http404` → 404, update parcial, derivados solo en el servicio).
- Snapshot independiente de distribución y derivados (`fin`, `disponibilidad`) recalculados solo en el servicio.
- Guard fiable de entradas compradas mediante el nuevo atributo `entradas_compradas`.

**Non-Goals:**

- Selección de asientos, entradas, compras, ventas y listado comercial (specs futuras).
- Mutación de `disponibilidad`/`distribución` por compra: la compra futura hará `A` → `R` y decrementará disponibilidad; fuera de este change.
- Corregir `Pelicula.duracion_minutos` para exigir ≥ 1 (spec futura de `movies`).

## Decisions

1. **App nueva `movie_up/funciones/`** con la estructura de `peliculas`/`salas`: `models.py`, `services.py`, `views.py`, `urls.py` con `app_name='funciones'`, `admin.py`, `templates/funciones/`, `tests.py`. Alternativa descartada: agregar a una app existente (rompe el dominio por app del proyecto).

2. **Modelo `Funcion`**: campos del esquema más `entradas_compradas = models.PositiveIntegerField(default=0)`. Se usa `PositiveIntegerField` porque admite el 0 inicial (rango 0–2147483647). `distribucion` y `disponibilidad` persisten; `disponibilidad` se deriva contando solo `A` y `fin` se deriva de `inicio` + duración. FKs con `on_delete=PROTECT` para reflejar el `NO ACTION` del esquema y asegurar "no borrar película/sala" a nivel de base. El formulario de funciones no expone `entradas_compradas` ni `fin`.

3. **Copia profunda de la distribución**: al crear, se asigna una copia (`copy.deepcopy` del dict) de `sala.distribucion`, conservando su `version` tal cual; se persiste serializada en la fila de la función. Alternativa descartada: referencia compartida (implicaría que editar la sala afecte a la función). El versionado de la copia ante futuras compras es contrato de la spec futura de compra.

4. **Zona horaria global**: `TIME_ZONE = 'America/Argentina/Buenos_Aires'` manteniendo `USE_TZ = True`. Los `datetime-local` del formulario se interpretan en la zona por defecto al hacerlos aware. No existe ningún `DateTimeField` en las apps actuales (solo `fecha_estreno`, `DateField`), por lo que el cambio no reinterpreta datos existentes.

5. **Solapamiento como intervalos `[inicio, fin)`**: consulta de mismo `sala_id` con `inicio < otra.fin AND fin > otra.inicio`, excluyendo el propio registro en update, sin filtrar por `funcion_activa` (las inactivas también bloquean). El contacto exacto `fin == inicio` queda fuera del predicado. La validación se ejecuta dentro de la misma transacción que el `save()`; se bloquea la fila de la sala (`select_for_update`) para cerrar la carrera entre dos creaciones simultáneas en la misma sala.

6. **Guard de entradas con contador, no con derivados**: `entradas_compradas > 0` bloquea update y delete. Se descartó `disponibilidad == count(A)` porque la compra futura decrementa ambos lados y la igualdad se preservaría. Invariante: al crear `entradas_compradas = 0` y `disponibilidad = count(A)`; como cada update queda bloqueado una vez que hay entradas, ningún recálculo del CRUD puede romper los derivados después de la primera venta.

7. **Activación vencida**: `funcion_activa` es un booleano en el formulario (elegido al crear). En update se aplica con la semántica de update parcial (`False` explícito sí aplica). Si `fin <= now(Buenos_Aires)`, se rechaza la transición de `false` a `true`; reenviar `true` cuando ya era el valor almacenado no se considera una nueva activación.

8. **Reutilización visual del detalle de salas**: la plantilla de detalle carga el filtro `celda_clase` del módulo `salas.templatetags.salas_tags` y los estáticos `salas/css/salas.css` y `salas/js/grid.js` en modo solo lectura (sin listeners de clic). Alternativa descartada: duplicar CSS/JS (diverge en cada fix).

9. **Menús de selección**: `<select>` poblados con `Pelicula.objects.all()` y `Sala.objects.all()`; ambos modelos ya exponen el nombre en `__str__`. El valor enviado es el `id`.

10. **Errores**: el servicio lanza `ValueError` con mensajes en español y la vista re-renderiza el formulario con `{'error': ...}`; `get_funcion` traduce `DoesNotExist` en `Http404`. Sin `except Exception`.

## Risks / Trade-offs

- [Película con `duracion_minutos = 0`] → `fin == inicio` y el intervalo queda vacío; no lo bloqueamos por decisión de alcance. Mitigación: registrar la dependencia de la spec futura de `movies` en tasks; resolverla antes o junto con la implementación.
- [Carrera entre dos creaciones en la misma sala] → mitigado con `select_for_update` sobre la fila de la sala dentro de la transacción de guardado.
- [Deriva del contador si un futuro flujo de compra olvida incrementarlo] → el guard se debilitaría. Mitigación: la spec futura de compra es dueña del incremento y del `A` → `R`; queda escrito como contrato en la propuesta.
- [Cambio global de `TIME_ZONE`] → altera la interpretación de fechas futuras en todas las apps. Mitigación: `USE_TZ = True` se mantiene, zona IANA y sin `DateTimeField` previos que reinterprear.
- [Snapshot y versionado] → la copia hereda la versión de la sala; si la sala sube versión después, ambas divergen. Es intencional (la versión viaja con la copia); incrementos por compra los define la spec futura.

## Migration Plan

1. Crear la app y su migración inicial (`funcion` con `entradas_compradas default 0`).
2. Cambiar `TIME_ZONE` en `settings.py`.
3. Incluir `funciones/` en `core/urls.py`.
4. Tests con `python movie_up/manage.py test peliculas salas funciones`.
5. Rollback: revertir `settings.py` y retirar la app (la migración es aditiva; no toca datos existentes).

## Open Questions

- La spec futura de compra definirá si cada `A` → `R` incrementa la `version` del snapshot de la función.
- El orden del listado administrativo se fija en implementación por inicio ascendente; no es comportamiento contractuado en la spec.
