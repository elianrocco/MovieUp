# Tasks

## 1. Infraestructura visual

- [x] 1.1 Crear `movie_up/static/` con `css/`, `js/` e `img/` y registrar `STATICFILES_DIRS = [BASE_DIR / 'static']` en `core/settings.py`; verificar con `manage.py findstatic css/tokens.css` que resuelve dentro de la nueva carpeta.
- [x] 1.2 Crear `movie_up/static/css/tokens.css` con los 12 tokens oklch y sus pares de texto de `.opencode/skills/ui-design/references/palette.md`; verificar que cada variable coincide 1:1 con la tabla del reference.
- [x] 1.3 Registrar `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']` y crear `movie_up/templates/base.html` con `{% load static %}`, las fuentes Playfair Display e Inter, los bloques `title`/`head`/`content`/`scripts` y los contenedores de nav y footer; verificar con `manage.py check` y con la suite completa en verde (nadie extiende el template todavía).
- [x] 1.4 Agregar `'core'` a `INSTALLED_APPS` para que el discovery de tests alcance `movie_up/core/tests.py`; verificar con `manage.py test core` que termina con exit 0 sin error de discovery.

## 2. Shell global: nav, footer y foto

- [x] 2.1 Implementar el nav en `base.html` según el requisito "Nav global con estados de sesión" (nombre "MovieUp" centrado con el logo a su izquierda, `Login`/`Logout`, foto y nombre debajo del icono, ticket dorado solo para comunes hacia `/entradas/`); verificar con tests en `core/tests.py` que cubren los tres estados y el clic del ticket, ejecutados con `manage.py test core`.
- [x] 2.2 Implementar el footer en `base.html` con el nombre "Elian" y el aviso de proyecto educativo sin fines de lucro; verificar con test en `core/tests.py` que aparece en una vista existente.
- [x] 2.3 Refactorizar los 15 templates existentes (list/detail/form/confirm_delete de películas, salas y funciones, más los de entradas) para que extiendan `base.html` con sus bloques, moviendo los CSS propios a `{% block head %}`; verificar con la suite completa en verde y con Playwright en vistas representativas de las 4 apps (nav y footer visibles, sin errores de consola).
- [x] 2.4 Agregar el campo `foto_url` a `Cuenta` con su migración, poblarlo desde el proveedor de Google al iniciar sesión y usarlo en el nav con marcador de posición cuando esté vacío; verificar con `manage.py makemigrations --check --dry-run` (sin cambios pendientes tras aplicar la migración) y con tests en `cuentas/tests.py` (poblado y fallback) ejecutados con `manage.py test cuentas`.
- [x] 2.5 Actualizar el comando de tests de `AGENTS.md` para incluir `core`; verificar que el comando documentado ejecuta la suite completa con exit 0.

## 3. Página principal

- [ ] 3.1 Crear la vista `home` en `movie_up/core/views.py`, la ruta `path('')` en `core/urls.py` y `movie_up/templates/home.html` (extiende `base.html`) con el hero: rectángulo centrado de poco más de la mitad del alto y tres cuartos del ancho, portada de la película en cartelera de mayor `fecha_estreno` y contenido (título, descripción, género, clasificación, `Trailer`, `Comprar entradas`) en el sector inferior izquierdo; verificar con tests en `core/tests.py` (selección, filtro `en_cartelera`, estado vacío, visitante y común con 200, administrador redirigido a `/gestion/`) ejecutados con `manage.py test core`.
- [ ] 3.2 Implementar el grid bajo el hero (solo `en_cartelera`, filas de hasta 3, tarjetas de la mitad del alto y un cuarto del ancho del hero, portada con título/género/clasificación dentro y `Trailer`/`Comprar entradas` fuera, justo debajo); verificar con tests en `core/tests.py` (exclusión de no-cartelera, reparto en filas de hasta 3, botones fuera del rectángulo).
- [ ] 3.3 Cablear `Trailer` (a `url_trailer` desde el hero y las tarjetas) y `Comprar entradas` (sin sesión → login conservando `?next=`; con sesión → sin destino, decisión D8); verificar con tests en `core/tests.py` para ambos estados.
- [ ] 3.4 Verificar la página principal en navegador real con Playwright como visitante y como cuenta común (hero, grid y gating de compra), comprobando que no hay errores de consola.

