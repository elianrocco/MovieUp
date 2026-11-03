# Paleta cinematográfica pastel — MovieUp

Spec de color completo de la interfaz. Las reglas duras (tamaño de botón, centrado, protocolo de desviación) viven en `../SKILL.md` y tienen prioridad ante cualquier contradicción de este archivo.

## Tokens

| Token | Valor | Uso | Texto encima |
|---|---|---|---|
| Fondo crema | oklch(0.95 0.045 90) ≈ #F6EDD3 | Fondo general de la página | — |
| Crema claro | oklch(0.985 0.018 90) ≈ #FCF8EC | Tarjetas y popovers | — |
| Texto principal (negro cálido) | oklch(0.24 0.015 20) ≈ #2B2224 | Texto principal; nunca negro puro | — |
| Rojo cine (primario) | oklch(0.6 0.14 22) ≈ #C8575A | Acción principal | blanco cálido oklch(0.99 0.005 80) |
| Rosa suave (secundario) | oklch(0.94 0.03 18) ≈ #F6E3E2 | Elementos suaves | rojo oscuro oklch(0.4 0.1 22) |
| Dorado | oklch(0.84 0.1 85) ≈ #E3C67D | Detalle de lujo | marrón oscuro oklch(0.3 0.05 70) |
| Dorado claro (acento) | oklch(0.9 0.07 88) ≈ #EFDDA6 | Acento claro | oklch(0.38 0.07 70) |
| Ink (negro sala) | oklch(0.23 0.012 20) | Bloques oscuros | oklch(0.97 0.01 80) |
| Fondo apagado | oklch(0.955 0.012 70) | Fondos neutros | — |
| Texto secundario | oklch(0.5 0.02 30) ≈ #6F625F | Metadatos y descripciones | — |
| Bordes e inputs | oklch(0.9 0.02 50) ≈ #E7DCD5 | Bordes, inputs, separadores | — |
| Anillo de foco | mismo rojo primario | focus-visible | — |

## Dónde usar cada color

- **Rojo:** botón principal de compra ("Comprar entradas"), el logo, la palabra destacada de la marca, subtítulos pequeños en mayúsculas con tracking amplio, hover de los títulos y la franja "Comprar" al pasar el cursor por una tarjeta. Es el color de acción: no usarlo en fondos grandes.
- **Ink:** nav (con backdrop-blur y borde inferior sutil), cartelera o hero de la película destacada, fondo de los pósters y cintas de película decorativas. Ahí el texto va en crema claro.
- **Dorado:** badges importantes (botón "Ver mis entradas"), el subtítulo en itálica serif dentro del hero y bordes finos sobre fondos oscuros (ring dorado al 40%). Usarlo poco, como detalle de lujo.
- **Rosa:** chips de horarios, etiquetas suaves y botones secundarios.
- **Crema:** fondo de la página y tarjetas.
- **Gris cálido (texto secundario):** metadatos como duración, género o clasificación y las descripciones.
- **Badges sobre imágenes:** fondo crema al 90% con texto oscuro.

## Tonalidades y proporciones

- Todo pastel y cálido: chroma baja o media, matices entre rojo (≈20) y amarillo (≈90). No usar azules, verdes ni grises fríos.
- Proporción aproximada: 60% crema, 25% ink (hero y pósters), 10% rojo, 5% dorado.
- Mantener contraste AA y usar siempre el par de color definido para cada fondo.
- Para hover, bajar la opacidad del mismo token (p. ej. primario al 80%) en lugar de inventar colores nuevos.
- Sombras suaves; en tarjetas, un ring de 1px con el color de borde.

## Fondo decorativo

- Sobre el crema, degradados radiales sutiles: uno más claro arriba, oklch(0.97 0.035 90), y uno más dorado abajo, oklch(0.9 0.05 80 / 0.6).
- Encima, una capa de grano de película (ruido SVG `feTurbulence` en tono marrón) con opacidad muy baja, para que se perciba sin ensuciar.
- Cintas de película verticales en ink a los costados, con perforaciones en crema y separadores de fotograma en dorado al 35%, todo con baja opacidad y sin interferir con el contenido.

## Tipografía

- Títulos en serif elegante (Playfair Display) y texto en sans (Inter). Máximo dos familias.
