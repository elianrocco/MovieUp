---
name: ui-design
description: "Trigger: cambiar colores, CSS, estilos, interfaz, paleta, botón, centrar, tipografía, hover, tema. Establece la paleta pastel cinematográfica y el layout de MovieUp."
license: Apache-2.0
metadata:
  author: "Elian"
  version: "1.0"
---

# ui-design

## Activation Contract

Cargar esta skill antes de crear o modificar cualquier elemento visual de la página (templates, CSS, colores, layout, botones, tipografía) y como contexto de soporte al verificar la UI en navegador. No cargar para cambios sin componente visual.

## Hard Rules

- Paleta cerrada: solo los 12 tokens de `references/palette.md`, cada uno con su par de texto definido. Prohibido azul, verde o gris frío; prohibido negro puro y blanco puro.
- Todo par texto/fondo debe cumplir contraste AA mínimo.
- Proporción 60% crema / 25% ink / 10% rojo / 5% dorado. Rojo solo en acciones y acentos puntuales, nunca en fondos grandes; dorado como detalle de lujo.
- Hover: bajar la opacidad del mismo token (p. ej. primario al 80%), nunca inventar un color nuevo.
- Sombras suaves; tarjetas con ring de 1px en el color de borde.
- Tipografía: máximo dos familias — Playfair Display en títulos, Inter en texto.
- Botones: min-height 40px, max-height 56px, padding-x 16–32px, texto 14–18px. CTA principal: max-width 320px en desktop, full-width solo en móvil.
- Centrado solo en hero, encabezados de página, estados vacíos y confirmaciones. Listados, tarjetas, formularios, tablas y textos largos alineados a la izquierda; en tarjetas el CTA va abajo.
- Desviación de color: si el usuario propone un color fuera de la paleta, preguntar "¿Seguro que querés usar X en vez del token Y? (sí/no)" y esperar la respuesta antes de aplicar; sin respuesta, no proceder.

## Decision Gates

| Pregunta | Acción |
|---|---|
| ¿El cambio toca CSS o templates? | Leer `references/palette.md` y mapear cada elemento a un token antes de escribir. |
| ¿El usuario pide un color fuera de la paleta? | Pregunta sí/no bloqueante; aplicar solo con "sí" y dejar constancia en el reporte. |
| ¿Hay texto sobre fondo oscuro (ink)? | Usar el par ink/crema claro definido. |
| ¿Es un botón? | Aplicar las reglas de tamaño; si es el CTA principal, max-width 320px en desktop. |
| ¿Es texto largo, tabla o formulario? | Alinear a la izquierda; nunca centrar. |

## Execution Steps

1. Leer `references/palette.md` (tokens con sus pares, dónde usar cada uno, fondo decorativo, tipografía).
2. Mapear cada elemento visual a un token y verificar su par de texto y contraste AA.
3. Aplicar las reglas de tamaño de botón y centrado.
4. Verificar la UI en navegador real con Playwright antes de dar el cambio por hecho.
5. Reportar según el Output Contract.

## Output Contract

Reportar: elementos modificados con su token asignado, desviaciones de color aprobadas por el usuario (si las hubo) y resultado de la verificación visual en navegador.

## References

- `references/palette.md` — spec de color completo: 12 tokens con oklch, hex y par de texto; dónde usar cada uno; proporciones y tonalidades; fondo decorativo; tipografía.
