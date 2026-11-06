# Tasks

## 1. Base visual

- [x] 1.1 Crear `movie_up/static/css/forms.css` con la tarjeta de página, los campos, la lista de detalle, la tabla, los mensajes de error y las variantes de botón para superficie clara (`--neutral`, `--danger`, `--sm`) sobre los tokens, y enlazarlo en `templates/base.html` después de `components.css` — Verificación: `docker compose exec web python movie_up/manage.py check` termina con 0 errores y la página principal solicita el CSS nuevo con estado 200 en la pestaña Network.
- [x] 1.2 Migrar a `forms.css` los selectores de `salas.css` que consumen los listados de gestión (`.data-table`, `.button-link`, `.actions`, `.form-field`, `.error-message`, `.grid-controls`) reescritos con tokens — Verificación: `docker compose exec web python movie_up/manage.py test core` termina OK y `/gestion/` conserva el aspecto de sus tres listados en Playwright.
- [x] 1.3 Migrar `.seat-grid*` y `.celda--*` a `forms.css` conservando los hex aprobados (`A` `#1976d2`, `R` `#d4af37`, `P` `#888`), eliminar `movie_up/salas/static/salas/css/salas.css` y quitar sus `<link>` de los cuatro templates que lo cargan — Verificación: Playwright abre detalle y formulario de salas y de funciones sin tipografía Arial ni fondo `#f6f7f9`, el grid se pinta con los mismos colores y la consola no reporta errores; `docker compose exec web python movie_up/manage.py test peliculas salas funciones` termina OK.

## 2. Plantillas en parciales y páginas con shell

- [x] 2.1 Dividir los templates de `peliculas` en `_detail.html`, `_form.html` y `_confirm_delete.html`, reutilizados por `detail.html`, `form.html` y `confirm_delete.html`, con la información en tarjeta centrada y las acciones como botones — Verificación: Playwright abre detalle, edición y borrado de una película: shell completo, tarjeta centrada, botones en lugar de enlaces planos y 0 errores de consola.
- [x] 2.2 Repetir la división en `funciones`, conservando el grid de distribución y su script en la página completa — Verificación: Playwright abre detalle, edición y borrado de una función con el grid visible y 0 errores de consola.
- [x] 2.3 Repetir la división en `salas`, conservando el editor de butacas con `grid.js` en la página completa — Verificación: Playwright crea y edita una sala desde su página completa y el editor responde.
- [x] 2.4 Convertir en botones las acciones Ver, Editar, Eliminar y Crear de los tres `_listado.html` (peliculas, funciones y salas) — Verificación: Playwright en `/gestion/` muestra los botones en las tres pestañas y `docker compose exec web python movie_up/manage.py test core` termina OK.

## 3. Modo fragmento en el servidor

- [x] 3.1 Agregar en `movie_up/core/` un helper de fragmento que detecte el header `X-Panel-Request` y alterne entre la plantilla completa y la parcial, y aplicarlo al detalle, al formulario y a la confirmación de las tres apps — Verificación: tests nuevos por app que pidan cada vista con el header y asserten la parcial sin documento `<html>`, y la misma vista sin header devuelva la página completa.
- [x] 3.2 Hacer que las respuestas de panel incluyan `X-Panel-View: list|form|detail` y que el éxito de un `POST` devuelva el listado de la app en lugar de un redirect — Verificación: tests de `POST` con header en las tres apps: éxito → listado con el registro nuevo/actualizado/sin el eliminado, error → formulario con el mensaje del servicio.
- [x] 3.3 Extender `core/decorators.py` para que, ante una petición de panel sin sesión válida, responda `401` con `X-Panel-Redirect` en lugar de un redirect — Verificación: `AuthPanelTests` que envíen el header sin sesión y asserten 401 con la URL de retorno.
- [x] 3.4 Completitud del fragmento de edición de salas: el parcial de editar incluye el `json_script` de `initial_distribution` con la distribución real de la sala y el campo `distribucion` oculto dentro del formulario — Verificación: test que pida la edición con el header `X-Panel-Request` y asserte que el JSON de la sala aparece en el fragmento y coincide con el almacenado.
- [x] 3.5 Correr la suite completa — Verificación: `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas core` termina OK.

## 4. Navegación interna del panel

