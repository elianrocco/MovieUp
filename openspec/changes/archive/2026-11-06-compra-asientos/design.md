# Design

## Context

La página de compra (`compra_pelicula`) ya lista las funciones vendibles de una película con gating de login/staff/404, y su botón por función no tiene destino. Del lado del dominio todo el trabajo pesado ya existe: `entradas.services.crear_entrada` crea una entrada validando fila/asiento, marca la celda `R`, baja la disponibilidad y sube las entradas compradas en una transacción atómica con lock de fila, y la restricción `uq_entrada_asiento` impide doble venta. La cuadrícula de asientos ya tiene estilo propio (`.seat-grid`, `.celda--*` en `forms.css`) y un filtro de template `celda_clase` en `salas_tags`. Ver proposal.md por el motivo.

## Goals / Non-Goals

**Goals:**

- Conectar el botón de cada función con una vista de selección de asientos que use la distribución snapshot de la función.
- Convertir la selección del cliente en entradas reales, reutilizando `crear_entrada`, con garantía todo-o-nada.
- Mantener la vista dentro de los patrones existentes de la app `compras` (gating, services, templates a nivel de proyecto, CSS sobre tokens).

**Non-Goals:**

- Barrera de pago, validación de pago o retención de asientos antes de confirmar (queda para un cambio posterior).
- Límite de entradas por compra.
- Selección de asientos sin JavaScript: la cuadrícula interactiva requiere JS; el requisito `ui` "Degradación sin JavaScript" aplica a las acciones CRUD del panel, no a la compra.
- Mostrar los códigos de las entradas creadas en la pantalla de éxito (el mensaje de éxito queda tal como lo define la spec).

## Decisions

### D1. Ruta y gating de la vista

Ruta nueva en `compras/urls.py`: `path('<int:pelicula_id>/funciones/<int:funcion_id>/', views.seleccionar_asientos, name='seleccionar_asientos')`, servida bajo el prefijo `/compras/` ya incluido en `core/urls.py`. La vista replica el gating de `compra_pelicula`: visitante → redirect a `google_login` con `process=login` y `next` a la URL completa; `is_staff` → `/gestion/`; el resto renderiza.

La validación vive en un service nuevo `obtener_funcion_vendible(pelicula_id, funcion_id)` que lanza `Http404` si falta la película, falta la función, la función no pertenece a esa película, `funcion_activa` es falso o `fin <= ahora`. Alternativa descartada: redirigir al listado con un mensaje para funciones no vendibles — sería un estado que la spec no pide y rompería la consistencia con los 404 existentes de `compras`/`entradas`.

Una función agotada (disponibilidad 0) **sí** renderiza: no tiene celdas `A`, el contador queda en 0 y el botón de confirmación nace deshabilitado, lo que ya cubre su caso sin regla extra.

### D2. Cuadrícula renderizada en el servidor, JS solo para interacción

La cuadrícula se genera en el template con un bucle sobre `funcion.distribucion.filas` usando el filtro `celda_clase` (mismo render que `salas/_detail.html`), y las celdas `A` salen como `<button type="button">` mientras `P` y `R` salen como `<span>` inertes. Alternativa descartada: reutilizar `salas/js/grid.js`, que está acoplado al formulario del editor (cicla `P→A→R`, serializa al submit y edita la distribución); su lógica no aplica a selección.

La vista precalcula por cada celda `A` su **etiqueta de fila** (`etiqueta_fila`, convención bijectiva A, B, … Z, AA) y su **número de asiento** (ordinal 1-based entre `A`/`R` de la fila, sin contar `P`), y los emite como `data-fila` / `data-asiento`. El JS solo los copia a los inputs ocultos: así la regla de ordinal vive en Python y no se duplica en el cliente.

### D3. Confirmación por POST con PRG

El botón `Confirmar compra` es el submit de un `<form method="post">` con `{% csrf_token %}`; los inputs ocultos repetidos (`celda`, valor `FILA:ASIENTO`) los mantiene el JS sincronizados con la selección. El servidor lee `request.POST.getlist('celda')`.

Tras crear las entradas, la vista responde con **redirect (PRG)** a la misma ruta con `?compra=exitosa`, que renderiza únicamente el mensaje de éxito centrado y el botón `Mis entradas` (`entradas:entrada_list`). Alternativa descartada: renderizar el éxito en el mismo POST — recargar reenviaría el formulario e intentaría comprar de nuevo. Ruta dedicada de éxito descartada por sumar una URL que no aporta estado.

