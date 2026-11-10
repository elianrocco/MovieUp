# Tasks

## 1. Lote 1 — Listado de cuentas en /gestion/

- [x] 1.1 Implementar en `cuentas/services.py` `list_cuentas()` (orden alfabético por correo) y `toggle_permisos(cuenta, solicitante)` que sincroniza `is_staff`/`is_superuser` en transacción y lanza `ValueError` al intentar cambiar la propia cuenta; verificar con tests de servicio en `cuentas/tests.py` (listado, swap admin↔común, rechazo propio)
- [x] 1.2 Crear la vista POST `cuenta_permiso_update` en `cuentas/views.py` con `@staff_required` que re-renderiza `cuentas/_listado.html` con `X-Panel-View: list` en peticiones de panel y redirige a `/gestion/` sin ese header; registrar la ruta en `cuentas/urls.py` e incluir el namespace en `core/urls.py`; verificar con tests de vista (POST desde panel devuelve el fragmento con header, no-POST redirige, cuenta común redirigida a `/`)
- [x] 1.3 Crear `cuentas/templates/cuentas/_listado.html` con el estilo de los listados existentes: `h1`, tabla `data-table` con columnas Correo, Nombre, Permisos, Acciones; sin botón Crear ni Ver/Editar/Eliminar; switch en cada fila con `disabled` para la cuenta de la sesión y `data-panel-form` con CSRF; verificar con test de estructura (columnas, ausencia de links CRUD, `disabled` en la fila propia)
- [x] 1.4 Cambiar en `includes/management_subnav.html` el enlace `Cuentas` por `<button data-management-tab="accounts">` y agregar en `gestion.html` la sección `data-management-panel="accounts"` con el include del listado; verificar con los tests de `core/tests.py` actualizados (`count(data-management-tab=) == 5`, `assertNotContains` de `admin:index`, panel accounts presente)
- [x] 1.5 Agregar el estilo del switch (paleta del sitio) en la hoja global del shell; verificar con `openspec validate` de requisitos visuales implícitos y con revisión visual en navegador (Playwright) del listado de cuentas en `/gestion/`
- [x] 1.6 Actualizar los tests de `core/tests.py` que afirman el comportamiento viejo del subNAV y correr `python movie_up/manage.py test core cuentas` — debe pasar 100%

## 2. Lote 2 — Guards de películas y salas

- [ ] 2.1 Implementar en `peliculas/services.py::update_pelicula` el guard de edición: si la película tiene funciones asociadas, comparar campos enviados vs actuales normalizados y rechazar con `ValueError("No se puede editar una película con funciones asociadas; solo puede cambiarse el estado En cartelera.")` cuando algo distinto de `en_cartelera` cambie (imagen nueva cuenta como cambio), antes de unicidad y de tocar el disco; verificar con tests: sin cambios OK, solo `en_cartelera` OK, cambio de título/duración rechazado, imagen nueva rechazada, película sin funciones OK
- [ ] 2.2 Implementar en `peliculas/services.py::delete_pelicula` el guard de borrado (funciones asociadas → `ValueError("No se puede eliminar una película con funciones asociadas.")` **antes** de borrar la portada) y capturar `ValueError` en `peliculas/views.pelicula_delete` re-renderizando `confirm_delete` con `error`; verificar con tests: borrado rechazado conserva película y portada, borrado sin funciones elimina, confirmación muestra el mensaje en panel rojo
- [ ] 2.3 Implementar en `salas/services.py::update_sala` el guard de `ValueError("No se puede actualizar una sala con funciones activas.")` antes de mutar (reemplazando el TODO), y en `salas/services.py::delete_sala` el guard `ValueError("No se puede eliminar una sala con funciones asociadas.")` por cualquier función asociada; verificar con tests: edición con activas rechazada aunque no cambien datos, edición con solo desactivadas OK, borrado con funciones (activas o desactivadas) rechazado, sala sin funciones OK
- [ ] 2.4 Capturar `ValueError` en `salas/views.sala_delete` re-renderizando `confirm_delete` con `error`; verificar con test de vista: el POST de borrado rechazado devuelve la confirmación con el mensaje y la sala permanece
- [ ] 2.5 Cambiar en `peliculas/templates/peliculas/_form.html` el modo edición: submit `Guardar cambios` y acción `Cancelar` con `data-panel-link` hacia `peliculas:pelicula_detail` (el alta no cambia); verificar con test que el formulario de edición contiene ambas etiquetas y el href del detalle, y que no aparece `Volver al listado` en edición
- [ ] 2.6 Correr `python movie_up/manage.py test peliculas salas funciones cuentas core` — debe pasar 100%

## 3. Verificación final

- [ ] 3.1 Correr la suite completa `python movie_up/manage.py test peliculas salas funciones cuentas entradas compras core estadisticas chatbot` y verificar 100% en verde
- [ ] 3.2 Verificar `python movie_up/manage.py makemigrations --check` (sin migraciones pendientes) y `openspec validate gestion-cuentas-y-bloqueos --strict` (válido)
- [ ] 3.3 Verificar en navegador real (Playwright, `docker compose up --build` + `http://localhost:8000/`): clic en `Cuentas` carga el listado sin cambiar la URL ni ir a `/admin/`, switch deshabilitado en la fila propia, toggle efectivo, guard de edición de película y de sala con panel rojo, y botones `Guardar cambios`/`Cancelar` (→ detalle) en la edición de película; consola sin errores

## Workflow follow-up

- Archivar el change con `/opsx-archive gestion-cuentas-y-bloqueos` tras la revisión del usuario (sync de deltas a `openspec/specs/` incluido en el flujo).