- [x] 4.1 Crear `movie_up/static/js/management-panel.js` que intercepte los enlaces `data-panel-link`, haga `fetch` con el header, reemplace el contenido de la pestaña, mantenga `aria-busy` durante la carga, mueva el foco al primer encabezado y cancele la petición anterior con `AbortController` — Verificación: Playwright en `/gestion/` ejecuta Ver, Editar, Eliminar y Crear en las tres pestañas sin cambiar la URL ni recargar, con la pestaña activa intacta y 0 errores de consola.
- [x] 4.2 Interceptar el envío de los formularios `data-panel-form` con `FormData`, volviendo al listado en el éxito y mostrando el mensaje del servicio en el panel ante un error — Verificación: Playwright crea, edita y borra una sala y una función dentro del panel y observa la lista actualizada en cada caso, más un caso de error de validación visible en el formulario.
- [x] 4.3 Refactorizar `movie_up/salas/static/salas/js/grid.js` a un namespace `window.SeatGrid.init(root)` que corra tras cada intercambio acotando todas sus queries al `root`, con un guard que impida inicializar dos veces el mismo panel, y que siga auto-invocándose en `DOMContentLoaded` para la página completa — Verificación: Playwright crea una sala desde el panel y el editor de butacas responde a los clics y al redimensionado; en la página completa `salas/nueva/` sigue operativo.
- [x] 4.4 Cargar `salas/js/grid.js` una sola vez desde `templates/gestion.html` y disparar el `init` desde `management-panel.js` — Verificación: Playwright abre `/gestion/`, entra en Editar de una sala y comprueba en la consola que el script se pidió una sola vez y que la cuadrícula aparece pintada con celdas; sin errores de consola.
- [x] 4.5 Cambiar en `static/css/components.css` `.management-panel button` a `.management-panel button:not(.seat-grid__cell)` para que las celdas no adopten `min-height: 40px` ni `background: var(--secondary)`, sin tocar las clases que genera el JS ni `--grid-columns` — Verificación: Playwright en el panel hace clic en celdas y comprueba por DOM/estilos computados que cada celda conserva `2rem` de ancho y el color `#888` (P), `#1976d2` (A) o `#d4af37` (R) dentro de `/gestion/`.
- [x] 4.6 Cubrir la sesión vencida y la degradación sin JavaScript — Verificación: Playwright con la cookie de sesión eliminada manda al login con retorno a `/gestion/`, y con JavaScript desactivado los enlaces del listado abren las páginas completas.

## 5. Acceso directo y cierre de sesión

- [x] 5.1 Apuntar el `Login` del nav y el `Comprar entradas` sin sesión a `{% provider_login_url "google" process="login" next=... %}` — Verificación: tests de `core/tests.py` actualizados (reemplazan la aserción de `/accounts/login/?next=/`) y Playwright: el clic en `Login` llega al flujo de Google sin mostrar la pantalla intermedia de acceso.
- [x] 5.2 Convertir el `Logout` del nav en un `<form method="post">` con token CSRF y botón estilado — Verificación: `LogoutNavTests` con `POST` que cierra sesión y redirige a `/` y sin token que no cierra; Playwright cierra sesión con una sola activación y aterriza en la página principal.
- [x] 5.3 E2E por rol completo con consola limpia — Verificación: Playwright recorre visitante (home, compra → Google), cuenta común (entradas) y administrador (gestión → operación de panel → `/admin/`) sin errores de consola.

## 6. Verificación de integración

- [x] 6.1 Suite completa y comprobaciones estáticas — Verificación: `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas core`, `manage.py check` y `manage.py makemigrations --check` terminan con 0 errores (solo los dos warnings conocidos W036 de allauth).
- [x] 6.2 Validación estricta de la spec — Verificación: `openspec validate ui-crud-pages --strict` sale con código 0.
- [x] 6.3 Verificación visual final en navegador real de las nueve páginas CRUD, las tres pestañas de la gestión y los flujos de acceso — Verificación: registro de pantallas por rol sin desviaciones de paleta y con consola limpia.

## Workflow follow-up

- Presentar el diff pendiente y esperar la aprobación explícita del usuario antes de cualquier `git add`, `git commit` o `git push`.
- Registrar el cambio en el README con el agente `readme-maintainer` cuando el usuario lo solicite.
- Archivar `ui-crud-pages` (`openspec validate ui-crud-pages --specs --strict`, sincronizar specs y actualizar los árboles de `AGENTS.md` y `README.md`) bajo petición explícita.
