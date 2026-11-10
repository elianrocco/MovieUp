# Proposal

## Why

La pestaña `Cuentas` del subNAV de `/gestion/` es el único control que hoy navega fuera de la vista (enlaza a `/admin/`), rompiendo la regla de que la gestión no cambia de URL; además no existe un listado de cuentas con el mismo estilo que los listados de Películas, Funciones y Salas. En paralelo, los guards de asociación entre películas/salas y funciones están speceados desde hace tiempo pero sin implementar (quedaron como TODOs): eliminar una película con funciones provoca un `ProtectedError` con la página de error de Django —y además borra la portada del disco antes de que PROTECT rechace—, y editar o borrar salas en uso pasa sin ningún control.

## What Changes

- La pestaña `Cuentas` deja de ser un enlace a `/admin/` y pasa a ser una pestaña como las demás: carga en el cuerpo un listado de cuentas con el mismo estilo que los demás listados, sin cambiar la URL.
- El listado muestra correo, nombre y permisos; no ofrece crear, ver detalle, editar ni eliminar: su única acción es un switch por registro que intercambia `Usuario común` ↔ `Administrador`, deshabilitado en la fila de la cuenta con la que se inició sesión (y rechazado igualmente por el servidor).
- Guard de eliminación de película: rechazada si la película tiene funciones asociadas (activas o no), sin tocar ni el registro ni la portada —elimina el 500 actual—.
- Guard de edición de película: con funciones asociadas, solo puede cambiar `en_cartelera`; cualquier otro cambio real se rechaza con el mensaje en panel rojo.
- Guard de eliminación de sala: rechazada si la sala tiene cualquier función asociada (activa o no); el spec actual solo bloqueaba por funciones activas —se endurece—.
- Guard de edición de sala con funciones activas (ya speceado, hoy sin implementar): rechazo con panel rojo, sin modificar datos.
- Botones del formulario de edición de Película alineados con los de salas y funciones: `Guardar cambios` y `Cancelar`, y `Cancelar` muestra el detalle de la película en lugar del listado.
- El `/admin/` de Django queda montado y accesible directamente (recuperación con `createsuperuser`, changelist de cuentas); solo se quita el acceso desde el subNAV.

## Capabilities

### New Capabilities

Ninguna; el change modifica capacidades existentes.

### Modified Capabilities

- `cuentas`: se ajusta el requisito de gestión vía panel de administración (ya no es "sin una interfaz de gestión propia") y se agregan los requisitos del listado de cuentas en la gestión y del cambio de permisos mediante switch.
- `ui`: el requisito "Cuentas dentro del shell" deja de exigir el panel de Django y pasa a exigir el listado de cuentas en el cuerpo sin cambiar la URL; se ajusta el escenario de cancelación de formularios (edición → detalle) y se agrega el requisito de botones del formulario de edición (`Guardar cambios` / `Cancelar` → detalle).
- `movies`: el guard de borrado por funciones asociadas deja de ser condicional y su mensaje se alinea al estilo de funciones; se agrega el guard de edición que permite cambiar solo `en_cartelera` cuando hay funciones asociadas.
- `salas`: el bloqueo de operaciones en uso pasa a rechazar el borrado por cualquier función asociada (no solo activas) y fija los mensajes explícitos de rechazo.

## Impact

- **Templates**: `movie_up/templates/includes/management_subnav.html` (enlace → botón de pestaña), `movie_up/templates/gestion.html` (nuevo panel de cuentas), `movie_up/peliculas/templates/peliculas/_form.html` (botones de edición), `movie_up/cuentas/templates/cuentas/_listado.html` (nuevo).
- **Backend**: `movie_up/cuentas/services.py` (listado y toggle de permisos), `movie_up/cuentas/views.py` + `urls.py` (fragmento y endpoint POST del switch), `movie_up/core/urls.py` (include de `cuentas`), `movie_up/core/views.py` (contexto del listado), `movie_up/peliculas/services.py` y `views.py` (guards de edición/borrado), `movie_up/salas/services.py` y `views.py` (guards de edición/borrado + captura de `ValueError` en borrado).
- **Frontend/CSS**: componente visual del switch en el panel de gestión.
- **Tests**: `cuentas/tests.py`, `core/tests.py` (conteo de pestañas 4 → 5, ausencia de `admin:index` en el subNAV), `peliculas/tests.py` y `salas/tests.py` (guards y botones).
- **Specs**: deltas en `openspec/specs/{cuentas,ui,movies,salas}/spec.md`.
