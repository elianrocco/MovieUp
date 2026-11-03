# Design

## Context

Ver proposal.md para el motivo. Hechos que condicionan la implementación:

- 15 templates autosuficientes (cada uno declara su `<head>` y linkea sus CSS); no existe base template y `TEMPLATES['DIRS']` está vacío.
- `STATIC_URL` es todo lo que hay: no hay `STATICFILES_DIRS` ni `STATIC_ROOT`; el único static por app es `salas/static/salas/` (editor de grilla, exclusivo de esa app) y ya hay una fuga: los templates de `funciones` linkean `salas/css/salas.css`.
- `peliculas/views.py`, `salas/views.py` y `funciones/views.py` no tienen ningún decorator ni mixin de acceso (15 funciones sin guardar); solo `entradas` usa `login_required`/`staff_member_required`.
- `Pelicula` tiene todos los campos del home; `Cuenta` no tiene campo de foto (solo `correo` y `nombre`).
- `core/urls.py` no tiene ruta para `/`; el admin vive en `/admin/`.
- La skill `ui-design` gobierna todo lo visual (paleta cerrada, pares de texto + AA, centrado, tamaño de botones); `ui` es la spec de comportamiento.

## Goals / Non-Goals

**Goals:**

- Un shell único (nav + footer + base template) reutilizable por todas las vistas, cargado una sola vez.
- Dashboard admin con pestañas que cambian el cuerpo sin cambiar la URL.
- El panel de cuentas de Django funcionando dentro del shell de la web.
- Cerrar el agujero de acceso de las tres apps CRUD con un mecanismo de rechazo consistente con la spec.
- Infraestructura de assets globales que deje lista la carpeta para el CSS/JS del sistema de diseño.

**Non-Goals:**

- La vista de compra de entradas (otro cambio) y cualquier cosa dependiente de ella.
- La vista de Estadísticas.
- Imágenes definitivas: el logo lo carga el autor y la foto la aporta el proveedor (placeholders hasta entonces).
- Cambios de modelo de `Pelicula`.
- Reestilizar la pantalla de login del admin de Django (solo su shell autenticado).

## Decisions

### D1. Infraestructura: statics y templates a nivel de proyecto

`movie_up/static/` (+ `STATICFILES_DIRS = [BASE_DIR / 'static']`) y `movie_up/templates/base.html` (+ `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']`).

- **Por qué:** el shell y la paleta son transversales; una app nueva sería código de dominio sin dominio (contradice "apps por dominio") y `core/static` mezclaría assets de diseño con el paquete de configuración. Es el patrón documentado de Django para assets compartidos.
- **Alternativa descartada:** app `ui` con `startapp` (scaffolding muerto en `INSTALLED_APPS`).

### D2. Pestañas del dashboard: pre-render + alternancia con JS

La vista de gestión renderiza los tres listados (películas, funciones, salas) como parciales apilados en el cuerpo; JS alterna su visibilidad al hacer clic. La URL nunca cambia.

- **Por qué:** cero dependencias nuevas, cambio instantáneo, sin endpoints de fragmentos, fácil de testear (Playwright). La degradación sin JS (los tres listados visibles apilados) es aceptable en un panel solo-staff.
- **Alternativas descartadas:** `fetch` de fragmentos (más JS + endpoints sin necesidad) y HTMX (dependencia nueva para un solo componente).
- **Cuentas queda fuera de este mecanismo:** ver D4.

### D3. Rechazo de acceso: decorator propio compartido

Un único decorator `staff_required` en `core/decorators.py`: anónimo → redirect a `LOGIN_URL` (pantalla de login de allauth, conservando `?next`); autenticado no-staff → redirect a `/`. Se aplica a las 15 funciones CRUD, a la vista de gestión y (en inverso) la home redirige a `/gestion/` cuando el visitante es staff.

- **Por qué:** `staff_member_required` de Django manda al login del admin (`/admin/login/`), que no es la "pantalla de inicio de sesión" que exige la spec; el comportamiento pedido (anónimo → login, común → home) no existe en un decorator estándar.
- **Centralizarlo** en un solo archivo evita repetir la lógica en cuatro apps y lo cubre con un solo set de tests de comportamiento más los flujos por app.

### D4. Cuentas (B4): navegación al admin con shell inyectado

