# Tasks

## 1. Modelo y migración

- [ ] 1.1 Definir el modelo `Sala` en `movie_up/salas/models.py` con `nombre` (CharField 45, unique), `distribucion` (JSONField), `tipo_sala` (CharField 45), `tipo_sonido` (CharField 45), `capacidad` (PositiveIntegerField) y `__str__` que devuelva el nombre. Verificar: `python movie_up/manage.py makemigrations salas` genera `0001_initial` sin errores.
- [ ] 1.2 Aplicar la migración y comprobar que la tabla existe con su columna JSON. Verificar: `docker compose exec web python movie_up/manage.py showmigrations salas` muestra la migración aplicada y `DESCRIBE salas_sala` incluye `distribucion` de tipo `json`.

## 2. Validación, capacidad y versionado

- [ ] 2.1 Implementar `validar_distribucion(distribucion)` en `movie_up/salas/services.py`: acepta un dict o un string JSON, normaliza espacios y mayúsculas, exige `filas` no vacío, todas las filas de igual longitud, máximo 100×100, celdas restringidas a `P`/`A`/`R` y al menos una celda `A` o `R`. Devuelve la distribución normalizada con `version` coherente o levanta `ValueError` con mensaje accionable. Verificar: tests que cubran distribución válida, filas desiguales, carácter inválido, más de 100 filas, más de 100 columnas, distribución sin butacas y normalización de espacios y minúsculas.
- [ ] 2.2 Implementar `calcular_capacidad(distribucion)` contando `A` y `R` e ignorando `P`. Verificar: tests con matriz mixta (120 `A`, 15 `R`, 40 `P` → 135) y con matriz solo de pasillos (→ 0).
- [ ] 2.3 Implementar la regla de versionado: `1` cuando no hay distribución previa, la misma versión cuando la distribución normalizada es idéntica a la almacenada, y la anterior más 1 cuando difiere. Descartar siempre cualquier `version` que llegue desde el formulario. Verificar: tests de creación, actualización con cambio real, actualización con matriz idéntica y actualización con versión manipulada en el envío.

## 3. Service Layer del CRUD

- [ ] 3.1 Implementar `list_salas()` ordenada por nombre y `get_sala(pk)` que levante `Http404` si no existe. Verificar: tests de listado ordenado y de `get_sala` con ID inexistente.
- [ ] 3.2 Implementar `create_sala(data)`: exigir todos los campos obligatorios, normalizar `tipo_sala` y `tipo_sonido`, rechazar `nombre` duplicado, validar la distribución, fijar `version = 1`, calcular la capacidad derivada e ignorar cualquier `capacidad` recibida. Verificar: tests de creación exitosa, nombre duplicado, distribución inválida, capacidad manipulada y versión manipulada.
- [ ] 3.3 Implementar `update_sala(pk, data)`: aplicar solo los campos escalares con valor omitiendo `None` y `''`, rechazar `nombre` duplicado excluyendo la propia sala, reemplazar la distribución completa cuando venga, aplicar la regla de versionado y recalcular la capacidad en cada guardado. Verificar: tests de actualización parcial, de nombre repetido ajeno, de conservar el propio nombre, de reemplazo de distribución con incremento de versión, de reenvío idéntico sin incremento y de ID inexistente.
- [ ] 3.4 Agregar en `update_sala` y `delete_sala` el bloque `TODO` comentado que consultará funciones activas cuando exista la app `funciones`. Verificar: test que confirme que ambas operaciones funcionan hoy sin la app, y que el bloque comentado no ejecuta queries ni rompe el arranque.

## 4. Estáticos: CSS y JavaScript de la cuadrícula

