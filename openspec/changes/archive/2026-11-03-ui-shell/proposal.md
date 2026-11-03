# Proposal

## Why

La web no tiene portada ni navegación compartida: `/` responde 404, cada vista es un documento aislado sin nav ni footer, y el administrador no tiene una vista de gestión central (llega por URL directa o por `/admin/` de Django). Además, las rutas CRUD de películas, salas y funciones están sin protección: cualquier visitante anónimo puede crear, editar o borrar registros.

## What Changes

- **Nav global único** presente en todas las vistas: logo (placeholder para una imagen que cargará el autor) pegado a la izquierda del nombre "MovieUp" centrado; a la derecha, enlace `Login` e icono circular; tras iniciar sesión, el icono muestra la foto de cuenta que carga el sistema, aparece el nombre del usuario y `Login` se convierte en `Logout`; si la cuenta es común (no administradora), un botón en forma de ticket dorado a la izquierda de `Logout` lleva al listado de sus entradas.
- **Footer global** en toda vista: nombre del autor (Elian) y aclaración de proyecto educativo sin fines de lucro, con el módulo de pago existente con propósito de aprendizaje y no de negocio.
- **Página principal (`/`)** para visitantes y cuentas comunes: rectángulo horizontal centrado (un poco más de la mitad del alto, tres cuartos del ancho) con la portada de la película en cartelera de estreno más reciente y, en su sector inferior izquierdo, título, descripción, género, clasificación y los botones `Trailer` (URL del tráiler) y `Comprar entradas`; debajo, en filas de hasta 3, el grid de todas las películas en cartelera (incluida la más reciente) con portada, título, género y clasificación dentro de la tarjeta y los botones `Trailer` y `Comprar entradas` fuera, justo debajo.
- **Gating de compra**: `Comprar entradas` sin sesión iniciada no permite el acceso y redirige al inicio de sesión.
- **Control de acceso por rol en la portada**: un administrador no puede acceder a la página principal y es redirigido a la vista de gestión.
- **Vista de gestión central (`/gestion/`)** solo para el personal, con subNAV de 5 botones repartidos parejos (Películas seleccionado por defecto, Funciones, Salas, Cuentas, Estadísticas) visible en todo momento; los botones cargan en el cuerpo de la misma vista, sin cambiar la URL, el contenido del listado correspondiente; `Cuentas` muestra el panel de cuentas de Django con el shell de la web (navs, footer y paleta); `Estadísticas` existe como botón pero su vista queda fuera de este cambio.
- **BREAKING**: las cuatro rutas CRUD (listado, detalle, formulario y borrado) de películas, salas y funciones pasan a aceptar solo al personal autorizado; hoy están abiertas para cualquier visitante.

## Capabilities

### New Capabilities

- `ui`: comportamiento del shell visual de la web — nav global con sus estados de sesión, footer global, página principal (hero, grid, estados de compra) y vista de gestión central con subNAV, más las redirecciones por rol que gobiernan el acceso a la portada y a la gestión.

### Modified Capabilities

- `movies`: nuevo requisito de acceso restringido al personal en las rutas de listado, detalle, formulario y borrado, con rechazo de cuentas comunes y visitantes.
- `salas`: ídem (acceso restringido al personal en sus cuatro rutas).
- `funciones`: ídem (acceso restringido al personal en sus cuatro rutas).

## Impact

- **`movie_up/core/`**: nuevas vistas para `/` (home) y `/gestion/` (dashboard), rutas en `urls.py`, y settings con `STATICFILES_DIRS` y `TEMPLATES['DIRS']` para los assets globales y el base template.
- **`movie_up/peliculas/views.py`, `salas/views.py`, `funciones/views.py`**: decoradores de control de acceso (hoy ninguno) — cierra un agujero de seguridad real.
- **Templates**: nuevo base template con nav y footer; los 15 templates existentes pasan a extenderlo; overrides de templates del admin de Django para `Cuentas`.
- **`movie_up/static/`** (nuevo): CSS/JS globales del sistema de diseño regido por la skill `ui-design`.
- **`movie_up/cuentas/`**: donde se persista la foto de Google del nav (decisión de diseño).
- **Tests**: cobertura de redirecciones por rol y del gating de compra en cada app afectada; verificación visual en navegador real antes de dar las vistas por hechas.
- **Sin cambios de modelo de película**: `Pelicula` ya expone `imagen_portada`, `genero`, `clasificacion`, `descripcion`, `fecha_estreno` y `url_trailer`.
