# Design

## Context

Las tres vistas a decorar ya funcionan y comparten la base visual del proyecto: tokens de paleta en `tokens.css`, `.btn`/`.btn--buy` en `components.css` y `.seat-grid`/`.celda--*` en `forms.css`. El listado de funciones usa un `grid` fijo de 4 columnas (de ahí el salto entre `Idioma` y `Subtitulada`); la vista de selección tiene `h1`, cuadrícula, datos y resumen como hermanos planos; la pantalla de éxito es horizontal con botón rojo; y los templates de `entradas` (`list.html`, `detail.html`) no cargan ningún CSS ni siquiera `{% block head %}` — la app no tiene `static/`. El dorado del nav es `--gold` con texto `--on-gold` (`.site-nav__ticket`), y el reembolso ya existe como servicio (`eliminar_entrada(entrada_id, 'reembolso')` con sus guards de activa y 24 horas) pero sin ruta ni vista. Ver proposal.md por el motivo.

## Goals / Non-Goals

**Goals:**

- Dar jerarquía visual a las vistas de compra con tres paneles (dorado, blanco, blanco) y un solo renglón para los datos del listado.
- Estilar lista y detalle de `/entradas/` con el dorado del nav y botones con contorno rojo, usando CSS propio de la app.
- Conectar el botón `Reembolso` al servicio de reembolso existente sin tocar servicios ni modelos.
- Mantener intactos los contenidos, el gating, las reglas de reembolso y los tests de contenido actuales.

**Non-Goals:**

- CSS, media queries o verificación para móvil/tablet: la app es solo PC y el usuario pidió no probar en teléfono.
- Cambiar el nav, la paleta, los textos de datos o el estado vacío `No tenés entradas.`
- Modificar las reglas de reembolso (activa, 24 horas, reversión) ya definidas en `entradas`.
- Flujo de pago, límite de entradas por compra o mensajes de éxito nuevos que no se pidieron.

## Decisions

### D1. Una sola línea en el listado de funciones

`.funcion-item__meta` pasa de `grid-template-columns: repeat(4, minmax(0, 1fr))` a `display: flex; flex-wrap: wrap` con items a ancho de contenido y el gap existente. Los siete datos (~600 px de contenido) caben en la fila única dentro de los ~710 px disponibles a 1280 px, y el `flex-wrap` hace que solo se parten si la ventana se angosta mucho. Los media queries de columnas de este bloque quedan sin efecto y se eliminan. Alternativa descartada: `repeat(7, 1fr)` forzaría columnas de ~100 px y partiría las fechas (`.funcion-item__valor` tiene `overflow-wrap: anywhere`). Verificación: Playwright mide que los siete items comparten la misma coordenada `top`.

### D2. Paneles de la vista de selección

Wrappers en `seleccion_asientos.html`: `.panel.panel--gold` envuelve `h1` + alerta de error + `.seat-grid-viewport`; `.panel.panel--light` envuelve `.datos`; el `<form class="resumen panel panel--light">` envuelve el resumen. En `compras.css`:

- Ancho con `margin-inline: 10vw` (un `vw` = 1% del ancho de pantalla, la lectura literal de "10% del ancho total de la pantalla a cada lado" → 80% de ancho), centrado por márgenes automáticos.
- `border-radius: 12px` (igual que `.funcion-item`), `background: var(--gold)` en el dorado, `var(--surface)` en los blancos, `padding: 1rem 1.25rem` (el "sobresalir apenas" vertical) y título en `var(--on-gold)` (par de contraste AA del oro).
- Pegado: `margin-top: 0` en el panel blanco de datos (su borde toca el del dorado); `margin-block: 1.5rem` en el del resumen ("margen arriba y abajo"); las filas `.datos__fila` conservan su gap.
- `.seleccion` pierde `width: 75%` (los paneles son dueños de sus márgenes) y conserva el margen vertical de sección.
- Sin media queries nuevas: sin soporte móvil por decisión del usuario. En ventanas estrechas de PC la cuadrícula ya tiene `overflow: auto` propio.

Alternativa descartada: `width: 80%` sobre el contenedor actual — porcentajes de ancho se resuelven contra el padre (75%), no contra la pantalla, y no darían el 10% pedido.

### D3. El "blanco" de los paneles

`--surface` (crema claro, `#FCF8EC`) es el blanco de la paleta y es lo que se usa fuera de las tarjetas. El blanco puro `#FFFFFF` está prohibido por la regla de paleta cerrada: si se lo pide expresamente, primero pregunto "¿seguro que querés `#FFFFFF` en vez de `--surface`?" antes de aplicarlo.

