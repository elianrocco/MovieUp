# Proposal

## Why

La portada muestra siempre la misma película en el rectángulo principal y las vistas de entradas y de compra exitosa presentan sus datos en un layout poco legible: la información de cada entrada se mezcla en una sola fila flexible, el detalle no agrupa los campos relacionados y los textos de estado no usan un lenguaje claro para el usuario. Conviene renovar la estética de estas cuatro vistas para dar más protagonismo a la cartelera y ordenar la información de las entradas.

## What Changes

- El rectángulo principal (hero) de la página principal rota automáticamente entre las tres películas en cartelera con fecha de estreno más reciente: cada 7 segundos el contenido de la siguiente película desplaza hacia la izquierda el anterior, con una transición lenta, en orden de estreno descendente cíclico.
- En `/entradas/`, el encabezado `Mis entradas` pasa a estar centrado dentro de un panel dorado del mismo ancho que las tarjetas de entrada y de alto delgado. Todo el contenido de cada tarjeta, incluido `Ver entrada`, queda centrado. Cada tarjeta muestra el título sin etiqueta; debajo, estado e inicio en la misma fila con sus etiquetas sobre los valores; y luego sala, fila y asiento en una fila con sus etiquetas. Ambas filas usan el máximo espacio horizontal que cabe dentro del tercio central de la tarjeta; en pantallas o datos más anchos, se reacomodan sin invadir los tercios laterales.
- El texto del estado de una entrada cambia de `Pendiente de validación`/`Validada` a `Sin usar`/`Usada` en el listado y en el detalle.
- En `/entradas/<id>/`, la fila con sala, fila y asiento y la fila con tipo de sala, tipo de sonido y capacidad se muestran cada una en una sola línea con un margen mediano entre elementos; cada dato va en su propio panel blanco que ocupa el ancho disponible de su columna sin sobrepasar el margen interior del panel dorado, con etiqueta y valor centrados y la etiqueta fuera del panel, arriba del valor, excepto el título de la película; y el botón `Reembolso` iguala su alto al de `Volver a mis entradas`.
- La vista de compra exitosa envuelve mensaje y botón `Mis entradas` en un único panel blanco.

## Capabilities

### New Capabilities

- Sin capacidades nuevas.

### Modified Capabilities

- `ui`: el requisito del hero de la página principal pasa de mostrar una única película destacada a rotar automáticamente entre las tres películas en cartelera más recientes con transición lateral.
- `entradas`: cambia la presentación del listado (encabezado en panel dorado, orden de filas por tarjeta y etiquetas), cambia la presentación del detalle (agrupación en filas, paneles blancos por dato con etiqueta fuera, igualdad de alto de botones) y cambia el texto de estado (`Sin usar`/`Usada`).
- `compras`: la vista de compra realizada envuelve todo su contenido en un único panel blanco.

## Impact

- **Código afectado:** `movie_up/core/views.py` (contexto del hero), `movie_up/templates/includes/pelicula_hero.html`, `movie_up/templates/home.html`, `movie_up/static/css/components.css` (estilos del hero) y un JS nuevo de rotación en `movie_up/static/js/`; `movie_up/entradas/templates/entradas/list.html`, `movie_up/entradas/templates/entradas/detail.html`, `movie_up/entradas/static/entradas/css/entradas.css`; `movie_up/templates/compras/compra_exitosa.html` y `movie_up/static/css/compras.css`.
- **Tests:** `core/tests.py` (hero), `entradas/tests.py` (textos de estado y estructura), `compras/tests.py` (página de éxito). No se esperan cambios de modelos, migraciones ni endpoints.
- **Sin dependencias nuevas:** la rotación se implementa con HTML/CSS/JS del propio proyecto, sin librerías externas.
- **Fuera de alcance:** el grid de películas de la portada, la vista de selección de asientos, la validación en puerta y cualquier regla de negocio.
