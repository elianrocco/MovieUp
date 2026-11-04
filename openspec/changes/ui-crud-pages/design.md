# Design

## Context

Ver `proposal.md` (Why) para la motivación. Hechos que condicionan la solución:

- El shell ya existe: `templates/base.html` carga `tokens.css → base.css → site-shell.css → components.css`, y la vista de gestión pre-renderiza los tres listados como parciales dentro de un `<section data-management-panel>` que `static/js/management-tabs.js` alterna sin tocar la URL. `ui-shell` descartó el `fetch` de fragmentos en su design.md porque las pestañas no tenían estado.
- Las vistas CRUD son delgadas y delegan en `services.py`; el contrato es `ValueError` con mensaje en español → la vista re-renderiza el formulario con `error`, e inexistente → `Http404`.
- `salas/css/salas.css` declara `:root { font-family: Arial }`, `body { background: #f6f7f9; padding: 2rem }`, `a { color: #145da0 }` y `.data-table` / `.button-link` / `.actions` que hoy **también** consumen los listados de gestión; lo cargan `funciones/detail.html`, `funciones/form.html`, `salas/detail.html` y `salas/form.html` desde `{% block head %}`.
- `salas/js/grid.js` se auto-inicializa en `DOMContentLoaded` con `document.querySelector` y referencias globales.
- django-allauth 65.21.1 (verificado en el código instalado): `LogoutView.get()` renderiza la confirmación, `LogoutView.post()` cierra sesión y redirige; no existe ningún `ACCOUNT_LOGIN_URL`, y `{% provider_login_url "google" process="login" next="..." %}` construye la URL del proveedor con el retorno.

## Goals / Non-Goals

**Goals:**

- Una sola fuente de verdad por operación: el mismo fragmento alimenta la página completa y el panel de gestión.
- Cero cambios en modelos, servicios, contratos de error y rutas existentes.
- Degradación real sin JavaScript (los enlaces siguen siendo enlaces).
- Verificación en navegador real de cada vista antes de darla por hecha.

**Non-Goals:**

- Estilizar las páginas propias de allauth (`/accounts/login/`, confirmación de `GET /accounts/logout/`): quedan como excepción no enlazada por la interfaz.
- Histórico de navegación del panel (botón "atrás" del navegador) y modo de trabajo sin JavaScript en la gestión.
- Las páginas de `entradas` (listado, detalle y validación del cliente): candidatas a un cambio posterior.
- El botón `Estadísticas` y la vista de cuentas dentro del panel, que ya funcionan como están.

## Decisions

**D1 — Fragmentos por header sobre las mismas vistas.** Las vistas existentes detectan el header `X-Panel-Request: 1` y alternan entre la plantilla completa y la parcial (`_detail.html`, `_form.html`, `_confirm_delete.html`, `_listado.html`), que la página completa incluye a su vez. Toda esa lógica vive en un único helper, `core/panel.py` (`render_panel`, `panel_list_or_redirect`), que deriva el parcial desde el nombre de la plantilla completa (`salas/detail.html` → `salas/_detail.html`, con `list.html` → `_listado.html` como única excepción), de modo que las vistas siguen delgadas. *Por qué:* una sola implementación de flujo, contexto y errores por operación; la página completa y el panel no pueden divergir. *Alternativa descartada:* vistas `gestion_panel` dedicadas por app (12 vistas nuevas con la lógica de errores duplicada) y pre-renderizar todos los detalles en la gestión (peso innecesario y datos que envejecen).

**D2 — El servidor decide el estado de vuelta.** Toda respuesta de panel incluye `X-Panel-View` con el estado que se entregó: `list` (listado, incluido el de un `POST` exitoso), `form` (formulario y confirmación de borrado) o `detail` (detalle). Nunca hay redirect: el éxito de un `POST` responde 200 con el fragmento del listado, y una sesión vencida responde `401` con `X-Panel-Redirect: /accounts/login/?next=/gestion/` — la URL de login **ya con el retorno**, para que el cliente solo tenga que navegar a ella. *Por qué:* el JS no adivina por el HTML ni sigue redirects que le devolverían la página de login completa dentro del panel; el retorno apunta siempre a la gestión porque una petición de panel, por definición, sale de ahí. *Excepción:* una cuenta autenticada sin permisos de staff conserva el `302` a `/` de siempre (no es una sesión vencida).