## 4. Control de acceso a los CRUD

- [x] 4.1 Crear `movie_up/core/decorators.py` con `staff_required` (anónimo → pantalla de inicio de sesión conservando `?next=`; autenticado no-staff → `/`); verificar con tests en `core/tests.py` que cubren los tres caminos (anónimo, común, personal).
- [x] 4.2 Aplicar `staff_required` a las 5 funciones de `movie_up/peliculas/views.py`; verificar con tests en `peliculas/tests.py` (rechazo de visitante y común en las cuatro rutas sin modificar el registro, acceso normal del personal) ejecutados con `manage.py test peliculas`.
- [x] 4.3 Aplicar `staff_required` a las 5 funciones de `movie_up/salas/views.py`; verificar con tests en `salas/tests.py` con el mismo patrón que 4.2, ejecutados con `manage.py test salas`.
- [x] 4.4 Aplicar `staff_required` a las 5 funciones de `movie_up/funciones/views.py`; verificar con tests en `funciones/tests.py` con el mismo patrón que 4.2, ejecutados con `manage.py test funciones`.

## 5. Vista de gestión

- [ ] 5.1 Crear la vista `gestion` en `movie_up/core/views.py`, la ruta `path('gestion/')` y `movie_up/templates/gestion.html` (extiende `base.html`) protegidos con `staff_required`, con el subNAV de 5 botones repartidos parejos (`Películas` por defecto, `Cuentas` apuntando a `/admin/`); verificar con tests en `core/tests.py` (anónimo → login, común → `/`, administrador → 200 con subNAV y listado de películas por defecto) ejecutados con `manage.py test core`.
- [ ] 5.2 Extraer el contenido de los listados existentes a un parcial por app (`_listado.html`), incluir los tres en `gestion.html` y agregar el JS que alterna la pestaña activa sin cambiar la URL ni recargar la página; verificar con tests de servidor (los tres parciales renderizan dentro de la gestión) y con Playwright: los clics en `Funciones` y `Salas` cambian el cuerpo y la URL permanece en `/gestion/`.
- [ ] 5.3 Crear el override `movie_up/templates/admin/base_site.html` que envuelve el admin con el nav global, el subNAV (`Cuentas` activo), el footer y la paleta de la web; verificar con smoke test de `/admin/` autenticado (renderiza con el shell y el CRUD de cuentas sigue funcionando) y con Playwright.
- [ ] 5.4 Dejar el botón `Estadísticas` presente en el subNAV sin vista asociada; verificar con test en `core/tests.py` que los cinco botones aparecen en la gestión.

## 6. Verificación de integración

- [ ] 6.1 Ejecutar `manage.py check` y `manage.py makemigrations --check --dry-run` con exit 0 (solo la migración de `foto_url` ya aplicada, nada pendiente).
- [ ] 6.2 Ejecutar la suite completa `manage.py test peliculas salas funciones cuentas entradas core` en verde.
- [ ] 6.3 Verificar E2E con Playwright por rol: visitante (`/` con hero y grid, clic `Comprar entradas` → login), cuenta común (ticket → `/entradas/`), administrador (en `/` redirige a `/gestion/`, tabs sin cambio de URL, `Cuentas` con el shell) sin errores de consola.
- [ ] 6.4 Ejecutar `openspec validate ui-shell --strict` con exit 0.

## Workflow follow-up

- Archivar el change con `/opsx:archive` tras la revisión del usuario, sincronizando `openspec/specs/ui/spec.md` y los deltas de `movies`, `salas` y `funciones` a las specs principales.
- Actualizar los árboles de estructura de `AGENTS.md` y `README.md` tras el archivado.
