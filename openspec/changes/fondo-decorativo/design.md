# Design

## Context

- La sección *Fondo decorativo* de la paleta oficial define las tres capas (degradados radiales `oklch(0.97 0.035 90)` arriba y `oklch(0.9 0.05 80 / 0.6)` abajo; grano SVG `feTurbulence` en marrón con opacidad muy baja; cintas verticales en ink a los costados con perforaciones en crema y separadores en dorado al 35%) pero nunca se implementó: `body` en `movie_up/static/css/base.css` solo tiene `background: var(--bg)` (crema plano).
- `base.html` es la plantilla base de todas las vistas de la web; `admin/base_site.html` carga `tokens/components/site-shell/admin-shell` pero **no** `base.css`.
- `.site-header` es `position: sticky; z-index: 100; background: var(--ink); backdrop-filter: blur(12px)` — difumina lo que queda a su espalda.
- Paneles, tarjetas y botones tienen fondos opacos propios (`.panel--light`, cards) y se leen por encima de cualquier decoración de fondo. Ver proposal.md para la motivación y specs/ui para el contrato.

## Goals / Non-Goals

**Goals:**

- Las tres capas de la paleta globales y siempre por detrás del contenido.
- Ambos tipos de cintas simultáneos: verticales ancladas a los costados y diagonales cruzando todo el fondo.
- CSS puro: cero dependencias, cero JavaScript, cero elementos de markup nuevos.

**Non-Goals:**

- Decorar `/admin/` (no carga `base.css`; se puede agregar después en `admin-shell.css` si se pide).
- Alterar colores de contenido, contraste AA o la paleta de 12 tokens.
- Animación o interactividad de la decoración.
- Ajustes responsive: la app es solo desktop (verificación a 1280×900).

## Decisions

**D1 — Todo el cambio vive en `base.css`.**
Una sola fuente, cargada por cada vista vía `base.html`, sin tocar ningún template.
*Alternativa descartada:* un elemento decorativo en `base.html` — agrega markup sin necesidad; los fondos no requieren elementos.

**D2 — Capas apiladas como `background` de `body`, sin pseudo-elementos.**
La decoración se declara como múltiples capas de `background` en `body` (gradientes, grano como SVG data-URI y cintas como `repeating-linear-gradient`). El fondo de `body` se propaga al lienzo del documento, así que queda inherentemente por detrás de **todo** el contenido, nunca intercepta clics (los fondos no son interactivos) y no puede quedar mal apilado por un `z-index` o un stacking context accidental.
*Alternativas descartadas:* (a) `body::before/::after` fixed — piezas móviles con riesgo de stacking context según qué reglas se agreguen después; (b) capa en un elemento del HTML — markup nuevo; (c) canvas/JS — dependencia y costo para algo estático.

**D3 — Opacidades jerarquizadas con tokens de la paleta.**
Degradados con los valores exactos de la paleta; grano en marrón con ~4% de opacidad; cintas verticales en `--ink` con alfa baja, perforaciones en crema y separadores en `--gold` al 35% (tal cual la paleta); cintas diagonales en `--ink` con alfa menor que las verticales para que la zona central —donde hay texto directo sobre el fondo— siga limpio.
*Alternativa descartada:* opacidades altas o colores nuevos — rompen legibilidad y la paleta está cerrada.

**D4 — Jerarquía entre los dos tipos de cintas.**
Las verticales se anclan a los costados y las diagonales cruzan todo el viewport; en la pila de `background` las diagonales van por debajo de las verticales para que las laterales enmarquen la composición y las cruzadas aporten profundidad sin empastarse.

**D5 — `background-attachment: fixed` en todas las capas.**
El fondo permanece estable mientras el documento scrollea ("background general de toda la web") y evita repintado ligado al scroll: no hay elementos que repintar por posición, solo la capa de fondo del lienzo.
*Alternativa descartada:* scroll — las cintas se desplazarían con el documento y perderían el efecto de marco.

## Risks / Trade-offs

- [Las diagonales cruzan zonas con texto directo sobre el fondo (descripciones de tarjetas, estados vacíos)] → mantener su alfa muy por debajo de las verticales y verificar legibilidad en Playwright en home y `/gestion/`.
- [El `backdrop-filter` del nav difumina la decoración a su espalda] → comportamiento esperado y deseable; verificar sin artefactos usando capturas de **página completa** (el artefacto de captura de elemento con `backdrop-filter` ya está documentado de sesiones previas).
- [Muchas capas de fondo con `attachment: fixed` podrían costar en scroll] → todas son gradientes y un SVG mínimo (cientos de bytes), sin imágenes pesadas; la verificación de consola/rendimiento queda en la tarea de integración.
- [El grano en SVG data-URI puede inflar `base.css` si se elige un SVG elaborado] → usar un `feTurbulence` mínimo, en una línea.