### D4. `confirmar_compra`: prevalidación + lote atómico

Service nuevo en `compras/services.py` decorado con `@transaction.atomic`:

1. Rechaza si no hay celdas o si hay pares `FILA:ASIENTO` duplicados.
2. Bloquea la `Funcion` con `select_for_update()` y revalida que siga activa y con `fin > ahora` (ojo: `crear_entrada` chequea `fin` pero **no** `funcion_activa`; sin esto un admin podría desactivar la función y la compra igual entraría).
3. Verifica `disponibilidad >= cantidad` y que la marca de distribución enviada por el formulario (las filas vigentes) coincida con la actual.
4. Llama a `crear_entrada` por cada par dentro de la misma transacción: cada llamada anida su `atomic` como savepoint, levanta `ValueError` si la celda ya no es `A`, y cualquier error revierte el lote completo.

La revalidación por celda la hace el propio `crear_entrada`, que ya mapea ordinal → celda y rechaza `R`; no se reimplementa. La marca de distribución cubre el caso residual en que el admin cambia la sala de una función sin entradas vendidas entre la carga de la página y la confirmación (la distribución cambió y los pares enviados podrían apuntar a otro asiento).

### D5. Selección, contador y total en JS

Archivo nuevo `movie_up/compras/static/compras/js/seleccion_asientos.js` (estático de la app, siguiendo el precedente de `salas/static/salas/js/grid.js`), cargado con `defer` desde el bloque `scripts` de la plantilla. En cada clic sobre un botón de asiento alterna la clase `celda--seleccionada` y `aria-pressed`, vuelve a escribir los inputs ocultos, recalcula contador y total, y alterna `disabled` + `btn--sold-out` en el botón de confirmación (mismo formato que el botón agotado del listado, reutilizando la clase existente en `compras.css`).

El total se calcula en **centavos enteros** (`Math.round(precio * 100) * cantidad`) y se formatea con `toFixed(2)` sin separador de miles para coincidir con `$30000.00` de `floatformat:2` en el listado. El precio llega en un atributo `data-precio` de la barra de resumen. Sin JS el botón queda deshabilitado y la compra no avanza (Non-Goal).

### D6. CSS

Todo en `compras.css`, sobre los tokens existentes:

- `.celda--seleccionada { background-color: var(--primary); }` — usa el token de la paleta (rojo cine), sin introducir hex nuevos; las tres celdas `P`/`A`/`R` conservan su excepción documentada en `forms.css`.
- Secciones nuevas: encabezado `Elija sus asientos`, filas de datos centradas con la etiqueta encima (mismo patrón de `.funcion-item__etiqueta`/`__valor`), barra de resumen alineada a la derecha y pantalla de éxito centrada.
- El centrado de la cuadrícula y de las filas de datos es una excepción pedida explícitamente por el usuario a la regla general de alineación a la izquierda (igual que las excepciones de celda ya aprobadas); queda asentada aquí.

## Risks / Trade-offs

- [Dos usuarios compran el mismo asiento a la vez] → La restricción `uq_entrada_asiento` y el lock de fila en `crear_entrada` serializan; el segundo lote falla completo y la vista muestra el error para re-seleccionar.
- [Función desactivada o vencida entre carga y confirmación] → Revalidación dentro de la transacción en `confirmar_compra`; rechazo sin crear nada.
- [La venta requiere JavaScript] → Aceptado como Non-Goal; sin JS el botón permanece deshabilitado y no se envía nada.
- [El `POST` es manipulable (celdas inventadas, duplicadas, fuera de rango)] → El servidor no confía en el cliente: pares duplicados/vacíos se rechazan y cada par pasa por `crear_entrada`, que valida existencia de fila, rango de ordinal y que la celda no esté reservada, todo dentro de la transacción.
- [Pérdida de dinero si el total del cliente no coincide con el cobrado] → En este cambio no hay cobro: el total es informativo y la creación usa el precio actual de la función en el servidor; la divergencia real se resuelve cuando entre la barrera de pago.
- [Reutilizar `btn--sold-out` para un botón que no está agotado] → El nombre queda impreciso, pero evita duplicar el estilo y romper el test existente del listado; renombrarlo se puede hacer en un refactor aparte.

## Migration Plan

Sin migraciones de datos ni de esquema: no se tocan modelos. El despliegue es el flujo normal de la app (migraciones se aplican al arrancar y no las hay). Rollback: revertir el código; las entradas creadas quedan consistentes con la distribución y no requieren limpieza.
