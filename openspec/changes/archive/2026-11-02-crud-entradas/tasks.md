# Tasks

## 1. Modelo y migración

- [x] 1.1 Crear el modelo `Entrada` en `movie_up/entradas/models.py` con `db_table = 'entrada'`, `funcion` y `cuenta` en `PROTECT` e índice único compuesto `(funcion, l_fila, n_asiento)`, y verificar que `docker compose exec web python movie_up/manage.py makemigrations entradas` genera `0001_initial`.
- [x] 1.2 Aplicar la migración y verificar con `manage.py migrate --plan` que solo se agrega la tabla `entrada`, y con `manage.py check` que sale en 0 con únicamente los 2 warnings `W036` conocidos.

## 2. Creación interna

- [x] 2.1 Implementar en `services.py` la conversión entre posición de fila y etiqueta alfabética base-26, verificando con tests que fila 1 → `A`, fila 26 → `Z`, fila 27 → `AA`, y que una etiqueta sin fila correspondiente lanza `ValueError` con mensaje en español.
- [x] 2.2 Implementar `crear_entrada` con las validaciones de función existente y no vencida, celda `A`, rango de asiento ordinal entre `A`/`R` (sin contar `P`) y generación de código con `secrets`, verificando con tests que los pasillos no incrementan `n_asiento`, las celdas `R` sí conservan posición y cada rechazo lanza `ValueError` sin persistir entrada.
- [x] 2.3 Verificar con tests que una creación exitosa actualiza los tres derivados a la vez (`entradas_compradas + 1`, `disponibilidad - 1`, celda → `R`) y que una creación rechazada deja la función exactamente igual.
- [x] 2.4 Verificar con un test de concurrencia que dos creaciones simultáneas para el mismo asiento persisten solo una entrada.
- [x] 2.5 Verificar con tests que los códigos generados son distintos entre entradas, usan solo caracteres del alfabeto de 32 sin ambiguos, se guardan en mayúsculas y que la base rechaza un código duplicado.

## 3. Eliminación con motivo

- [x] 3.1 Implementar `eliminar_entrada(entrada, motivo)` aceptando únicamente `reembolso` y `finalizacion`, con `Http404` ante una entrada inexistente, verificando con tests el rechazo de un motivo desconocido y el 404.
- [x] 3.2 Verificar con tests que el reembolso borra la entrada y revierte la función en la misma operación (`entradas_compradas - 1`, `disponibilidad + 1`, celda → `A`).
- [x] 3.3 Verificar con tests que la eliminación por finalización borra la entrada sin modificar entradas compradas, disponibilidad ni distribución.
- [x] 3.4 Verificar con tests que el reembolso se rechaza cuando la entrada ya fue validada (`activa = False`), informa el motivo y la entrada permanece.
- [x] 3.5 Verificar con un test de invariante que, tras crear y reembolsar, `disponibilidad` vuelve a coincidir con el conteo de celdas `A` y `entradas_compradas` queda en 0.
- [x] 3.6 Implementar en `eliminar_entrada` el límite de anticipación de 24 horas sobre `Funcion.inicio`, aplicado únicamente cuando el motivo es `reembolso`, y verificar con tests que con más de 24 horas se acepta, con menos se rechaza con mensaje en español y que la entrada permanece.
- [x] 3.7 Verificar con tests el borde exacto de 24 horas (acepta), que una función ya iniciada rechaza el reembolso, y que la eliminación por finalización se ejecuta igual cuando la función ya finalizó.

## 4. Listado y detalle

- [x] 4.1 Implementar el servicio y la vista de listado filtrado por la cuenta de la sesión, verificando con tests que solo aparecen las entradas propias, que el resumen incluye título, sala, inicio, fila, asiento y estado, y que una cuenta sin entradas ve la lista vacía.
- [x] 4.2 Implementar el detalle con control de propiedad, verificando con tests que la cuenta dueña recibe 200 y que una entrada ajena o inexistente responde 404.
- [x] 4.3 Verificar con un test de contenido que el detalle muestra código, fila, asiento, estado, título de la película, inicio, y nombre, tipo de sala, tipo de sonido y capacidad de la sala, y que el HTML no contiene identificadores, distribuciones ni campos de administración.
- [x] 4.4 Registrar las rutas de la app y montarlas en `movie_up/core/urls.py`, verificando con tests que listado y detalle responden y que las rutas candidatas de alta y de borrado responden 404.

## 5. Validación en puerta

- [x] 5.1 Implementar la validación atómica por código en `services.py`, verificando con tests que un código activo informa "encontrada" y deja `activa = False`, que repetir el mismo código informa "no encontrada", y que un código inexistente informa "no encontrada".
- [x] 5.2 Implementar la vista y el template de validación, verificando con tests que el personal autorizado puede validarla y que una cuenta sin ese permiso es denegada.
- [x] 5.3 Verificar con un test de concurrencia que dos validaciones simultáneas del mismo código informan "encontrada" una sola vez.

## 6. Admin y guard de cuentas

- [x] 6.1 Registrar `EntradaAdmin` de solo lectura, sin permiso de eliminación y sin acciones masivas, verificando con un test que el panel no ofrece borrado de entradas.
- [x] 6.2 Activar los guards `TODO(entrada)` de `movie_up/cuentas/admin.py` en `delete_model` y `delete_queryset`, verificando con tests que una cuenta con entradas no se borra por ninguna de las dos vías y que una cuenta sin entradas se borra por ambas.
- [x] 6.3 Actualizar el test `cuentas/tests.py:375`, que hoy exige `source.count('TODO(entrada)') == 2`, y verificar que la suite de `cuentas` pasa con el guard activo.

## 7. Verificación e integración

- [x] 7.1 Correr la suite completa con `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas` y verificar que termina en OK.
- [x] 7.2 Verificar `docker compose exec web python movie_up/manage.py makemigrations --check --dry-run` limpio y `manage.py check` en 0 con solo los 2 warnings `W036` conocidos.
- [x] 7.3 Verificar en navegador real con Playwright MCP el listado, el detalle y la vista de validación en `http://localhost:8000/`, y registrar el resultado en el README.
- [x] 7.4 Documentar el caso de uso de entradas en `AGENTS.md` y `README.md` y verificar que todos los enlaces relativos del README apuntan a archivos existentes.
- [x] 7.5 Correr `openspec validate crud-entradas --strict` y verificar exit 0.

## Workflow follow-up

- Revisar los artefactos con el usuario antes de implementar; los cambios de alcance detectados se plantean acá y no en código.
- Archivar el change con `/opsx:archive` una vez completadas todas las tareas, sincronizando `openspec/specs/entradas/spec.md` y actualizando el requisito de `cuentas`.
