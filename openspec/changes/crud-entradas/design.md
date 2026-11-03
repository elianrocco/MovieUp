# Design

## Context

La motivación y el alcance están en `proposal.md`. Lo que condiciona esta propuesta técnica:

- `Funcion.distribucion` es un `JSONField` con forma `{'version': n, 'filas': ['AARPP', ...]}`: filas de celdas `P` (pasillo), `A` (asiento) y `R` (reservado), **sin etiqueta de fila** — la posición ordinal es su única identidad. Lo confirman tanto `salas/services.py` (`ALLOWED_CELLS`, `MAX_DISTRIBUTION_SIZE = 100`) como los templates de `salas` y `funciones`, que iteran por índice.
- `Funcion.disponibilidad` se inicializa como `sum(row.count('A'))` en `_distribution_snapshot`, así que **es** el conteo de asientos `A` y no una cifra independiente.
- `funciones` ya garantiza, por spec, que una función con `entradas_compradas > 0` no se puede editar ni eliminar. Eso congela `precio_entrada` mientras exista al menos una entrada.
- `cuentas.Cuenta` declara `db_table = 'cuenta'`; `Funcion`, `Sala` y `Pelicula` usan el nombre por defecto de Django. La base real tiene `cuenta.id` y `funciones_funcion.id` como `BIGINT` (`inspectdb`), y **no existe ninguna tabla de entradas**.
- El DDL entregado referencia `mydb.funcion` (tabla inexistente) y usa `INT` para las tres claves. Ver `proposal.md` y la sección de riesgos.

## Goals / Non-Goals

**Goals:**

- Un único punto de escritura de entradas, con toda la mutación de la función en la misma transacción.
- Invariante duradero: mientras exista una entrada, `disponibilidad` == conteo de `A` en la distribución y `entradas_compradas` == entradas de esa función.
- Ninguna superficie de borrado o edición manual, ni en vistas ni en admin.
- Que el contrato de fila (`l_fila`) sea explícito y compartible con el proceso de compra.

**Non-Goals:**

- Definir cómo elige el usuario su asiento ni cómo paga: eso vive en la spec de compra.
- Disparar la limpieza por vencimiento o el flujo completo de reembolso: son specs futuras que invocan servicios de este change.
- Cambiar la distribución, el modelo de `Funcion` o las specs de `salas`/`funciones`.

## Decisions

**1. La celda en la distribución y el índice único son dos capas, no una redundancia.**
La celda `R` da lectura inmediata a la UI y a la compra; el índice único `(funcion, l_fila, n_asiento)` aguanta la carrera que la celda no cubre (dos escrituras que leen la misma versión del JSON). Alternativa descartada: confiar solo en la celda — requiere serializar todas las escrituras de la función y aun así no cubre reintentos; solo el índice garantía cardinalidad a nivel de base.

**2. Coordenadas de asiento estables sin tocar la distribución.**
`l_fila` usa etiqueta alfabética por posición en base-26 (`fila 1 → A … Z → AA …`). `n_asiento` es el ordinal 1-based entre las celdas `A` y `R` de esa fila; las celdas `P` no suman, pero `R` sí porque es un asiento reservado cuya identidad debe persistir tras la venta. Alternativas consideradas: (a) meter etiquetas o numeración en el JSON obliga a cambiar `salas` y `funciones` y a migrar datos; (b) contar columnas físicas incluye los pasillos y contradice la convención fijada por el usuario. Se elige derivar ambas coordenadas para compartir el contrato con la compra sin guardar datos nuevos.

**3. Una sola transacción con `select_for_update()` sobre la `Funcion`.**
Es el patrón que ya usa `update_funcion`. La escritura del JSON es un leer-modificar-escribir: con `F()` atómico se evita el lock pero dos transacciones pueden partirse la celda. Se bloquea la función, se validan contra su estado bloqueado y se guardan los tres derivados juntos. Alternativa descartada: `F('entradas_compradas') + 1` aislado — arregla un campo y deja los otros dos expuestos.

