# Design

## Context

Ver `proposal.md` — Why. Resto de contexto necesario:

- `/gestion/` pre-renderiza todos los listados en una sola página (`core/views.gestion`) y `management-tabs.js` solo alterna paneles `hidden`; la URL no cambia porque no hay fetch. La navegación interna (Ver/Editar/Eliminar/Crear) usa `management-panel.js` con header `X-Panel-Request: 1` y las vistas responden fragmentos `_*.html` con `X-Panel-View` vía `core/panel.py`.
- El subNAV (`includes/management_subnav.html`) es el único punto que enlaza a `/admin/` (pestaña `Cuentas`).
- Contrato de errores de la casa (crud-conventions): el servicio lanza `ValueError` con mensaje en español y la vista re-renderiza con `error` en contexto → panel rojo (`div.error-message`); `Http404` para registro inexistente.
- `Funcion.pelicula` y `Funcion.sala` son `on_delete=PROTECT`; los guards de `peliculas/services.py` y `salas/services.py` quedaron como TODOs comentados porque se escribieron antes de que existiera la app `funciones`.
- `update_pelicula` aplica solo campos enviados no vacíos (update parcial): la vista construye `data` solo con `FORM_FIELDS` presentes y `en_cartelera` como bool siempre presente.

## Goals / Non-Goals

**Goals:**

- Que la pestaña `Cuentas` cargue su listado con el mecanismo de paneles existente, sin cambiar la URL y sin salir de `/gestion/`.
- Toggle de permisos por fila con sincronía `is_staff`/`is_superuser`, protegido en cliente y servidor.
- Guards de edición/borrado de películas y salas implementados en services, con el flujo `ValueError` → panel rojo ya existente.
- Botones de la edición de Película idénticos a los de salas/funciones.

**Non-Goals:**

- Deshabilitar o quitar el `/admin/` de Django (sigue montado: recuperación con `createsuperuser`, changelist de cuentas).
- CRUD completo de cuentas desde gestión (sin crear/editar/borrar; solo listar + switch).
- Cambiar etiquetas de los formularios de ALTA de películas (`Crear` / `Volver al listado` quedan como están; el alcance pedido fue la edición).
- Tocar la app `funciones` o relajar `PROTECT` (queda como red de integridad final ante cualquier path no previsto).
- Rediseño visual más allá del componente switch con la paleta del sitio.

## Decisions

1. **Listado de cuentas pre-renderizado, no fetch.** Se agrega una `<section data-management-panel="accounts" hidden>` con `{% include 'cuentas/_listado.html' %}` y `'cuentas'` al contexto de `gestion()`, replicando exactamente el patrón de las otras pestañas. *Alternativa descartada*: traer el listado al clickear la pestaña — rompería la premisa "todo pre-renderizado" del panel y obligaría a manejar loading/errores en la primera carga.

2. **SubNAV: `<a>` → `<button data-management-tab="accounts">`.** `management-tabs.js` ya es genérico (no requiere cambios); `management_subnav.html` deja de referenciar `admin:index`, que pasa a ser el único cambio relacionado con `/admin/` en templates.

3. **Endpoint POST único para el toggle, sin página GET.** `cuentas/urls.py` expone `permisos/<pk>/` (solo POST, `@staff_required`, CSRF por form). La vista re-renderiza `cuentas/_listado.html` con `X-Panel-View: list` cuando hay `X-Panel-Request`; sin ese header (POST nativo sin JS) redirige a `/gestion/`. *Alternativa descartada*: crear `cuentas/list.html` + URL `/cuentas/` como en otros CRUDs — sería una página que nadie enlaza (la pestaña nunca navega) y la gestión ya depende de JS para cambiar de pestaña, por lo que no hay degradación nueva.

4. **Rechazo del auto-cambio en dos capas.** El `disabled` del switch es solo presentación; el servicio/validación de vista compara `cuenta.pk == request.user.pk` y lanza `ValueError`. Con eso el admin activo nunca puede degradarse a sí mismo → siempre queda al menos un administrador en el sistema, sin guard de "último admin" adicional. *Alternativa descartada*: solo `disabled` (un POST directo lo evade).

