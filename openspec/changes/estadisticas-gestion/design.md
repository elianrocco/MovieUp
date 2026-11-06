# Design

## Context

`/gestion/` es una sola página que pre-renderiza todos los listados (`gestion()` en `core/views.py`) y alterna paneles con `management-tabs.js` mediante el contrato `data-management-tab` ↔ `data-management-panel`, sin cambiar la URL. El botón `Estadísticas` del subNAV existe pero está deshabilitado (`management_subnav.html`). La app `estadisticas` recién creada tiene `services.py` vacío. Los datos a agregar viven en `Funcion` (`inicio`, `precio_entrada` Decimal, `entradas_compradas`, `funcion_activa`) y `Pelicula.genero` (texto libre, sin choices). `TIME_ZONE = America/Argentina/Buenos_Aires`. Ver proposal.md por el motivo.

## Goals / Non-Goals

**Goals:**
- Habilitar el tab `Estadísticas` reutilizando el mecanismo actual de paneles (cero cambios en `management-tabs.js`).
- Servir los tres periodos pre-renderizados en la misma carga de `/gestion/` y alternarlos con JS mínimo.
- Gráfico de barras en HTML/CSS puro con las unidades exactas que pide la spec (ancho en % de pantalla, tope en % de pantalla, línea base común).
- Agregaciones en un solo query derivado, con `Decimal` en todo el cálculo de dinero.

**Non-Goals:**
- Exportar datos, filtros por película/sala/idioma, o comparativas entre periodos.
- Persistir preferencia de periodo (al recargar vuelve a semanal).
- Soporte mobile (la app es solo PC).
- Modificar modelos o migrar datos.

## Decisions

### D1 — Integración del tab en `/gestion/`
Habilitar el botón en `templates/includes/management_subnav.html` quitando `disabled`, `aria-disabled` y la clase `--disabled`, y agregándole `data-management-tab="statistics"` (el contrato que `management-tabs.js` ya entiende → **el JS no se toca**). En `gestion.html` se agrega una `<section class="management-panel" data-management-panel="statistics" hidden>` con `{% include 'estadisticas/_panel.html' %}`. `gestion()` agrega los datos al contexto vía `estadisticas.services`.

*Alternativa descartada:* una vista propia en `/estadisticas/` — viola el requisito "sin cambiar de URL" y rompe el patrón de la sección.

### D2 — Pre-render de los 3 modos vs. fetch
Se pre-renderizan los tres periodos (semanal, mensual, anual) en el contexto de `gestion()` y un JS propio alterna la visibilidad de los bloques `[data-stats-period]`. *Alternativa descartada:* endpoint JSON + fetch — agrega red, estados de carga y manejo de errores sin beneficio observable (los datos son chicas). *Alternativa descartada:* query param + recarga — cambia la URL.

### D3 — API de `estadisticas/services.py`
- `build_estadisticas(ahora=None)` → `{'semanal': …, 'mensual': …, 'anual': …}`; cada periodo: `generos: [{genero, recaudacion, altura_vh}]` y `peliculas: [{titulo, genero, entradas, recaudacion, es_lider}]`.
- **Un solo query**: se traen las funciones con `inicio` dentro del año en curso (semana y mes en curso siempre caen dentro del año en curso) y los tres periodos se derivan filtrando en memoria — una query, tres modos.
- Helpers puros y testeables: `_rango_periodo(modo, ahora)` con fronteras `[inicio, fin)` en hora Argentina (semana = lunes 00:00 → lunes siguiente 00:00, **con los días ya pasados de la semana en curso incluidos — confirmado con el usuario**; mes y año = calendario), `altura_barra(recaudacion)` y las agregaciones por género/película.
- Dinero siempre en `Decimal` (`precio_entrada × entradas_compradas` por función, luego suma); el formato de presentación reutiliza la convención monetaria ya existente en el resumen de compra.

