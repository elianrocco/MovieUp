# Tasks

## 1. Botón de validación en el nav

- [x] 1.1 Agregar en `movie_up/templates/includes/site_nav.html` el botón de validación al extremo izquierda del nav, con guard `{% if user.is_staff %}` y enlace a `{% url 'entradas:entrada_validar' %}`; verificar con tests de plantilla en `movie_up/core/tests.py` (junto a los de `Mis entradas`) de que la administradora ve el botón con ese enlace, la cuenta común no lo ve y el visitante no lo ve.
- [x] 1.2 Estilizar el botón en `movie_up/static/css/site-shell.css` dentro de la celda `grid-column: 1` con el par `--gold`/`--on-gold` y hover por opacidad (D3); verificar con `python movie_up/manage.py check` sin errores y con un test que el HTML del nav contiene la clase del botón dorado.

## 2. Presentación de la vista de validación

- [x] 2.1 Envolver el contenido de `movie_up/entradas/templates/entradas/validar.html` (encabezado, formulario, mensaje y `dl`) en un `.panel.panel--light` centrado horizontalmente con ancho acotado (D4); verificar con un test en `movie_up/entradas/tests.py` de que el `GET` de la vista muestra el panel centrado y que el mensaje y los datos de la entrada quedan dentro del mismo panel.
- [x] 2.2 Cambiar el botón de envío `Validar` a `class="btn btn--gold"` (D5); verificar con un test en `movie_up/entradas/tests.py` de que el formulario de la vista contiene esa clase.
- [x] 2.3 Presentar en `validar.html` cada dato de una entrada exitosa como etiqueta con `:` a la izquierda de su valor; agregar en `entradas.css` una grilla de dos columnas con separación vertical uniforme, etiquetas pequeñas en `--text-muted` y `dd` sin margen predeterminado; verificar con tests que cada etiqueta y dos puntos preceden a su valor y que todos los datos se renderizan.

## 3. Verificación integrada

- [x] 3.1 Correr la suite completa `python movie_up/manage.py test peliculas salas funciones cuentas entradas compras core estadisticas` con 0 fallos, `python movie_up/manage.py check` con 0 errores y `python movie_up/manage.py makemigrations --check` sin cambios pendientes.
- [x] 3.2 Verificar en navegador real con Playwright a 1280×900: login como administradora, botón dorado visible al extremo izquierda del nav (y ausente en una cuenta común), clic que conduce a `/entradas/validar/`, panel blanco centrado con el botón `Validar` en dorado, envío de un código de prueba cuyo resultado aparece dentro del panel, consola del navegador sin errores; guardar la captura en `.playwright-mcp/`.
- [x] 3.3 Verificar en Playwright a 1280×900 una validación exitosa: cada etiqueta con `:` aparece a la izquierda de su dato, las filas tienen una separación visual pequeña y uniforme y el resultado sigue dentro del panel; guardar la captura en `.playwright-mcp/validar-entradas-exito.png`.

## Workflow follow-up

- Revisar el cambio con el usuario y, tras su aprobación, archivarlo (`openspec validate --specs --strict` previo) actualizando los árboles de AGENTS.md y README.md.
