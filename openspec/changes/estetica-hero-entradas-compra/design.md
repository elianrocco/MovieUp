# Design

## Context

La portada (`movie_up/templates/home.html`) renderiza un único hero mediante el include `includes/pelicula_hero.html` con la película más reciente en cartelera que pasa `core/views.py`; el include también lo reutiliza la página de compra con una sola película (`mostrar_compra=False`). `/entradas/` lista todas las filas de datos de cada entrada envueltas en una sola fila flexible dentro de una tarjeta dorada (`entradas/list.html` + `entradas/static/entradas/css/entradas.css`), el detalle muestra una lista `dl` plana dentro del panel dorado, y la página de compra exitosa centra mensaje y botón sin contenedor (`compras/compra_exitosa.html`). La motivación completa está en proposal.md; los comportamientos exigidos, en los deltas de `specs/ui`, `specs/entradas` y `specs/compras`.

## Goals / Non-Goals

**Goals:**
- Rotación automática del hero con desplazamiento lateral lento, sin librerías externas y sin romper el uso único del include en la página de compra.
- Reordenar lista y detalle de entradas con la estructura de filas pedida, reutilizando los componentes y tokens existentes (`.panel`, `.btn`, paleta `ui-design`).
- Mantener en verde la suite actual, ajustando solo las aserciones que fijaban textos o estructura viejos.

**Non-Goals:**
- Cambiar el grid de películas, la selección de asientos, la validación en puerta o cualquier regla de negocio.
- Agregar controles manuales (pausa, flechas, indicadores) al carrusel.
- Tocar modelos, migraciones, endpoints o la vista de gestión.

## Decisions

**D1 — El hero se pre-renderiza completo en el servidor, con hasta 3 slides.** `core/views.py` pasa además `hero_peliculas` (hasta 3 películas de `en_cartelera=True` ordenadas por `-fecha_estreno`) y el include renderiza un `<article class="hero__slide">` por película, cada uno con su portada, datos y botones propios. La página de compra sigue pasando una sola película: el include con un solo slide emite exactamente el markup actual, sin JS de rotación. *Alternativas:* cargar slides por AJAX (complejidad y parpadeo innecesarios), renderizar toda la cartelera en el hero (irrelevante: el alcance son las 3 más recientes), slider de librería externa (dependencia nueva sin necesidad).

**D2 — Rotación con JS propio y slides superpuestos.** Los slides se posicionan `absolute` sobre el alto del hero; cada 7000 ms el slide activo sale hacia la izquierda (`translateX(-100%)`) y el siguiente entra desde la derecha (`translateX(0)`), con una transición CSS de ~1000 ms (`transition` sobre `transform`, `ease`) — ese es el sentido "desplaza hacia la izquierda" pedido y funciona igual en el ciclo 3→1. Con 1 slide el script no hace nada; con 2, alterna. Script vanilla en `movie_up/static/js/hero-carousel.js`, cargado con `defer` solo desde `home.html`. *Supuestos registrados:* duración de la transición 1 s ("lenta") y ciclo exacto de 7 s; ninguno de los dos es observable en los tests salvo que se verifique en navegador. *Alternativa:* carrusel horizontal con `track` (`translateX` por índice) — descartada porque el ciclo 3→1 requiere clonar el primer slide o salto visible.

**D3 — Lista: contenedor único que fija el ancho compartido.** El encabezado `Mis entradas` y la `ul` de tarjetas pasan a vivir dentro de un contenedor con los márgenes horizontales actuales (`margin-inline: 10vw`), de modo que el panel dorado del encabezado y las tarjetas miden exactamente lo mismo sin magia de CSS. Dentro de cada `.entrada-card`, `.entrada-card__datos` deja de ser `flex-wrap` y se vuelve columna de filas: título (sin `.entrada-card__etiqueta`), estado, inicio, y una fila horizontal con sala/fila/asiento. Los textos de estado se cambian en `list.html` y `detail.html` (`activa ? Sin usar : Usada`). *Alternativa:* `grid-template-columns` por fila — más rígida para un único grupo de tres.

**D4 — Detalle: etiqueta fuera, valor en panel blanco propio.** Se conserva el panel dorado `panel panel--gold detalle` como contenedor y el `dl`; cada dato se compone como `detalle__campo` (etiqueta `dt` arriba, fuera) + `dd` estilado como panel blanco con su propio fondo y borde (token de superficie clara de la paleta `ui-design`, no blanco puro). Dos grupos pasan a filas horizontales con margen mediano (~1rem): `[Sala][Fila][Asiento]` y `[Tipo de sala][Tipo de sonido][Capacidad]`; el resto de los datos (código, estado, fecha y hora de inicio) queda apilado, uno por panel. Los dos botones comparten alto con un `min-height` único dentro del rango 40–56 px de `ui-design` (aplicado a `.detalle__acciones .btn`). *Alternativa:* paneles blancos como filas completas de ancho total — no satisface "misma fila con margen mediano".

**D5 — Compra exitosa: reutilizar `panel panel--light`.** El `section.exito` envuelve mensaje y botón en un único `div.panel.panel--light` (componente existente en `components.css`), centrado, conservando el orden DOM mensaje→botón que ya asertan los tests. *Alternativa:* clase nueva `.exito__panel` con estilos propios — solo si `panel--light` no alcanza; se prefiere reutilizar.

## Risks / Trade-offs

- El include del hero se comparte con `/compras/<id>/` → se mantiene compatible con un solo slide y se cubre con el test existente `test_hero_reuses_home_structure_without_buy_button`.
- Tests que fijaban textos viejos (`Pendiente de validación` en `entradas/tests.py`) y orden de elementos (`exito__mensaje` antes del botón en `compras/tests.py`) → se actualizan las aserciones conservando el comportamiento nuevo verificable.
- Rotación automática sin control de pausa (WCAG 2.2.2) → todo el contenido rotativo también existe de forma estática en el grid de la portada; un control de pausa quedaría como mejora futura si se pide.
- Superposición de slides con `position: absolute` puede filtrar contenido en viewports bajos → el alto del hero ya está definido por `.hero` y los slides heredan su caja; verificar en Playwright a 1280×900 y en una altura chica.

## Migration Plan

Sin migraciones ni cambios de datos. Se despliega junto con el resto del código y se revierte revertiendo los commits de templates/CSS/JS.

## Open Questions

- Ninguna: la ubicación de las etiquetas del detalle quedó resuelta con el usuario (fuera del panel, arriba del valor).