**D3 — Opt-in explícito por enlace.** Solo los enlaces marcados con `data-panel-link` (Ver, Editar, Eliminar, Crear, Volver) se interceptan. *Por qué:* el enlace del tráiler en el detalle es externo y `a[href^="http"]` no es suficiente porque las rutas internas también son absolutas.

**D4 — `POST` por `fetch` con el `FormData` del propio formulario.** El formulario del fragmento ya lleva `{% csrf_token %}`, así que el token viaja sin endpoints nuevos ni excepciones de CSRF. *Alternativa descartada:* cabecera `X-CSRFToken` manual (duplica la lógica del token).

**D5 — `grid.js` expone `init(root)` y `/gestion/` lo carga una vez.** El editor de butacas deja de auto-inicializarse solo en `DOMContentLoaded`: pasa a exponer un namespace (`window.SeatGrid.init`) y `management-panel.js` lo llama después de inyectar cada fragmento, manteniendo la auto-invocación para la página completa (comprobando `document.readyState` por si el script llega tarde). Tres detalles obligatorios: (a) `templates/gestion.html` agrega `<script src="salas/js/grid.js" defer>` porque el fragmento no trae scripts y `innerHTML` no los ejecuta; (b) todas las queries (`[data-seat-grid]`, `[data-grid-width]`, `[data-grid-height]`, `[data-grid-resize]`, `[data-distribution-input]` e `#initial-distribution`) se acotan al `root` — no al documento — para que no colisionen con nada fuera del panel; (c) el guard vive en el **elemento de cuadrícula** (`data-grid-ready`), no en el `root`: el `<section>` del panel persiste entre swaps y marcarlo impediría la segunda inicialización, mientras que la cuadrícula se reconstruye en cada intercambio y el guard se resetea solo — así dos swaps o un swap doble no duplican listeners y el clic avanza un solo paso. Los listeners viejos mueren con el DOM sustituido. *Por qué:* sin esto el formulario de salas entra al panel con un editor muerto.

**D6 — `forms.css` nuevo y `salas.css` eliminado.** Tarjeta de página, campos, lista de detalle, tabla, mensajes de error, botones para superficie clara y el grid de asientos se escriben con tokens en `static/css/forms.css`, y `salas.css` se borra junto con sus `<link>` en los templates. **Excepción de color aprobada por el usuario:** las celdas conservan sus hex actuales — `A` (asiento) `#1976d2`, `R` (reservado) `#d4af37`, `P` (pasillo) `#888` — fuera de la paleta cerrada, únicamente en el grid de asientos. *Por qué:* el usuario pidió mantener esos colores y son semánticamente estables entre el editor y las vistas de solo lectura.

**D7 — Migrar antes de borrar.** `.data-table`, `.button-link`, `.actions`, `.form-field`, `.error-message`, `.grid-controls` y `.seat-grid*` se migran a `forms.css`/`components.css` en el mismo paso en que se elimina `salas.css`, porque los listados de gestión y las cuatro páginas que lo cargan dependen de ellas. *Riesgo si se invierte el orden:* la gestión y las vistas pierden estilos sin aviso.

**D8 — Variantes de botón para superficie clara.** `btn--secondary` es transparente con texto crema (pensado para el hero): sobre fondo crema es ilegible. Se agregan `--neutral` (superficie con borde) y `--danger` (rojo de marca) manteniendo el contrato de tamaño de 40–56px.

**D9 — Login directo y logout por `POST`.** `Login` y el CTA de compra usan `{% provider_login_url "google" process="login" next=... %}`, y `SOCIALACCOUNT_LOGIN_ON_GET = True` hace que esa URL responda con un `302` a Google en un solo salto; sin ese flag allauth renderiza su propia pantalla de confirmación ("You are about to sign in using a third-party account from Google") en el `GET`, que es exactamente el intermedio que la spec manda saltear — medido antes del flag: `200` con esa pantalla, después: `302` con `Location: https://accounts.google.com/o/oauth2/v2/auth?…`. `Logout` es un `<form method="post">` con token CSRF dentro del nav, que `LOGOUT_REDIRECT_URL` lleva a `/`. *Por qué:* enlazar `accounts.google.com` a mano rompería la validación del `state` OAuth; `ACCOUNT_LOGOUT_ON_GET=True` permitiría desloguear con una imagen embebida. *Trade-off asumido:* queda un salto 302 del servidor que no renderiza pantalla — es el mínimo posible. *Coste colateral:* la etiqueta `provider_login_url` consulta `SocialApp` al renderizar, así que `FooterTests` pasó de `SimpleTestCase` a `TestCase`.

