# Proposal

## Why

El botón `Comprar entradas` de cada función del listado no tiene destino: la spec `compras` lo dejó explícitamente "fuera de alcance: MUST NO navegar" hasta que existiera el flujo de selección. Sin una vista de asientos el cliente no puede elegir dónde sentarse ni completar la compra, y todo el trabajo de disponibilidad, distribución y creación de entradas que ya existe queda sin conectar.

## What Changes

- **Nueva vista de selección de asientos** en `/compras/<pelicula_id>/funciones/<funcion_id>/` con el mismo gating que la página de compra: visitante conducido al login con Google con retorno a esa página, cuenta administradora redirigida a `/gestion/`; una película o función inexistente, una función ajena a la película, inactiva o finalizada responden 404.
- **Cuadrícula de asientos** debajo del nav, centrada, con el encabezado `Elija sus asientos` y la distribución snapshot de la función, usando los mismos colores que el editor de sala: gris `P`, azul `A`, dorado `R`. Solo las celdas `A` son interactivas: al hacer clic pasan a rojo (seleccionada) y vuelven a azul; las celdas `P` y `R` no admiten interacción.
- **Datos de solo lectura** debajo de la cuadrícula, en filas centradas y con la etiqueta encima de cada ítem: título y descripción de la película; idioma, subtitulada, tipo de sala y tipo de sonido; inicio, fin y duración de la función.
- **Barra de resumen abajo a la derecha**: contador `Cantidad de entradas` y total (`cantidad × precio de entrada`) con su etiqueta a la izquierda (no arriba), y el botón `Confirmar compra` sin etiqueta. El contador y el total se actualizan con cada celda seleccionada y solo la cuadrícula y el botón son interactivos.
- **Botón `Confirmar compra` deshabilitado en 0 celdas**, con el mismo formato que el botón agotado del listado (rojo primario atenuado, `cursor: not-allowed`, sin envío); con una o más celdas queda habilitado.
- **Confirmación de la compra**: al confirmar, el sistema crea una entrada por cada celda seleccionada con su fila y su número de asiento, en una única operación atómica (todo-o-nada) que revalida la venta al momento de confirmar. **La barrera de pago queda fuera de alcance en este cambio: el sistema avanza directamente como si el pago se hubiera confirmado.** Después muestra el mensaje `Compra realizada con éxito, puede ver sus entradas en` seguido del botón `Mis entradas` (`/entradas/`).
- **DESTINO del botón `Comprar entradas`**: el botón pasa de no navegar a conducir a la vista de selección de asientos de su función (REMOVED del requisito "Botón de compra de cada función" + ADDED de "Destino del botón de compra de cada función"); el botón de una función agotada sigue deshabilitado y sin navegación.
- **Sin límite de entradas por compra** en este cambio: si debe existir uno, se define junto con la barrera de pago.
- **BREAKING**: ninguna.

## Capabilities

### New Capabilities

- (ninguna: la selección de asientos pertenece al flujo de compra existente)

### Modified Capabilities

- `compras`: MODIFIED de "Botón de compra de cada función" (el botón ahora navega a la vista de selección de asientos) y ADDED de los requisitos de la vista de selección, la cuadrícula interactiva, los datos de solo lectura, el resumen con contador y total, la confirmación atómica de la compra y la vista de éxito.

## Impact

- **`movie_up/compras/`**: vista `seleccionar_asientos`, ruta nueva en `urls.py` (`app_name='compras'`), servicios `obtener_funcion_vendible` y `confirmar_compra` en `services.py` y tests nuevos.
- **`movie_up/templates/compras/`**: plantilla de la vista de selección y plantilla de confirmación, siguiendo la ubicación de `compra_pelicula.html`.
- **`movie_up/templates/compras/compra_pelicula.html`**: el botón de cada función vendible pasa a ser un enlace a la nueva vista; el de agotada conserva el `button disabled`.
- **`movie_up/static/css/compras.css`**: celda seleccionada (rojo primario de la paleta), encabezado, filas de datos con etiqueta encima, barra de resumen y vista de éxito.
- **Nuevo JS de selección** (estático de la app `compras`, siguiendo el precedente de `salas/static/salas/js/grid.js`): alterna la selección de las celdas `A`, actualiza contador, total y estado del botón, y envía las celdas seleccionadas en el POST.
- **Reutiliza sin modificar** `entradas.services.crear_entrada` (una llamada por celda dentro de una transacción externa), `salas_tags.celda_clase` para los colores y las clases `.seat-grid`/`.celda--*` de `forms.css`.
- **Sin cambios de modelo ni migraciones**: se usan `Pelicula`, `Funcion`, `Sala` y `Entrada` existentes.
- **Tests**: nuevos de `compras` (acceso, 404, render de la cuadrícula, interacción, revalidación y lote atómico) y ajuste de los tests del botón de compra en `compras`/`core`.
