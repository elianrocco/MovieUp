# Proposal

## Why

Las páginas de detalle, formulario y borrado de películas, funciones y salas no usan el shell de la web: `peliculas/` renderiza sin clases ni estilos propios y `funciones/` y `salas/` cargan `salas.css`, un reset global que pisa la paleta, la tipografía y el fondo del sitio. Además, dentro de `/gestion/` las acciones Ver, Editar y Eliminar abandonan el panel hacia otra URL, y los botones `Login` y `Logout` del nav pasan por pantallas intermedias que no aportan al usuario.

## What Changes

- **Presentación de las páginas CRUD**: detalle, formulario y confirmación de borrado de películas, funciones y salas heredan el shell (nav, footer, paleta, tipografía) y presentan su información en una tarjeta centrada de ancho acotado, con el contenido alineado a la izquierda, los enlaces de acción convertidos en botones y el mensaje del servicio visible en el propio formulario.
- **Limpieza de `salas.css`**: se elimina `salas.css` por completo —incluido su reset global de tipografía Arial, fondo `#f6f7f9` y links azul— y sus estilos de componente migran a `forms.css`; los colores de celda `A` (asiento), `R` (reservado) y `P` (pasillo) se mantienen como excepción documentada a la paleta cerrada.
- **Operaciones CRUD dentro de la gestión**: en `/gestion/`, Ver, Editar, Eliminar y Crear cargan el contenido de su vista dentro de la pestaña activa, sin cambiar la URL ni recargar la página; un control `Volver al listado` regresa al listado de esa misma pestaña con datos frescos.
- **Editor de distribución operativo en ambos destinos**: el editor de butacas de `salas` se inicializa también dentro del panel, pinta sus celdas con los colores de pasillo, asiento y reservado, carga la distribución existente al editar y no la reemplaza cuando el usuario no la toca.
- **Formularios sin salir del panel**: los errores de validación del servicio se muestran dentro del panel sobre el mismo formulario; el éxito de crear, actualizar o eliminar devuelve a la lista de la pestaña.
- **Degradación sin JavaScript**: cada acción conserva un enlace real hacia las rutas existentes, que siguen funcionando como páginas completas.
- **Login directo con Google**: el botón `Login` del nav y el `Comprar entradas` sin sesión conducen al flujo de Google sin renderizar la pantalla intermedia de acceso.
- **Logout sin página intermedia**: el botón `Logout` cierra la sesión con un `POST` protegido por CSRF y redirige a la página principal.
- **BREAKING**: ninguna. Las rutas CRUD, la pantalla de acceso y el cierre de sesión siguen existiendo y respondiendo como hoy para el acceso directo y sin JavaScript.

## Capabilities

### New Capabilities

- Ninguna: la presentación y los flujos de acceso pertenecen a capacidades existentes.

### Modified Capabilities

- `ui`: MODIFIED del requisito "Gating de Comprar entradas" (ahora conduce al flujo directo de Google conservando el retorno); ADDED de presentación de las páginas CRUD, de operaciones de CRUD dentro de la gestión y de degradación sin JavaScript.
- `cuentas`: ADDED de inicio de sesión directo con Google desde cualquier punto de entrada y de cierre de sesión desde el nav sin página intermedia.

## Impact

- **`movie_up/static/css/`**: nuevo `forms.css` con tarjeta de página, campos, lista de detalle, tabla, grid de asientos y variantes de botón para superficie clara; `movie_up/salas/static/salas/css/salas.css` se elimina junto con sus cargas en los templates; en `components.css` se acota `.management-panel button` con `:not(.seat-grid__cell)` para que las celdas del editor conserven sus colores y su tamaño dentro del panel.
- **`movie_up/peliculas/`, `funciones/`, `salas/`**: plantillas de detalle, formulario y borrado divididas en parciales (`_detail.html`, `_form.html`, `_confirm_delete.html`) reutilizados por la página completa y por el panel de gestión.
- **`movie_up/*/views.py`**: modo fragmento en las vistas existentes (header `X-Panel-Request`) que alterna plantilla completa y parcial, y respuesta de listado en el éxito de un `POST`.
- **`movie_up/core/`**: guard de sesión vencida para peticiones de panel (401 con URL de retorno) y helpers de render de fragmentos.
- **`movie_up/static/js/`**: `management-panel.js` para la navegación interna del panel y refactor de `salas/js/grid.js` a un namespace `init(root)` —con guard de doble inicialización— para que el editor de butacas arranque tras cada intercambio.
- **`movie_up/templates/gestion.html`**: carga `salas/js/grid.js` una única vez, porque el fragmento no trae scripts y `innerHTML` no los ejecuta.
- **`movie_up/templates/includes/site_nav.html`**: `Login` apuntando al proveedor Google y `Logout` como formulario `POST` con token CSRF.
- **Tests**: se ajustan las aserciones que esperan `?next=/accounts/login/` y se agregan pruebas por operación de panel, por fragmento y por cierre de sesión.
- **Sin cambios de modelo, de servicios ni de rutas**: la lógica de negocio y el contrato de errores de los servicios quedan intactos.
