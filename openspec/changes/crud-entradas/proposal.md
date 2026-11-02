# Proposal

## Why

El sistema ya vende funciones y guarda distribuciones de asientos, pero todavía no existe el registro de **quién compró qué asiento**: no hay dónde persistir la entrada, ni con qué código se valida en la puerta, ni cómo se devuelve un asiento al cancelar. Sin el agregado `Entrada` los casos de cliente "Consultar y gestionar entradas desde la cuenta" y "Reembolsar entradas" no tienen dónde operar, y los guards de `cuentas` siguen sin poderse implementar porque no existe la relación que consultar.

## What Changes

- Nuevo modelo `Entrada` en la app `entradas` con los campos mínimos del esquema entregado: `funcion` (FK), `cuenta` (FK), `codigo` único, `l_fila`, `n_asiento` y `activa`. **Sin precio, sin timestamps ni ningún otro dato**, por decisión explícita de alcance; el precio vive en `Funcion.precio_entrada` y queda congelado por los guards de edición de `funciones`.
- **Creación interna sin interfaz**: no hay vista ni formulario de alta. La compra (fuera de esta spec) invoca un servicio que recibe `funcion`, `cuenta` de la sesión actual, `n_asiento` y `l_fila` **tal como los calcula la compra**, sin derivarlos; `activa` nace en `True` y el código se genera de forma compleja y única dentro del servicio.
- Contrato de fila: **`l_fila` es la etiqueta alfabética derivada de la posición** (fila 1 → `A`, 2 → `B`, … 27 → `AA`, base-26). La distribución de `Funcion` es una lista de cadenas sin etiquetas, así que esta convención es la que permite localizar la celda a modificar; se comparte con el proceso de compra.
- Al crear, la función se actualiza en la misma transacción: `entradas_compradas += 1`, `disponibilidad -= 1` y la celda correspondiente pasa de `A` a `R` en `distribucion`. La celda debe ser `A`: `R` (ya reservada) y `P` (pasillo) se rechazan, y una unicidad compuesta `(funcion, l_fila, n_asiento)` impide vender el mismo asiento dos veces.
- **La entrada no se edita jamás**: no existe servicio, endpoint ni formulario de actualización. Este es el único "CRUD" del proyecto sin operación de update, y es una regla de dominio, no una omisión.
- Listado propio: cada cuenta ve solo sus entradas, con datos resumidos (película, sala, inicio, asiento).
- Detalle con control de propiedad: información de cartelera y de sala, **sin IDs renderizados, sin distribuciones ni datos técnicos**; cuenta distinta a la de la sesión responde `404` para no permitir enumeración de IDs ajenos.
- Validación en puerta: vista que recibe un `codigo`, lo busca entre las entradas activas, informa si existe o no y, si existe, pasa `activa` a `False` de forma atómica.
- Eliminación **solo automática, nunca manual**: el servicio acepta dos motivos. `reembolso` borra la entrada y revierte la función (`entradas_compradas -= 1`, `disponibilidad += 1`, celda `R` → `A`); `finalizacion` borra sin tocar la función. No hay vista de borrado ni acción de admin, y un motivo distinto a esos dos se rechaza.
- **Método de reembolso acotado**: solo elimina la entrada, actualiza la función y ejecuta las validaciones correspondientes. **La devolución de dinero queda para una spec futura.**
- Los **disparadores** de ambas eliminaciones (flujo de reembolso del cliente y limpieza tras `Funcion.fin`) también quedan para specs futuras; este change entrega y prueba el servicio completo que ambos van a invocar.
- Se activa el guard pendiente de `cuentas`: al existir la relación, el borrado de cuentas con entradas asociadas pasa de `TODO` a validación real.

### Fuera de alcance

- El proceso de compra (selección de asiento, pago con Mercado Pago, llamada al servicio).
- Devolución de dinero en el reembolso.
- Disparadores automáticos: limpieza de entradas vencidas y flujo completo de reembolso.
- Impedir que una función ya finalizada pueda editarse (spec futura en `funciones`).

## Capabilities

### New Capabilities

- `entradas`: ciclo de vida de una entrada — creación interna con efectos sobre la función, etiqueta de fila, listado y detalle por cuenta con control de propiedad, validación en puerta por código y eliminación automática por reembolso o por finalización.

### Modified Capabilities

- `cuentas`: el requisito "Borrado bloqueado por entradas asociadas" deja de condicionar la validación a un `TODO` "mientras la app `entrada` no exista". Este change crea la relación, así que el guard queda activo y esa condición deja de ser cierta.

## Impact

- `movie_up/entradas/models.py`: modelo `Entrada`, `db_table = 'entrada'`, `PROTECT` en ambas FK e índice único compuesto `(funcion, l_fila, n_asiento)`.
- `movie_up/entradas/migrations/0001_initial.py`: crea la tabla nueva; no hay backfill ni riesgo sobre datos existentes.
- `movie_up/entradas/services.py`: `crear_entrada`, `eliminar_entrada`, `listar_entradas`, `obtener_entrada` y validación por código.
- `movie_up/entradas/views.py`, `urls.py`, `templates/entradas/`: listado, detalle y validación en puerta.
- `movie_up/entradas/admin.py`: lectura sin acciones de borrado.
- `movie_up/entradas/tests.py`: cobertura de servicios, flujos de vista y concurrencia de validación.
- `movie_up/cuentas/admin.py`: activación de los dos guards `TODO(entrada)` en borrado individual y masivo.
- `movie_up/core/urls.py`: rutas de la nueva app.
- Lee y muta `movie_up/funciones/models.py` (`entradas_compradas`, `disponibilidad`, `distribucion`) con `select_for_update`, y lee `peliculas.Pelicula` y `salas.Sala` para las vistas.
- `AGENTS.md` y `README.md`: árbol de estructura y documentación del caso de uso.
- Sin cambios de requisitos en `movies`, `salas` ni `funciones`.
