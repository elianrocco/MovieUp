# Proposal

## Why

La paleta oficial define un fondo decorativo completo —degradados radiales, grano de película y cintas de cine— que nunca se implementó: el `body` de la web es crema plano. Se pide activarlo íntegro, con **ambos** tipos de cintas: las verticales a los costados y cintas cruzadas en diagonal sobre todo el fondo.

## What Changes

- Degradados radiales sutiles sobre el crema del fondo global: más claro arriba y más dorado abajo.
- Capa de grano de película en tono marrón con opacidad muy baja, encima de los degradados.
- Cintas de película verticales en ink a los costados, con perforaciones en crema y separadores de fotograma en dorado al 35%.
- Cintas de película cruzadas en diagonal sobre todo el fondo.
- Todo como capa decorativa detrás del contenido, con opacidad baja que no interfiere con la lectura ni con la interacción.

## Capabilities

### New Capabilities

 Ninguna.

### Modified Capabilities

- `ui`: nuevo requisito de fondo decorativo global (degradados, grano y cintas de cine, verticales y cruzadas) presente en todas las vistas de la web.

## Impact

- CSS: `movie_up/static/css/base.css` (capa decorativa del `body`). Sin cambios de templates, rutas, vistas, servicios ni modelos.
- Alcance: todas las vistas que extienden `base.html`. Las páginas de `/admin/` no cargan `base.css` y quedan fuera de este cambio.
- Tests: no hay HTML nuevo que assertear; la verificación es la suite completa sin regresiones más Playwright a 1280×900 con capturas.