- [ ] 4.1 Crear `movie_up/salas/static/salas/css/salas.css` con las clases de celda (`celda--pasillo` gris, `celda--asiento` azul, `celda--reservado` dorado), el layout de la cuadrícula y el estilo de los controles de tamaño. Verificar: la hoja se carga en las tres vistas vía `{% load static %}` y los tres colores se distinguen a simple vista.
- [ ] 4.2 Crear `movie_up/salas/static/salas/js/grid.js`: construir la cuadrícula desde `json_script` o en 10×10 todo Pasillo si no hay estado inicial, alternar `P` → `A` → `R` → `P` al hacer clic sobre cada `<button type="button">`, redimensionar con dos `input type="number" min="1" max="100"` conservando las celdas de la intersección y descartando las excedentes, y serializar el estado a un `<input type="hidden" name="distribucion">` con la forma `{"version": N, "filas": [...]}` antes del envío. Verificar: prueba manual en navegador de los cuatro comportamientos, sin errores en consola.
- [ ] 4.3 Implementar la cuadrícula de solo lectura para el detalle en el template, reutilizando `salas.css` y las mismas clases de celda y sin cargar `grid.js`, recorriendo las filas del JSON y emitiendo una celda por carácter con su clase de color. Verificar: el HTML servido contiene las clases correctas para `P`, `A` y `R` y las dimensiones coinciden con la distribución guardada.
- [ ] 4.4 Crear el filtro de template `celda_clase` que traduzca `P`, `A` y `R` a `celda--pasillo`, `celda--asiento` y `celda--reservado`, y un test de paridad que verifique que el mapa equivalente de `grid.js` devuelve exactamente las mismas tres clases. Verificar: el test falla si alguien cambia un color o un nombre de clase solo en un lado.

## 5. URLs, vistas y templates

- [ ] 5.1 Configurar `movie_up/salas/urls.py` con `app_name = 'salas'` y las cinco rutas (lista, detalle, crear, actualizar, eliminar) e incluir `salas.urls` en `movie_up/core/urls.py` bajo `salas/`. Verificar: `python movie_up/manage.py check` sin issues y resolución inversa de cada nombre de ruta.
- [ ] 5.2 Implementar la vista de listado y `templates/salas/list.html` con nombre, tipo de sala, tipo de sonido y capacidad, más enlaces a detalle y creación. Verificar: test de `GET /salas/` con 200 y las salas presentes en el HTML.
- [ ] 5.3 Implementar la vista de detalle y `templates/salas/detail.html`, con la cuadrícula de solo lectura y capacidad y tipos visibles. Verificar: test de 200 con contenido y test de 404 para ID inexistente.
- [ ] 5.4 Implementar la vista de creación y `templates/salas/form.html` con `required`, `maxlength="45"`, los controles de tamaño con `min`/`max` y el contenedor de la cuadrícula. En POST, capturar `ValueError` del service y volver a mostrar el formulario con el mensaje y la distribución enviada. Verificar: test de POST válido que crea y redirige, y test de POST con distribución sin butacas que muestra el error sin crear.
- [ ] 5.5 Implementar la vista de actualización reutilizando `form.html`, precargando todos los campos y entregando la distribución vigente a la cuadrícula vía `json_script`. Verificar: test de GET con campos y cuadrícula precargados, de POST parcial, de reemplazo de distribución y de 404 para ID inexistente.
- [ ] 5.6 Implementar la vista y `templates/salas/confirm_delete.html` con confirmación por POST. Verificar: test de GET con la confirmación y de POST que elimina y redirige.

## 6. Admin

- [ ] 6.1 Registrar `Sala` en `movie_up/salas/admin.py` con `list_display` de nombre, tipo de sala, tipo de sonido y capacidad, y `search_fields` por nombre. Verificar: `python movie_up/manage.py check` sin issues y test que confirme que el modelo está registrado.

## 7. Verificación de integración

- [ ] 7.1 Correr la suite completa del proyecto. Verificar: `docker compose exec web python movie_up/manage.py test` pasa sin fallos, incluyendo los tests de `peliculas`.
- [ ] 7.2 Recorrer el CRUD de salas en navegador real vía Playwright MCP sobre `http://localhost:8000/salas/`, tal como exige AGENTS.md: crear una sala pintando la cuadrícula, verificar la capacidad y la versión 1, editar la distribución y verificar el incremento de versión, reenviar sin cambios y verificar que la versión no sube, y eliminar la sala. Verificar: el recorrido queda registrado y coincide con la spec.
- [ ] 7.3 Invocar al agente `readme-maintainer` para documentar la implementación, el reparto de validaciones y las decisiones no obvias (contador de versiones, guards diferidos, colores como único canal). Verificar: las propuestas quedan presentadas y aplicadas solo tras aprobación explícita.

## Workflow follow-up

- Archivar el change `crud-salas` con `/opsx-archive` una vez aprobada la implementación, verificando antes que `openspec validate --specs --strict` pase.
