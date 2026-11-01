# Proposal

## Why

MovieUp ya gestiona películas y salas, pero no existe la relación que une una película con una sala en un horario. Sin esa relación no hay programa de funciones que administrar ni futuro objeto de venta de entradas. Este change agrega el CRUD administrativo de funciones, dejando la parte comercial para specs posteriores.

## What Changes

- Nueva app Django `funciones` con las cinco operaciones CRUD (listar, detalle, crear, actualizar, eliminar), con la lógica de negocio en `services.py` y vistas delgadas, siguiendo la convención del proyecto.
- Campos de la función: estado `funcion_activa` (elegido por el administrador al crear), `inicio`, `fin` derivado, `idioma` (texto libre hasta 45), `subtitulada`, `distribucion` (copia de la sala), `disponibilidad` derivada, `precio_entrada`, película y sala elegidas por menú desplegable que envía el id, y `entradas_compradas` de solo sistema (inicia en 0, no editable desde el formulario).
- Validaciones de negocio: `inicio` presente o futuro, `fin` calculado a partir de `inicio` más la duración de la película asociada, rechazo de cualquier solapamiento con otra función de la misma sala (activa o inactiva, con encuentro exacto permitido), `precio_entrada >= 0` e idioma obligatorio.
- Distribución: copia completa (no referencia ni puntero) de la distribución de la sala al crear; se reemplaza por una copia nueva si cambia la sala en la actualización. La disponibilidad se deriva contando solo las celdas `A` de la distribución de la función.
- Bloqueos: actualización y eliminación mientras `entradas_compradas > 0` (cada entrada comprada lo incrementa en 1), y activación de una función cuyo `fin` ya pasó.
- Detalle administrativo con la distribución en cuadrícula de solo lectura, reutilizando el diseño del detalle de salas (CSS y JavaScript autorizados para esta spec).
- Cambio global de configuración: `TIME_ZONE` de `movie_up/core/settings.py` pasa a `America/Argentina/Buenos_Aires`, manteniendo `USE_TZ = True`.
- Fuera de alcance: selección de asientos, generación de entradas, compras y ventas, el listado comercial que ven los clientes, la desactivación automática de `funcion_activa` al vencer `fin` (spec futura del listado comercial) y la validación de duración mínima en películas (spec futura de `movies`).

## Capabilities

### New Capabilities

- `funciones`: CRUD administrativo de programación de funciones: alta con copia de la distribución de la sala, consulta con listado resumido y detalle, actualización con recálculo de atributos derivados, y eliminación, con bloqueos por entradas compradas y por intervalo de horario.

### Modified Capabilities

- Ninguna. Los guards condicionales de `movies` (borrado con funciones asociadas) y `salas` (operaciones sobre salas en uso) ya están redactados en sus specs como comportamiento futuro y no cambian. La validación de `duracion_minutos >= 1` queda para una futura spec de `movies`.

## Impact

- Código nuevo: app `movie_up/funciones/` (models, services, views, urls, admin, templates, templatetags o reutilización del filtro `celda_clase`, tests) y su inclusión en `movie_up/core/urls.py`.
- Configuración: `movie_up/core/settings.py` (`TIME_ZONE`), que afecta la interpretación y visualización de fechas y horas en todas las apps existentes.
- Dependencias de datos: `pelicula.duracion_minutos` (determina `fin`) y `sala.distribucion` (origen de la copia).
- Contrato para specs futuras: `entradas_compradas` será incrementado por la compra de entradas; el listado comercial desactivará funciones vencidas.
- Documentación: árboles de estructura en `AGENTS.md` y `README.md` al crear la app, y registro en los comandos de tests.