5. **Sincronía de permisos en una sola escritura atómica.** `toggle_permisos` setea `is_staff` e `is_superuser` juntos dentro de `transaction.atomic()` (regla fija de AGENTS: el indicador de administrador sincroniza ambos). Dos toggles concurrentes sobre la misma fila: gana el último, aceptable.

6. **Guard de edición de película = diff normalizado contra los campos enviados.** Si `Funcion.objects.filter(pelicula_id=pk).exists()`, se compara cada campo enviado con el valor actual (normalizando: `str`, `date.isoformat()`, trim) más `image_file is not None` como cambio de imagen; solo `en_cartelera` puede diferir. Cualquier otra diferencia → `ValueError` **antes** de la verificación de unicidad y de tocar el disco. Campo vacío/no enviado = sin cambio (consistente con el update parcial existente). *Riesgo cubierto*: comparar por igualdad de tipos (`'120' != 120`) rechazaría guardados sin cambios reales — por eso la normalización.

7. **Guard de borrado de película ANTES de tocar el filesystem.** Hoy `delete_pelicula` borra la portada y luego `pelicula.delete()` revienta con `ProtectedError` → la película sobrevive pero pierde la imagen. El check de funciones asociadas corre primero, y el `ValueError` se captura en la vista re-renderizando `confirm_delete` con `error` (patrón de `funcion_delete`). El import de `Funcion` es local dentro de la función (evita el import circular `peliculas ↔ funciones` y sigue el estilo de los TODOs originales).

8. **Guards de salas reemplazan los TODOs tal cual su texto de spec**: `update_sala` → rechazo incondicional si existe función **activa** (`filter(sala_id, funcion_activa=True)`) antes de mutar; `delete_sala` → rechazo si existe **cualquier** función (`filter(sala_id)`), activa o no. `sala_delete` gana el `try/except ValueError` → `confirm_delete` con `error`, que ya tiene el `div.error-message`.

9. **Botones de edición de Película en `_form.html`:** submit `Guardar cambios` y acción `Cancelar` con `data-panel-link` hacia `peliculas:pelicula_detail` (mismo patrón que `salas/_form.html`, que ya cancela hacia el detalle). El modo alta no cambia.

10. **Estilos del switch:** componente nuevo en la hoja global del shell (ya cargada por `base.html`), con los tokens de la paleta del sitio — al implementar se sigue la skill `ui-design`.

## Risks / Trade-offs

- [Falso positivo del diff de edición: rechazar una edición sin cambios reales] → normalización de tipos + tests de los cuatro casos (sin cambios, solo `en_cartelera`, otro campo, imagen nueva).
- [POST nativo sin JS responde un fragmento sin shell] → fallback con redirect a `/gestion/`; sin JS la gestión no funciona de todos modos (las pestañas son botones JS).
- [Tests existentes que afirman el comportamiento viejo] → `core/tests.py` (conteo `data-management-tab` 4→5, `assertContains(reverse('admin:index'))` → `assertNotContains`), posibles aserciones de botones en `peliculas/tests.py` — se actualizan en el mismo lote y se corre la suite completa (~75 s).
- [Dos administradores operando el mismo switch a la vez] → escritura atómica; último en llegar gana. Sin bloqueo de fila: el impacto es un flag de permisos, no dinero ni inventario.
- [El guard de salas bloquea un guardado sin cambios con funciones activas] → es el comportamiento pedido (y el que ya manda `update_funcion` con entradas > 0); queda fijado en un escenario de spec.

## Migration Plan

Sin migraciones de modelos: el cambio es de comportamiento y templates. Deploy = código; rollback = revert del commit. La data no se transforma.

## Open Questions

Ninguna; las decisiones de alcance (mensajes de error, borrado de sala por cualquier función, rechazo incondicional de edición de sala, `/admin/` intacto, alcance solo-edición de los botones) quedaron cerradas con el usuario en la sesión de planificación.
