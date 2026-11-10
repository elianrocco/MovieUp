# Tasks

## 1. Hero rotatorio en la portada

- [x] 1.1 Agregar en `movie_up/core/views.py` el contexto `hero_peliculas` (hasta 3 películas con `en_cartelera=True` ordenadas por `-fecha_estreno`, conservando `hero_pelicula`) y cubrirlo con un test nuevo en `core/tests.py` que verifique que el hero recibe las tres en orden; verificar con `docker compose exec web python movie_up/manage.py test core.tests.HomeViewTests.test_hero_context_contains_three_most_recent_movies_in_order --noinput`.
- [x] 1.2 Adaptar `movie_up/templates/includes/pelicula_hero.html` para renderizar un slide por película conservando el markup actual cuando llega una sola, y actualizar `movie_up/templates/home.html` para pasar la lista y cargar `static/js/hero-carousel.js`; verificar con `docker compose exec web python movie_up/manage.py test --noinput core.tests.HomeViewTests compras.tests.CompraViewTests` (slides en orden y hero de compra intacto).
- [x] 1.3 Estilar los slides superpuestos y la transición lenta de desplazamiento hacia la izquierda (~1 s sobre `transform`) en `movie_up/static/css/components.css`, sin alterar el aspecto de la primera carga; verificar con `docker compose exec web python movie_up/manage.py test --noinput core.tests.HomeViewTests` y revisando que las clases del hero siguen presentes.
- [x] 1.4 Implementar `movie_up/static/js/hero-carousel.js` (ciclo de 7000 ms: sale el slide activo hacia la izquierda y entra el siguiente desde la derecha, ciclo 3→1, no-op con un solo slide); verificar con `HomeViewTests.test_home_loads_hero_carousel_script` y Playwright a 1280×900: rotación cada ~7 s, vuelta al primer slide, un único slide activo y consola sin errores.

## 2. Lista de entradas

- [x] 2.1 Ajustar `movie_up/entradas/templates/entradas/list.html`: centrar todo el contenido y el botón `Ver entrada`; mostrar Estado e Inicio juntos con etiquetas arriba, seguido de la fila Sala/Fila/Asiento; conservar el título sin etiqueta y los estados `Sin usar`/`Usada`; verificar con `EntradaViewTests`.
- [x] 2.2 Ajustar `movie_up/entradas/static/entradas/css/entradas.css`: mantener las filas dentro del tercio central; usar el máximo gap que no toque los tercios laterales (`5.375rem` a 1280px con los datos reales; `1rem` hasta 600px) e implementar wrap como resguardo; verificar los límites en Playwright.
- [x] 2.3 Actualizar los tests de listado para la fila Estado/Inicio compartida, etiquetas sobre valores, centrado estructural y ausencia de los estados antiguos; verificar con `EntradaViewTests`.

## 3. Detalle de entradas

- [x] 3.1 Reestructurar `movie_up/entradas/templates/entradas/detail.html`: etiqueta fuera y arriba de cada panel blanco, fila `[Sala][Fila][Asiento]` y fila `[Tipo de sala][Tipo de sonido][Capacidad]` con margen mediano, título de la película fuera de los paneles y estado `Sin usar`/`Usada`; verificar con `docker compose exec web python movie_up/manage.py test --noinput entradas.tests.EntradaViewTests`.
- [x] 3.2 Hacer que `.detalle__valor` llene el ancho de su columna sin sobrepasar el margen interior dorado; centrar etiquetas y valores quitando `justify-items:center` de `.detalle__item`; verificar anchuras y centrado en Playwright.
- [x] 3.3 Actualizar y ampliar `movie_up/entradas/tests.py` en el detalle (texto de estado nuevo, paneles blancos por dato, las dos filas agrupadas y clases de alto común en los botones); verificar con `docker compose exec web python movie_up/manage.py test --noinput entradas.tests.EntradaViewTests` en verde.

## 4. Vista de compra exitosa

- [x] 4.1 Envolver mensaje y botón de `movie_up/templates/compras/compra_exitosa.html` en un único `section.panel.panel--light` centrado, ajustando `movie_up/static/css/compras.css`; verificar con `docker compose exec web python movie_up/manage.py test --noinput compras.tests.CompraExitosaTests`.
- [x] 4.2 Agregar en `movie_up/compras/tests.py` una aserción de que mensaje y botón quedan dentro del panel blanco y se conserva el orden mensaje→botón; verificar con `docker compose exec web python movie_up/manage.py test --noinput compras.tests.CompraExitosaTests` en verde.

## 5. Verificación integral

- [x] 5.1 Correr la suite completa `docker compose exec web python movie_up/manage.py test --noinput peliculas salas funciones cuentas entradas compras core estadisticas chatbot` con 0 fallos, `manage.py check` con 0 errores y `manage.py makemigrations --check` sin cambios.
- [x] 5.2 Verificar en Playwright a 1280×900: en `/entradas/` las filas permanecen dentro del tercio central, con gap medido de 86px y wrap para viewport angosto; en el detalle los `dd` ocupan todo el ancho de columna dentro del padding dorado y etiquetas/valores están centrados; el resto de las vistas continúa correcto; consola sin errores y capturas guardadas en `.playwright-mcp/entries-list-max-gap.png`, `entries-detail-full-width.png` y `compra-exitosa-final.png`.

## Workflow follow-up

- Revisar los artefactos con el usuario y, tras `openspec validate --specs --strict`, archivar el change con `/opsx-archive`.
- Ninguna operación de Git sin autorización explícita del usuario.