### D4 — Gráfico sin librería (HTML/CSS puro)
Estructura por columna: `[total] [barra]` sobre la línea base y `[género]` debajo de ella (`.stats-chart__baseline`).
- **Ancho**: columnas `flex: 1 1 0; min-width: 0` con `gap`, y `.stats-chart__bar { max-width: 10vw }` → con pocas barras llegan al tope de 10% del ancho; con muchas el flex las encoge automáticamente → **todas entran sin scroll** (más `overflow: hidden` en el panel como red de seguridad).
- **Altura**: zona de plot de `30vh` (el tope) y `altura_vh = min(30, recaudacion / 2000 × 2)` — "apenas un poquito" = **2% del alto de pantalla por cada 2000** (llega al tope a 30.000 de recaudación), con mínimo visible de 2px para géneros en $0. La constante `PASO_VH_POR_2000 = 2` vive en services, fácil de ajustar.
- El total de encima de la barra **no se acota** (spec): siempre muestra el valor real, aunque la barra esté en el tope.

*Alternativa descartada:* librería de gráficos (Chart.js, etc.) — no expresa el tope en unidades de viewport, impone su propio layout y agrega una dependencia nueva a `requirements.txt`.

### D5 — Selector de periodo
Un solo botón `.stats-switch` alineado a la derecha **entre** la zona de gráficos y la de listados, con `data-stats-switch`. `estadisticas/static/estadisticas/js/periodos.js` (~15 líneas) cicla `semanal → mensual → anual → semanal`, muestra/oculta los bloques `[data-stats-period]` de ambas zonas y actualiza la etiqueta con el modo actual. Estructura del DOM:3 gráficos apilados (1 visible), botón,3 listados apilados (1 visible) — así el botón queda visualmente entre gráfico y listado en cualquier modo, una sola vez en el DOM.

*Alternativa descartada:* reutilizar `management-tabs.js` — su contrato es del subNAV (tabs + paneles de gestión) y mezclarlo acoplaría ambas funcionalidades.

### D6 — Reglas de agregación
- **Géneros**: valores distintos de `Pelicula.genero` (campo libre) — aparece **todos** los géneros registrados aunque tengan $0 en el periodo.
- **Recaudación por género**: `Σ` sobre sus funciones en el periodo de `entradas_compradas × precio_entrada`.
- **Película**: entradas = `Σ entradas_compradas` de sus funciones en el periodo; recaudación = calcular por función y **luego sumar** (como pide el requisito).
- **Orden**: recaudación desc, desempate por título asc (orden estable). `es_lider` = primera fila → distintivo dorado (siempre que haya listado, aunque todas den $0); sin películas → estado vacío.
- **Inclusividad**: sin filtro `funcion_activa` — entran activas e inactivas (spec).

### D7 — Visual (paleta ui-design)
Paneles blancos = `--surface` (blanco puro prohibido por paleta), barras y distintivo `--gold` con texto `--on-gold`, etiquetas en `--text`/`--text-muted`. Botón del switcher con perfil `.btn--gold` (relleno dorado, legible sobre panel blanco). Estado vacío centrado, como en las demás vistas. Verificación **solo desktop 1280×900**.

### D8 — Estrategia de tests
- **Services**: bordes de periodo (semana lunes→domingo AR con días pasados incluidos; cambio de mes/año), una sola query deriva los 3 modos, agregación por género y por película con `Decimal`, altura con tope y paso, orden + desempate, distintivo, funciones inactivas incluidas, géneros en $0 presentes, estado vacío.
- **Vista/plantilla**: `/gestion/` 200 con el panel y los 3 periodos, botón sin `disabled`, `data-management-tab="statistics"` (actualizar `core/tests.py` de 3 a 4 tabs), contenido del gráfico y del listado, distintivo, switcher.
- **Playwright desktop**: clic en `Estadísticas` → panel visible y URL `/gestion/` intacta; ciclar el switcher; capturas en `.playwright-mcp/`.

## Risks / Trade-offs

- [Etiquetas de género encimadas con muchas barras o nombres largos] → columnas con `min-width: 0`, texto con `text-overflow: ellipsis` y `title` nativo como tooltip; el ancho se reduce antes que el scroll.
- [Tres agregaciones en cada carga de `/gestion/` mitigado a un solo query] → una query de funciones del año en curso + filtro en memoria; si la tabla crece mucho, futura partición por año (fuera de alcance hoy).
- [`precio_entrada` Decimal × entero] → todo el cálculo en `Decimal` con cuantización a 2 decimales solo al presentar; nunca `float`.
- [El test existente de `core` cuenta3 tabs] → actualizarlo a4 en la misma tarea que habilita el botón (rompería la suite si se hace en otro orden).