**D10 — Navegación interna sin entradas de historial.** El panel no llama `history.pushState`, igual que hoy las pestañas. *Por qué:* coherencia con el comportamiento ya aceptado y cero riesgo de desalinear URL y estado visible.

**D11 — Las celdas del editor quedan fuera del estilo de botón de la gestión.** `components.css:287-300` declara `.management-panel button { min-height: 40px; padding: .5rem 1rem; background: var(--secondary) … }`, con specificity `(0,1,1)` que gana a `.celda--*` `(0,1,0)`: dentro del panel las celdas que arma `grid.js` perderían sus colores, su altura de 2rem y su `padding: 0`. Se reescribe el selector a `.management-panel button:not(.seat-grid__cell)`. Además dos reglas de migración que no se pueden romper: (a) **ninguna clase que genera el JS se renombra** — `seat-grid__cell`, `celda--pasillo`, `celda--asiento`, `celda--reservado` y la custom property `--grid-columns` (`grid.js:1-5`, `grid.js:84`, `grid.js:91`) — y se conservan `padding: 0`, el tamaño de celda y los hex de `A`/`R`/`P`; (b) **el fragmento de edición incluye el `json_script` de `initial_distribution`** (`form.html:55`), que sí se injeta correctamente porque es un `<script type="application/json">` inerte leído por `textContent`. *Por qué:* el servidor solo protege de todo-P (`salas/services.py:64-65`); sin el JSON inicial el editor arranca vacío y un guardar real pisaría el mapa de la sala.

## Risks / Trade-offs

- [Duplicación de rutas de render entre modo completo y modo fragmento] → encapsular el cambio de plantilla en un helper único; las vistas solo declaran plantilla completa y parcial.
- [Tests existentes afirman `?next=/accounts/login/` (`core/tests.py`) y el href del nav] → actualizarlos en el lote de auth y agregar pruebas de fragmento, de `POST` de panel y de cierre de sesión.
- [La sesión vuelve inválida a mitad de un `fetch`] → guard en `staff_required`: si la petición es de panel, responder `401` con la URL de retorno en lugar de un redirect que el JS inyectaría.
- [Race conditions por clics rápidos en el panel] → `AbortController` que cancela la petición anterior antes de emitir la nueva.
- [El editor de distribución solo existe en la página completa: en el panel quedaría un `<div>` vacío o duplicaría listeners] → D5: `gestion.html` carga `grid.js` una vez, el `init` corre tras cada swap acotado al `root` con guard de doble inicialización.
- [Dentro del panel las celdas adoptan el estilo de botón de la gestión y pierden sus colores] → D11: `:not(.seat-grid__cell)` en `components.css`, clases del JS intocables y `json_script` obligatorio en el fragmento de edición.
- [Pérdida del foco y del contexto para lectores de pantalla] → `aria-busy` durante la carga y foco al primer encabezado tras el swap (requisito en la spec).
- [Sin JavaScript los tres listados de la gestión quedan apilados] → comportamiento ya aceptado en `ui-shell`; las acciones siguen abriendo páginas completas funcionales.
- [Celdas de colores fuera de paleta] → excepción documentada en D6, limitada a `.celda--*`; cualquier otro color fuera de tokens requiere aprobación previa.
- [Los estáticos de `/static` se sirven sin `Cache-Control` en DEBUG, así que el navegador los cachea por heurística y un JS/CSS recién editado no se ve — medido: se servía un `grid.js` de 4668 B en lugar del de 5677 B y `window.SeatGrid` quedaba indefinido] → durante el desarrollo, recargar con hard-refresh o limpiar la caché del navegador antes de verificar; en producción conviene `ManifestStaticFilesStorage` (nombre con hash) o cabeceras de caché en el servidor.

## Migration Plan

Sin migraciones de datos ni de esquema. Cinco lotes aplicables por separado, cada uno con `manage.py test` y verificación visual antes de pasar al siguiente:

1. Base visual (`forms.css`, variantes de botón, migración y eliminación de `salas.css`).
2. Parciales y las nueve páginas CRUD con shell.
3. Modo fragmento en servidor + guard de sesión + tests.
4. `management-panel.js` + refactor de `grid.js` + Playwright por operación.
5. Login/logout directos + ajuste de tests + E2E por rol.

Rollback: `git revert` del lote correspondiente; no hay estado persistido que deshacer.

## Open Questions

Ninguna pendiente: los colores del grid de asientos quedaron fijados por el usuario (D6).