**4. `codigo`: 12 caracteres de un alfabeto de 32 sin ambiguos, con `secrets` e índice único.**
Alfabeto `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (sin `0/O/1/I`), ≈60 bits, normalizado a mayúsculas antes de comparar. Descartados: UUID v4 (36 caracteres, imposible de tipear en puerta), entero (indistinguible de un ID y con mucha menos entropía), `secrets.token_urlsafe` (incluye `-` y `_`, fáciles de mal transcribir). El índice único es la garantía real; si la base detecta una colisión, el servicio rechaza esa creación con `ValueError` y no persiste entrada, conforme al escenario de la spec.

**5. `db_table = 'entrada'` con `PROTECT` en ambas FK.**
Se respeta el nombre del DDL entregado, con `cuenta` como precedente en el proyecto. `PROTECT` sigue el patrón de `Funcion.pelicula` y `Funcion.sala` y además es la red de seguridad detrás del guard de `cuentas`. Alternativa descartada: `CASCADE` — borrar una cuenta o una función arrastraría entradas silenciosamente, exactamente lo prohibido por spec.

**6. `404` (no `403`) ante una entrada ajena.**
Un `403` confirma que el ID existe, lo que permite enumerar entradas ajenas. `Http404` desde `DoesNotExist` es además el contrato de error del proyecto.

**7. Validación atómica con condición en el `UPDATE`.**
`filter(pk=…, activa=True).update(activa=False)` y usar el `rowcount` como oráculo de "encontrada / no encontrada". Alternativa descartada: leer, evaluar y guardar — dos validaciones simultáneas del mismo código podrían informar "encontrada" dos veces.

**8. Un servicio de eliminación con motivo cerrado.**
`motivo ∈ {reembolso, finalizacion}`; cualquier otro valor se rechaza. Hacer del "borrado manual" algo **imposible de expresar** es más fuerte que no publicar la vista: ni el admin ni una vista futura pueden invocarlo. Los disparadores futuros quedan como funciones delgadas sobre este servicio.

**9. El admin de `Entrada` es de solo lectura y sin acción de borrado.**
`has_delete_permission = False` y sin acciones masivas de eliminación, para que la regla se cumpla también desde el panel.

**10. Sin precio ni auditoría en la entrada: depende de un invariante ajeno.**
El precio se lee de `Funcion.precio_entrada` y la spec de `funciones` impide editarla mientras tenga entradas compradas; al reembolsar, la entrada se borra en la misma transacción en que se descuenta, así que nunca conviven una entrada y un precio cambiado. Coste aceptado: no queda registro de cuándo se compró ni de qué precio se pagó en la fila.

**11. El límite de 24 horas es una regla del reembolso, no del borrado.**
Se compara `Funcion.inicio` con `timezone.now()` (ambos *aware*, patrón ya usado en `funciones.services`) contra una constante `LIMITE_REEMBOLSO = timedelta(hours=24)`, y solo cuando el motivo es `reembolso`. La lectura es estricta: **faltan menos de 24 horas ⇒ rechaza; 24 horas exactas o más ⇒ acepta**; una función ya iniciada o finalizada queda rechazada por la misma regla. Alternativa descartada: aplicar el límite dentro del servicio de eliminación genérico — la eliminación por finalización ocurre necesariamente cuando `fin` ya transcurrió, con lo que esa rama quedaría **jamás ejecutable**. El orden de validaciones es `activa` primero y anticipación después, para que el mensaje de rechazo sea determinista cuando fallan ambas.

## Risks / Trade-offs

- [Dos compras simultáneas del mismo asiento] → lock de la función + índice único compuesto; test de concurrencia que ejecuta ambas creaciones a la vez.
- [Dos validaciones simultáneas del mismo código] → `UPDATE` condicional y `rowcount`; solo una puede informar "encontrada".
- [`disponibilidad` se desincroniza del conteo de `A`] → los tres derivados se escriben en la misma transacción; test de invariante que cuenta `A` y lo compara con `disponibilidad` después de crear y reembolsar.
- [Colisión de `codigo`] → índice único; un `IntegrityError` se convierte en `ValueError` y revierte la entrada y todos los cambios a la función.
- [El DDL entregado tiene tipos `INT` y referencia una tabla `funcion` inexistente] → la migración de Django es la fuente de verdad; **no crear la tabla a mano en Workbench**, o `migrate` fallará con "table already exists". Corregir el diagrama al archivar.
- [La especificación de reembolso se aplica al motivo equivocado] → el límite vive condicionado a `motivo == 'reembolso'`; test específico que verifica que la eliminación por finalización sigue ejecutándose con la función ya vencida.
- [El guard de `cuentas` pasa de `TODO` a real y puede romper un flujo de admin existente] → tests de borrado individual y masivo en ambas direcciones (con entradas y sin ellas).
- [La spec cubre comportamiento cuyo disparador aún no existe] → el servicio se prueba directamente; el disparador se implementa en la spec futura correspondiente.

## Migration Plan

1. Crear `movie_up/entradas/migrations/0001_initial.py` con `makemigrations entradas` (tabla nueva, sin backfill).
2. Verificar `manage.py makemigrations --check --dry-run` limpio y `migrate --plan` sin sorpresas.
3. Aplicar con `docker compose exec web python movie_up/manage.py migrate` — la entrada es automática al arrancar el contenedor.
4. Rollback: `migrate entradas 0000` elimina la tabla; como la capacidad nace en este change, no hay datos previos que preservar. Si ya se crearon entradas en producción, exportar antes de revertir.

## Open Questions

- **Longitud del código**: la spec solo exige que sea complejo y único. Los 12 caracteres son una decisión de implementación reversible sin tocar la spec.
- **Disparadores**: qué y cuándo llama a `eliminar_entrada` (reembolso del cliente, limpieza por `Funcion.fin`) queda para las specs futuras y no altera este diseño.
