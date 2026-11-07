# Design

## Context

- El nav global (`site_nav.html`) se renderiza con CSS grid de tres columnas (`minmax(0,1fr) auto minmax(0,1fr)`): la columna izquierda está vacía, el brand ocupa la central y las acciones de sesión la derecha. El patrón de guard por rol ya existe en el propio nav: `Mis entradas` se muestra con `{% if not user.is_staff %}`.
- La vista de validación (`entradas/validar.html`) extiende `base.html` y renderiza encabezado, formulario, mensaje y datos de la entrada sin ningún contenedor de presentación, con un `<button>` genérico de envío.
- Ya existen los patrones reutilizables: `.panel` + `.panel--light` (panel de superficie clara) y `.btn--gold` (fondo `--gold`, texto `--on-gold`, hover con opacidad al 80%), ambos con el par de contraste AA de la paleta.
- La ruta y la lógica de validación no cambian; ver proposal.md para la motivación y specs/ui + specs/entradas para el contrato de comportamiento.

## Goals / Non-Goals

**Goals:**

- Acceso de una sola navegación a `/entradas/validar/` para cuentas administradoras desde cualquier vista.
- Presentación de la vista de validación consistente con la paleta cinematográfica (panel blanco centrado, botón dorado).
- Reutilizar patrones y clases existentes; cero cambios de ruta, vista, servicio o modelo.

**Non-Goals:**

- Modificar el comportamiento de validación (búsqueda, activación única, autorización).
- Agregar el acceso al subNAV de `/gestion/`.
- Estilizar otros formularios o vistas del sitio.
- Ajustes responsive: la app es solo desktop (verificación a 1280×900).

## Decisions

**D1 — Ubicación del botón: celda izquierda de la grid del nav.**
Se agrega como primer elemento del nav con `grid-column: 1`, la columna que hoy está vacía. El brand permanece centrado y las acciones a la derecha, sin mover nada existente.
*Alternativas descartadas:* (a) insertarlo antes del brand en la celda central — desplazaría el brand centrado que exige el requisito "Nav global con estados de sesión"; (b) ponerlo dentro de `.site-nav__actions` — quedaría a la derecha, contrary a "a la izquierda del todo".

**D2 — Visibilidad con `{% if user.is_staff %}`.**
Es la convención exacta del propio nav (opuesto del guard de `Mis entradas`) y `is_staff` está sincronizado con el indicador de administrador del panel de Django. "Cuentas administradoras" ≡ cuentas con `is_staff`.
*Alternativa descartada:* `is_superuser` — excluiría a las cuentas de personal que el sistema considera administradoras.

**D3 — Color dorado con los tokens de la paleta.**
Fondo `var(--gold)` y texto `var(--on-gold)` (par con contraste AA), hover bajando la opacidad del mismo token. Precedente visual: el botón `Mis entradas` ya es dorado en el nav (`.site-nav__ticket`), por lo que el nuevo botón hereda esa estética de nav.
*Alternativa descartada:* inventar un tono nuevo — la paleta está cerrada a los 12 tokens.

**D4 — Centrado como bloque, formulario alineado a la izquierda.**
El contenido de `validar.html` se envuelve en `.panel.panel--light` y el panel se centra horizontalmente (`margin-inline: auto` con ancho acotado). Dentro del panel, encabezado, campos y resultado conservan alineación a la izquierda, siguiendo la regla de ui-design ("formularios nunca centrados") y el precedente del propio requisito CRUD: "tarjeta centrada de ancho acotado con el contenido alineado a la izquierda".
*Alternativa descartada:* centrar el texto de los campos y etiquetas — viola la regla de centrado y rompe la lectura de formularios.

**D5 — Botón `Validar` con la clase `btn btn--gold` existente.**
Reutiliza `.btn--gold` (tamaño de botón dentro del rango 40–56px, par AA, hover por opacidad) en lugar de declarar estilos nuevos para un solo elemento.
*Alternativa descartada:* una variante `btn--*` nueva — sin beneficio y con duplicación.

**D6 — Todo el contenido dentro del unico panel.**
Encabezado, formulario, mensaje de resultado y `dl` de datos comparten el mismo panel, de modo que el resultado posterior a la validación también quede contenido (escenario "Resultado dentro del panel").

## Risks / Trade-offs

- [El botón es global: aparece en todas las vistas para administradoras] → es el comportamiento pedido; los tests de visibilidad en `core/tests.py` lo cubren en varias vistas, junto a los existentes de `Mis entradas`.
- [El panel centrado con ancho acotado podría verse apretado en pantallas angostas] → la verificación Playwright es a 1280×900 (formato soportado por la app); el ancho acotado usa márgenes máximos generosos.
- [Caché del navegador tras editar CSS] → en la verificación se fuerza la recarga del stylesheet para no evaluar CSS viejo (gotcha ya conocido del proyecto).