Al hacer clic en `Cuentas`, la vista navega a `/admin/` (cambia la URL; la spec solo exige URL constante para Películas/Funciones/Salas). El admin se integra con un override de templates a nivel de proyecto: `templates/admin/base_site.html` en `DIRS` (que tiene prioridad sobre `APP_DIRS`) inyecta el nav global, el subNAV con `Cuentas` activo, el footer y un CSS con los tokens de la paleta, envolviendo el contenido nativo del admin.

- **Por qué:** el admin de Django es un documento completo con sus propios bloques; intentar inyectarlo dentro del cuerpo del dashboard requeriría iframe (descartado por el usuario) o parsear HTML ajeno. Con override, el admin conserva forms/tables funcionando y "usa los dos NAVs, el footer y la paleta".
- **Riesgo acotado:** solo se envuelve `base_site.html`/`base.html`; no se tocan formularios ni acciones del admin.

### D5. Foto de cuenta: campo en `Cuenta`

Nuevo campo nullable (`foto_url`) en `Cuenta`, poblado por el adapter/signal de allauth al iniciar sesión con Google, con fallback a placeholder en el nav si está vacío.

- **Por qué:** una consulta directa en el nav (sin joins a `SocialAccount`), supervive a cambios del proveedor y es lo que "carga el sistema" (el usuario nunca la edita).
- **Alternativa descartada:** leer `extra_data` de `SocialAccount` en cada render (consulta extra por request y acoplamiento al shape de la respuesta de Google).

### D6. Tipografías y logo

- Playfair Display + Inter desde Google Fonts CDN en `base.html` (máximo dos familias, como manda `ui-design`; el login con Google ya requiere internet en el entorno).
- Logo en `{% static 'img/logo.png' %}` con `alt="MovieUp"`: el archivo lo carga el autor en esa ruta; hasta entonces el navegador degrada a texto alternativo (sin JS roto ni layout roto).

### D7. Orden de infraestructura visual

`tokens.css` (12 variables oklch + pares de texto) → `base.css` (reset, tipografía, fondo crema con radiales y grano, nav/footer) → `components.css` (botones 40–56px, cards con ring 1px, chips, hero) — todo bajo las hard rules de `ui-design`. Los templates refactorizados pasan a `{% extends 'base.html' %}`; los CSS por app (editor de grilla de `salas`) se mueven a `{% block head %}`.

### D8. Botón `Comprar entradas` con sesión: sin destino

Hasta que la vista de compra exista, el botón queda sin destino operativo (`href="#"`) para cuentas autenticadas — decisión explícita del usuario, descartando tanto un 404 deliberado como una vista stub "próximamente". El cambio que implemente la compra lo enchufa.

## Risks / Trade-offs

- **Refactor de 15 templates rompe vistas que hoy funcionan** → suite completa (169 tests) + verificación Playwright en las rutas representativas tras cada tanda.
- **El override del admin rompe funcionalidad del panel** → envolver sin tocar forms/tables; smoke test del CRUD de cuentas en `/admin/` después del override.
- **Cuentas sin foto en Google** → escenario de fallback ya previsto en la spec (marcador de posición).
- **`staff_required` propio diverge de los decorators estándar** → un solo archivo, tests de rechazo por rol en cada app afectada.
- **Logo pendiente del autor** → placeholder con `alt`; riesgo visual menor, no bloquea.
- **Sin JS, los tres listados del dashboard se ven apilados** → aceptable en panel solo-staff; la verificación visual se hace con navegador real donde JS corre.

## Migration Plan

1. Infraestructura (settings + `static/` + `base.html`) sin romper nada: los templates viejos siguen funcionando hasta que se refactoricen.
2. Refactor por app (salas → funciones → películas → entradas) con suite + Playwright después de cada una.
3. Vistas home y gestión + `staff_required` + guards en las 15 funciones CRUD (aquí se cierra el agujero).
4. Foto de cuenta: migración `AddField` nullable (sin reset de volumen, compatible con el flujo de entradas ya archivado).
5. Override del admin.
6. Verificación final: suite completa, `manage.py check`, Playwright por rol (visitante, común, admin).

Rollback: los pasos 1–2 son aditivos (revertir no toca datos); el paso 4 es una migración nullable reversible con `RemoveField`.

## Open Questions

- Imagen definitiva del logo: la aporta el autor en `movie_up/static/img/logo.png` (no bloquea; el placeholder ya queda cableado).
