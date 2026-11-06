# Tasks

## Lote 1 — Vista de lectura

## 1. Acceso y ruta de la selección de asientos

- [x] 1.1 Implementar `obtener_funcion_vendible(pelicula_id, funcion_id)` en `movie_up/compras/services.py` con `Http404` para película/función ausente, función ajena a la película, `funcion_activa=False` y `fin <= ahora`, y verificación con tests de servicio en `movie_up/compras/tests.py` (pasa con `docker compose exec web python movie_up/manage.py test compras`).
- [x] 1.2 Agregar la ruta `seleccionar_asientos` en `movie_up/compras/urls.py` (`<int:pelicula_id>/funciones/<int:funcion_id>/`) y la vista con el gating de la compra (visitante → `google_login` con `process=login` y `next` a la URL completa; `is_staff` → `/gestion/`; común → render), verificando con tests de vista que los tres accesos y el 404 responden como espera la spec.

## 2. Cuadrícula, encabezado y datos de solo lectura

- [x] 2.1 Crear `movie_up/templates/compras/seleccion_asientos.html` con el encabezado `Elija sus asientos` y la cuadrícula renderizada en servidor desde `funcion.distribucion.filas` con el filtro `celda_clase`: celdas `A` como `<button type="button">` con `data-fila` (etiqueta vía `etiqueta_fila`) y `data-asiento` (ordinal entre `A`/`R`), `P` y `R` como `<span>` inertes; verificar con tests que aparecen las clases de color correctas, los `data-*` de cada asiento, los asientos ya vendidos en `R` y el estado inicial con contador en 0 y botón `Confirmar compra` deshabilitado con `btn--sold-out`.
- [x] 2.2 Agregar las cuatro filas de datos centradas con la etiqueta encima de cada ítem (`Título`, `Descripción`, `Idioma`, `Subtitulada`, `Tipo de sala`, `Tipo de sonido`, `Inicio`, `Fin`, `Duración`) usando `d/m/Y H:i` para inicio/fin, `Sí/No` para subtitulada y los minutos de la película para duración; verificar con tests de template que etiquetas, orden y valores coinciden con la spec.
- [x] 2.3 Extender `movie_up/static/css/compras.css` con el centrado de la cuadrícula, el encabezado, las filas de datos (etiqueta arriba del valor, patrón `funcion-item__etiqueta`/`__valor`) y la barra de resumen abajo a la derecha con las etiquetas `Cantidad de entradas` y `Total` a la izquierda de sus valores, verificando en navegador con Playwright que la vista se ve centrada en desktop y móvil sin romper el listado de funciones existente.

## 3. Botón de compra con destino

- [x] 3.1 Cambiar el botón `Comprar entradas` de cada función vendible en `movie_up/templates/compras/compra_pelicula.html` a un enlace a `compras:seleccionar_asientos` con `pelicula.pk` y `funcion.pk`, dejando el agotado como `<button disabled>`; verificar con tests que cada botón apunta a la función que representa, que el agotado sigue sin navegación y que los tests existentes del listado (`test_function_item_renders_all_fields`, `test_sold_out_button_is_disabled_without_href`) siguen pasando.

## Lote 2 — Confirmación en servidor

## 4. Confirmación atómica de la compra

- [ ] 4.1 Implementar `confirmar_compra(funcion_id, cuenta_id, celdas, marca_distribucion)` en `movie_up/compras/services.py` con `@transaction.atomic`: rechaza lista vacía, pares duplicados y marca de distribución distinta; bloquea la `Funcion` con `select_for_update()`, revalida `funcion_activa` y `fin > ahora`, comprueba `disponibilidad >= cantidad` y llama a `crear_entrada` por cada par dentro de la transacción; verificar con tests: compra de N asientos crea N entradas con fila/asiento correctos y actualiza distribución, disponibilidad y entradas compradas; un asiento tomado o una función desactivada/vencida revierten el lote completo dejando la función intacta.
- [ ] 4.2 Manejar el POST en la vista `seleccionar_asientos` con `{% csrf_token %}` y `request.POST.getlist('celda')`, re-renderizando la vista con mensaje de error cuando `confirmar_compra` lanza `ValueError`; verificar con tests que un POST sin sesión va al login con `next`, un POST válido redirige a `?compra=exitosa`, un POST sin celdas o con una celda ya ocupada no crea ninguna entrada y muestra el error.

## Lote 3 — Selección interactiva y cierre

## 5. Selección interactiva, contador y total

- [ ] 5.1 Crear `movie_up/compras/static/compras/js/seleccion_asientos.js` (cargado con `defer` en la plantilla) que al hacer clic alterna `celda--seleccionada`/`aria-pressed` solo en botones de asiento, reescribe los inputs ocultos `celda` (`FILA:ASIENTO`), recalcula el contador y el total en centavos con `data-precio` (formato `$0.00` sin separador de miles) y alterna `disabled` + `btn--sold-out` del botón de confirmación; agregar en `compras.css` `.celda--seleccionada` con `var(--primary)`, verificando con Playwright en desktop y móvil: clic en `A` cambia a rojo y suma, clic en rojo vuelve a azul y resta, clic en `P`/`R` no hace nada, el total es cantidad × precio y el botón pasa de deshabilitado a habilitado.
- [ ] 5.2 Verificar con Playwright que la consola del navegador queda sin errores en la vista de selección y que el flujo completo lista → selección → confirmación → éxito navega correctamente (capturas en `.playwright-mcp/`).

## 6. Pantalla de compra realizada

- [ ] 6.1 Renderizar con `?compra=exitosa` el mensaje `Compra realizada con éxito, puede ver sus entradas en` y el botón `Mis entradas` apuntando a `entradas:entrada_list` (`/entradas/`), centrado y sin cuadrícula; verificar con tests que el mensaje, el destino del botón y la ausencia de la cuadrícula se cumplen, y con Playwright que el redirect POST-GET no reenvía la compra al recargar.

## 7. Verificación de integración

- [ ] 7.1 Correr la suite completa `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas compras core`, más `manage.py check` y `manage.py makemigrations --check --dry-run`, y verificar que todo pasa sin errores ni migraciones pendientes.
- [ ] 7.2 Repetir la verificación Playwright final del flujo completo en desktop y móvil con la consola limpia, y dejar las capturas en `.playwright-mcp/`.

## Workflow follow-up

- Validar con `openspec validate compra-asientos --strict` y `openspec validate --specs --strict` antes de archivar.
- Archivar el cambio con `openspec archive compra-asientos` cuando el usuario lo pida, y actualizar los árboles de `AGENTS.md`/`README.md`.
- No invocar al agente `readme-maintainer` (instrucción explícita del usuario).
