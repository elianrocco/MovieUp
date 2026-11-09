# Tasks

## 1. Hero rotatorio en la portada

- [x] 1.1 Agregar en `movie_up/core/views.py` el contexto `hero_peliculas` (hasta 3 películas con `en_cartelera=True` ordenadas por `-fecha_estreno`, conservando `hero_pelicula`) y cubrirlo con un test nuevo en `core/tests.py` que verifique que el hero recibe las tres en orden; verificar con `docker compose exec web python movie_up/manage.py test core.tests.HomeViewTests.test_hero_context_contains_three_most_recent_movies_in_order --noinput`.
- [x] 1.2 Adaptar `movie_up/templates/includes/pelicula_hero.html` para renderizar un slide por película conservando el markup actual cuando llega una sola, y actualizar `movie_up/templates/home.html` para pasar la lista y cargar `static/js/hero-carousel.js`; verificar con `docker compose exec web python movie_up/manage.py test --noinput core.tests.HomeViewTests compras.tests.CompraViewTests` (slides en orden y hero de compra intacto).
- [x] 1.3 Estilar los slides superpuestos y la transición lenta de desplazamiento hacia la izquierda (~1 s sobre `transform`) en `movie_up/static/css/components.css`, sin alterar el aspecto de la primera carga; verificar con `docker compose exec web python movie_up/manage.py test --noinput core.tests.HomeViewTests` y revisando que las clases del hero siguen presentes.
- [x] 1.4 Implementar `movie_up/static/js/hero-carousel.js` (ciclo de 7000 ms: sale el slide activo hacia la izquierda y entra el siguiente desde la derecha, ciclo 3→1, no-op con un solo slide); verificar con `HomeViewTests.test_home_loads_hero_carousel_script` y Playwright a 1280×900: rotación cada ~7 s, vuelta al primer slide, un único slide activo y consola sin errores.

## 2. Lista de entradas

- [ ] 2.1 Reordenar `movie_up/entradas/templates/entradas/list.html`: encabezado `Mis entradas` centrado en panel dorado dentro del mismo contenedor de ancho que las tarjetas, y filas de cada tarjeta (título sin etiqueta; estado con etiqueta; fecha y hora de inicio con etiqueta; sala, fila y asiento en una fila con sus etiquetas) con los textos de estado `Sin usar`/`Usada`; verificar con `python movie_up/manage.py test entradas`.
- [ ] 2.2 Agregar en `movie_up/entradas/static/entradas/css/entradas.css` el panel del encabezado (mismo ancho que las tarjetas, alto delgado), la columna de filas por tarjeta y el margen pequeño entre filas y elementos de la fila; verificar con los tests de estructura de `entradas/tests.py` en verde.
- [ ] 2.3 Actualizar en `movie_up/entradas/tests.py` las aserciones `Pendiente de validación` → `Sin usar` y agregar tests de estructura del listado (panel dorado del encabezado, orden de filas, fila de sala/fila/asiento, ausencia de `Validada`); verificar con `manage.py test entradas` en verde.

## 3. Detalle de entradas

- [ ] 3.1 Reestructurar `movie_up/entradas/templates/entradas/detail.html`: etiqueta fuera y arriba de cada panel blanco, fila `[Sala][Fila][Asiento]` y fila `[Tipo de sala][Tipo de sonido][Capacidad]` con margen mediano, título de la película fuera de los paneles y estado `Sin usar`/`Usada`; verificar con `manage.py test entradas`.
- [ ] 3.2 Estilar en `movie_up/entradas/static/entradas/css/entradas.css` los paneles blancos por dato, las dos filas agrupadas y el alto compartido de `Volver a mis entradas` y `Reembolso` (`min-height` dentro del rango 40–56 px); verificar con los tests de estructura de `entradas/tests.py`.
- [ ] 3.3 Actualizar y ampliar `movie_up/entradas/tests.py` en el detalle (texto de estado nuevo, paneles blancos por dato, las dos filas agrupadas y clases de alto común en los botones); verificar con `manage.py test entradas` en verde.

## 4. Vista de compra exitosa

- [ ] 4.1 Envolver mensaje y botón de `movie_up/templates/compras/compra_exitosa.html` en un único `div.panel.panel--light` centrado, ajustando `movie_up/static/css/compras.css` solo si hace falta; verificar con `python movie_up/manage.py test compras`.
- [ ] 4.2 Agregar en `movie_up/compras/tests.py` una aserción de que mensaje y botón quedan dentro del panel blanco y se conserva el orden mensaje→botón; verificar con `manage.py test compras` en verde.

## 5. Verificación integral

- [ ] 5.1 Correr la suite completa `python movie_up/manage.py test --noinput peliculas salas funciones cuentas entradas compras core estadisticas chatbot` con 0 fallos, `manage.py check` con 0 errores y `manage.py makemigrations --check` sin cambios.
- [ ] 5.2 Verificar en Playwright a 1280×900: en la portada la rotación avanza cada 7 s con transición hacia la izquierda; en `/entradas/` el panel del encabezado y el orden de filas; en el detalle las dos filas agrupadas, los paneles blancos y los botones de igual alto; en la compra exitosa un único panel blanco; consola sin errores y captura completa guardada en `.playwright-mcp/`.

## Workflow follow-up

- Revisar los artefactos con el usuario y, tras `openspec validate --specs --strict`, archivar el change con `/opsx-archive`.
- Ninguna operación de Git sin autorización explícita del usuario.
