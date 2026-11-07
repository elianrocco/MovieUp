# Proposal

## Why

La vista de validación en puerta (`/entradas/validar/`) existe pero no tiene acceso visible desde la navegación: las administradoras deben escribir la URL a mano. Además, la vista se renderiza con estilos genéricos, sin panel ni centrado, y con un botón de envío sin la estética del sitio.

## What Changes

- Botón dorado en el nav global, al extremo izquierda, con enlace a `/entradas/validar/`, visible únicamente para cuentas administradoras.
- Presentación de la vista de validación: encabezado, formulario y resultado dentro de un panel blanco centrado horizontalmente en la página.
- Botón `Validar` con el color dorado de la paleta.

## Capabilities

### New Capabilities

 Ninguna.

### Modified Capabilities

- `ui`: nuevo requisito de botón de validación en el nav, visible solo para cuentas administradoras y al extremo izquierda.
- `entradas`: nuevo requisito de presentación de la vista de validación (panel blanco centrado y botón `Validar` dorado).

## Impact

- Templates: `movie_up/templates/includes/site_nav.html` (botón con guard de administradora), `movie_up/entradas/templates/entradas/validar.html` (envoltorio en panel y clase del botón).
- CSS: `movie_up/static/css/site-shell.css` (celda izquierda del nav y estilo dorado del botón).
- Tests: `movie_up/core/tests.py` (visibilidad por rol del botón), `movie_up/entradas/tests.py` (panel, centrado y botón dorado).
- Sin cambios de rutas, vistas, servicios ni modelos.
