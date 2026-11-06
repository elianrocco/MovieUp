# Proposal

## Why

El subNAV de `/gestion/` ya muestra el botón `Estadísticas` deshabilitado desde el shell de la UI, y el personal no tiene forma de consultar métricas de ventas (uso pendiente "Consultar métricas de ventas" del sistema). Se necesita el apartado de estadísticas completo: recaudación por género en un gráfico, listado de películas ordenado por recaudación y selector de periodo, todo dentro de `/gestion/` sin cambiar de URL.

## What Changes

- Se habilita el botón `Estadísticas` del subNAV de `/gestion/`: al precionarlo carga el apartado de estadísticas con el mismo mecanismo de paneles de los CRUDs (sin cambio de URL).
- Nuevo apartado dentro de un panel blanco con un **Common Baseline Bar Chart** de recaudación por género: una barra dorada por género registrado, ancho máximo 10% del ancho de pantalla que se reduce para que entren todas sin scroll, altura creciente por cada 2000 de recaudación con tope del 30% del alto de pantalla, nombre del género debajo de la línea base y total de recaudación (sin acotar) encima de cada barra.
- Nuevo listado de películas debajo del gráfico: cada película en un panel blanco con márgenes en todos sus lados y sus cuatro datos en una sola línea (título, género, entradas vendidas y recaudación), ordenado de mayor a menor recaudación, con distintivo dorado en la película líder.
- Nuevo botón de periodo a la derecha, entre el gráfico y el listado, que cicla semanal → mensual → anual en cada clic; solo cambia qué funciones se consideran (inicio dentro de la semana/mes/año en curso) para los cálculos del gráfico y del listado, sin cambiar la URL.
- Todos los cálculos consideran tanto las funciones activas como las inactivas.
- **Modificación del requisito de `ui`**: "Botón Estadísticas presente" pasa a describir un botón habilitado que abre el apartado sin cambiar la URL (la cláusula "su vista no se define en este cambio" queda falsa).

## Capabilities

### New Capabilities

- `estadisticas`: apartado de métricas de ventas dentro de `/gestion/` — habilitación del tab, gráfico de recaudación por género, listado de películas con distintivo, selector de periodo semanal/mensual/anual y reglas de cálculo (agregación por función, funciones activas e inactivas).

### Modified Capabilities

- `ui`: requisito "Botón Estadísticas presente" — el botón queda habilitado y abre el panel de estadísticas sin cambiar la URL, en lugar de ser un control deshabilitado cuya vista no está definida.

## Impact

- **Templates**: `movie_up/templates/includes/management_subnav.html` (botón habilitado con `data-management-tab="statistics"`), `movie_up/templates/gestion.html` (nueva sección `data-management-panel="statistics"` con el include del apartado).
- **Vista**: `movie_up/core/views.py` (`gestion()` agrega los datos de estadísticas al contexto vía services).
- **App `estadisticas`** (recién creada): `services.py` con el cálculo de periodos y agregaciones, `templates/estadisticas/_panel.html`, CSS/JS propios del apartado y `tests.py`.
- **JS existente sin tocar**: `management-tabs.js` alterna el tab nuevo con el mecanismo actual.
- **Tests existentes**: `core/tests.py::test_dashboard_prerenders_all_three_listings_and_five_controls` afirma `data-management-tab=` == 3 → pasa a 4.
- **Specs**: delta en `ui` (1 MODIFIED) y nueva capacidad `estadisticas` (ADDED).
- Sin migraciones de modelos; sin cambios en modelos ni en el cálculo de compras.
