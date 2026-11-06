# Tasks

## 1. Services de estadísticas

- [x] 1.1 Implementar en `movie_up/estadisticas/services.py` el cálculo de periodos — semana lunes→domingo en hora Argentina con los días ya pasados de la semana en curso incluidos, mes y año de calendario, fronteras `[inicio, fin)` — y una única query que cubra el año calendario y la semana completa aunque esta cruce diciembre/enero, de la que se derivan los tres modos; verificar con tests de bordes de periodo (semana en curso completa, cambio de mes y de año, funciones fuera del periodo excluidas).
- [x] 1.2 Implementar las agregaciones de `build_estadisticas()` — recaudación por género con `Decimal` (`entradas_compradas × precio_entrada` por función), entradas y recaudación por película calculadas por función y sumadas, todos los géneros registrados presentes aunque estén en $0, funciones inactivas incluidas, orden por recaudación desc con desempate por título y `es_lider` en la primera fila; verificar con tests de agregación (incluida una función no activa que aporta a sus totales y el estado vacío sin películas).
- [x] 1.3 Implementar `altura_barra()` con el paso de 2% del alto de pantalla por cada 2000 de recaudación, tope de 30vh y mínimo visible para $0; verificar con tests que una recaudación baja da una barra pequeña, que doble recaudación da altura proporcional y que ninguna altura supera el tope.

## 2. Tab habilitado y panel en /gestion/

- [x] 2.1 Habilitar el botón `Estadísticas` en `movie_up/templates/includes/management_subnav.html` (quitar `disabled`, `aria-disabled` y la clase `--disabled`; agregar `data-management-tab="statistics"`) y actualizar `movie_up/core/tests.py::test_dashboard_prerenders_all_three_listings_and_five_controls` para esperar 4 tabs; verificar con `python movie_up/manage.py test core` que pasa sin errores.
- [x] 2.2 Crear `movie_up/estadisticas/templates/estadisticas/_panel.html` con los bloques de gráfico pre-renderizados para los tres periodos, incluirlo en `gestion.html` dentro de `<section data-management-panel="statistics" hidden>` y pasar el contexto de `build_estadisticas()` desde `gestion()`; verificar con un test de vista que `/gestion/` responde 200 con el panel y los tres periodos presentes y el botón habilitado.

## 3. Gráfico Common Baseline Bar Chart

- [x] 3.1 Construir el marcado y los estilos del gráfico dentro de `_panel.html` + CSS propio de la app (panel blanco, una columna por género con total arriba, barra y nombre debajo de la línea base, barras `--gold`, `max-width: 10vw` con columnas flexibles y zona de plot de 30vh); verificar con tests de plantilla que cada género registrado tiene su barra, que el total aparece encima y el género debajo, que las barras usan la clase dorada y que la altura calculada respeta el tope.
- [x] 3.2 Verificar con Playwright desktop (1280×900) que todas las barras caben en el gráfico sin scroll con varios géneros y que ninguna supera el 10% del ancho de pantalla; dejar captura en `.playwright-mcp/` y la consola sin errores.

## 4. Listado de películas y distintivo

- [x] 4.1 Construir el listado en `_panel.html` + CSS: cada película en un panel blanco `--surface` con márgenes en todos sus lados, título/género/entradas/recaudación en una sola línea, orden ya servido por el service con el distintivo dorado en la primera fila y estado vacío cuando no hay películas; verificar con tests de plantilla que los cuatro datos aparecen juntos, que el distintivo está en la película líder y que el formato de moneda sigue la convención existente del resumen de compra.
- [x] 4.2 Verificar con Playwright desktop la fila del listado con sus cuatro datos en una línea y el distintivo dorado en la película con más recaudación; captura en `.playwright-mcp/` con consola limpia.

## 5. Selector de periodo semanal, mensual y anual

- [x] 5.1 Agregar el botón `.stats-switch` alineado a la derecha entre la zona de gráficos y la de listados, con su JS `estadisticas/static/estadisticas/js/periodos.js` que cicla semanal → mensual → anual → semanal, alterna los bloques `[data-stats-period]` y actualiza la etiqueta con el modo actual; verificar con tests de plantilla que el botón existe, que hay tres bloques por zona y que la etiqueta inicial indica el modo semanal.
- [x] 5.2 Verificar con Playwright desktop que al hacer clic en el switcher cambian gráfico y listado juntos, que la etiqueta recorre los tres modos y que la URL permanece en `/gestion/` durante todo el recorrido; capturas de cada modo en `.playwright-mcp/` con consola sin errores.

## 6. Integración

- [x] 6.1 Correr la suite completa `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas compras core estadisticas`; verificar que todos los tests pasan.
- [x] 6.2 Correr `docker compose exec web python movie_up/manage.py check` y `docker compose exec web python movie_up/manage.py makemigrations --check --dry-run`; verificar que no hay errores del sistema ni migraciones pendientes.

## 7. Verificación final desktop

- [x] 7.1 Repetir el recorrido completo en Playwright **solo desktop** (1280×900): `/gestion/` → clic `Estadísticas` (panel visible, URL intacta) → gráfico → listado → switcher en sus tres modos → capturas nuevas en `.playwright-mcp/` con consola sin errores.
