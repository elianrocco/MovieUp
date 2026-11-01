# Tasks

## 1. Scaffolding de la app y configuración

- [x] 1.1 Crear la app `funciones` con `startapp` desde `movie_up/`, registrarla en `INSTALLED_APPS`, crear `templates/funciones/.gitkeep` y `urls.py` con `app_name` base; verificar con `python movie_up/manage.py check` sin errores.
- [x] 1.2 Cambiar `TIME_ZONE` a `America/Argentina/Buenos_Aires` manteniendo `USE_TZ = True` en `movie_up/core/settings.py`; verificar con `python movie_up/manage.py shell -c "from django.utils import timezone; print(timezone.get_default_timezone())"` que imprime la zona de Buenos Aires.
- [x] 1.3 Actualizar los árboles de `AGENTS.md` y `README.md` y el comando de tests documentado (agregar `funciones`); verificar que todas las rutas citadas en los árboles existan.

## 2. Modelo y administración

- [x] 2.1 Definir el modelo `Funcion` (campos del esquema, `entradas_compradas` con default 0, `fin` y `disponibilidad` persistidos, FKs con `on_delete=PROTECT`); generar `migrations/0001_initial.py` y verificar con `python movie_up/manage.py migrate` que aplica limpio sobre MySQL.
- [x] 2.2 Registrar `Funcion` en Django Admin; verificar con `python movie_up/manage.py check` y que el modelo sea visible en `/admin/`.

## 3. Service Layer

- [ ] 3.1 Implementar `list_funciones` y `get_funcion` (traducir `DoesNotExist` en `Http404`) en `services.py`; verificar con tests de listado y de 404 para id inexistente en `funciones/tests.py`.
- [ ] 3.2 Implementar `create_funcion` con las validaciones de servicio (inicio presente o futuro en hora de Buenos Aires, precio >= 0, idioma obligatorio hasta 45) y los derivados (`fin` = inicio + duración, copia profunda de la distribución de la sala, `disponibilidad` = conteo de `A`, `entradas_compradas` = 0); verificar con tests de creación válida y de cada rechazo.
- [ ] 3.3 Implementar la validación de solapamiento `[inicio, fin)` por sala dentro de la transacción de guardado con bloqueo de fila de sala, aplicada a activas e inactivas, permitiendo el contacto exacto y excluyendo el propio registro en update; verificar con tests: solapamiento rechazado (incluido un segundo), funciones consecutivas aceptadas, función inactiva bloquea y update sin auto-conflicto.
- [ ] 3.4 Implementar `update_funcion` con update parcial (ausente = conservar), recálculo de `fin` ante cambio de inicio o película, recopia de distribución y recálculo de disponibilidad al cambiar de sala, bloqueo total por `entradas_compradas > 0` y rechazo de activar una función vencida; verificar con tests de cada rama y de 404.
- [ ] 3.5 Implementar `delete_funcion` con bloqueo por `entradas_compradas > 0` y sin eliminar película ni sala; verificar con tests de bloqueo, de borrado exitoso y de 404.

## 4. Vistas, rutas y templates

- [ ] 4.1 Crear las rutas con `app_name='funciones'` y las vistas delgadas de las cinco operaciones (request → servicio → respuesta, `ValueError` → formulario con `error`); verificar con tests de cliente Django que cada ruta responde y que un `ValueError` re-renderiza el formulario sin 500.
- [ ] 4.2 Crear el template de listado con las columnas película, sala, inicio, fin, estado, disponibilidad y precio; verificar con un test que muestra las funciones de fixture con esos datos.
- [ ] 4.3 Crear el template de detalle que muestra película y sala solo por nombre (sin ids) y renderiza la distribución como cuadrícula de solo lectura reutilizando `salas.templatetags.salas_tags`, `salas.css` y `grid.js`; verificar con tests de render: nombres presentes, ids ausentes y clases de celda correctas.
- [ ] 4.4 Crear el formulario de creación con menús desplegables de película y sala, `datetime-local` con mínimo, `precio` con `min=0`, campos obligatorios y selección de estado activo; verificar con tests de POST válido (derivados correctos) y de POST inválido rechazado por el servicio.
- [ ] 4.5 Crear el formulario de actualización precargado con los mismos menús y la vista de eliminación con confirmación; verificar con tests de precarga, de actualización parcial y de confirmación de borrado.

## 5. Verificación de integración

- [ ] 5.1 Correr la suite completa `docker compose exec web python movie_up/manage.py test peliculas salas funciones` y verificar 0 fallos con tests descubiertos.
- [ ] 5.2 Verificar en navegador real vía Playwright crear, editar y eliminar una función en `http://localhost:8000/`, incluida la cuadrícula de solo lectura del detalle y los rechazos visibles, con la consola del navegador sin errores.

## Workflow follow-up

- Dependencia consciente: verificar el estado de la validación `duracion_minutos >= 1` (spec futura de `movies`) antes de implementar; si aún no existe, dejarla registrada.
- Correr `openspec validate --specs --strict` antes de archivar el change.
- Archivar el change cuando se satisfagan los requisitos de revisión.