### D4. Botones dorados compartidos

En `components.css`, dos clases nuevas reutilizadas por las tres vistas:

- `.btn--gold`: `background: var(--gold); color: var(--on-gold)` con hover en opacidad 0.8 — mismo perfil que `.site-nav__ticket`. Lo usa `Mis entradas` de la pantalla de éxito.
- `.btn--gold-outline`: mismo fondo y texto más `border: 2px solid var(--primary)`. Lo usan `Ver entrada` del listado, `Volver a mis entradas` y `Reembolso` del detalle.

Ambas sobre `.btn` (min-height 40-56 px ✓). El contorno rojo usa `--primary`, token de paleta: sin desviaciones de color.

### D5. Lista de entradas: de tabla a tarjetas

Un `<tr>` no admite bordes redondeados confiables con `border-collapse: collapse`, así que `list.html` se reconvierte en `<ul class="entradas">` con `.entrada-card` por registro: fondo `--gold`, `border-radius: 12px`, contenido centrado, campos con la etiqueta encima (patrón ya usado en `.funcion-item__dato`) y el botón `Ver entrada` como `.btn--gold-outline`. Los textos y el `href` exactos no cambian: los tests actuales (`entradas/tests.py:483-508`) afirman contenido y enlaces, no `<table>`, y siguen pasando sin tocarlos. El estado vacío queda como está.

### D6. Detalle centrado con dos botones

`detail.html` envuelve el `<dl>` en un panel `.panel--gold` (misma clase que D2), centra los datos, les da `gap` visible entre items y convierte la navegación en una fila centrada: enlace `Volver a mis entradas` con `.btn--gold-outline` y, al lado, un `<form method="post">` con `{% csrf_token %}` y botón `Reembolso` — el **mismo perfil** `.btn--gold-outline` por uniformidad con su compañero (la alternativa de pintarlo de rojo por ser destructivo queda descartada por no haberse pedido).

### D7. Reembolso: ruta POST que delega en el servicio

Ruta nueva en `entradas/urls.py`: `path('<int:pk>/reembolso/', views.entrada_reembolsar, name='entrada_reembolsar')`. La vista, decorada con `@require_POST` (GET → 405):

1. `obtener_entrada(pk, request.user.pk)` — reutiliza el control de propiedad existente (ajena o inexistente → 404) sin duplicarlo.
2. `eliminar_entrada(entrada.pk, 'reembolso')` — el servicio ya valida activa, 24 horas, contadores y distribución; en `ValueError` se re-renderiza el detalle con `.error-message` (patrón de la compra: los checks del servicio ocurren antes de mutar, así que nada cambió y no hace falta refrescar).
3. Éxito → `redirect('entradas:entrada_list')` (PRG): la entrada ya no existe, la URL del detalle devolvería 404. Sin mensaje de éxito, que no se pidió.

`services.py` y los modelos no cambian.

### D8. Verificación

Toda la verificación es de escritorio (1280×900): Playwright para medidas (una sola línea, anchos de panel, pegado de los paneles, posición del botón de éxito, tarjetas y detalle) y consola limpia, más la suite Django para el reembolso y las clases nuevas. Sin capturas ni pruebas móviles.

## Risks / Trade-offs

- [Reconvertir la tabla a tarjetas rompe tests de markup] → Verificado: los tests de lista/detalle afirman textos y `href`, no elementos de tabla; el cambio conserva ambos.
- [El texto de los siete datos no cabe en ventanas de PC angostas] → `flex-wrap` degrada a dos renglones en vez de partir fechas; se verifica a 1280 px, el ancho de uso de la app.
- [Los paneles a 10vw dejan poco ancho en pantallas pequeñas] → la cuadrícula conserva su scroll interno (`overflow: auto`) y el padding mínimo evita que el contenido se corte; no se diseña para móvil.
- [Doble envío del reembolso] → el segundo POST llega después del redirect o contra una entrada ya borrada → `obtener_entrada` responde 404 y no hay doble efecto; el servicio además bloquea la fila.
- [El dorado como fondo grande rompe la proporción 60/25/10/5] → los paneles son bloques de contenido acotados (no fondos de página) y el oro ya está aprobado para badges; el título usa `--on-gold` con contraste AA.

## Migration Plan

Sin migraciones de datos ni de esquema: no se tocan modelos. Rollback: revertir el código; el reembolso aplicado es una operación de negocio legítima (entradas borradas por reembolso no se restauran, igual que cualquier reembolso).
