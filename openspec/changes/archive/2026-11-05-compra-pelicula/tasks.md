# Tasks

## 1. Alta de la app `compras`

- [x] 1.1 Crear la app con la skill `django-app-creator` (`startapp` desde `movie_up/`), registrarla como `'compras',` en `INSTALLED_APPS`, crear `templates/compras/.gitkeep`, `urls.py` y `services.py` vacío, e incluir `path('compras/', include('compras.urls'))` en `core/urls.py` — Verificación: `docker compose exec web python movie_up/manage.py check` termina con 0 errores y los archivos de la app existen.
- [x] 1.2 Actualizar el árbol de `movie_up/` en `AGENTS.md` y `README.md` con la línea `compras/` en orden alfabético, según la skill — Verificación: ambos árboles listan `compras/` antes de `cuentas/` y conservan `core/` como último elemento.

## 2. Hero y gating compartidos

- [x] 2.1 Extraer el hero de `templates/home.html` a `templates/includes/pelicula_hero.html` con `pelicula` y `mostrar_compra`, y hacer que la home lo incluya con `mostrar_compra=True` — Verificación: la home renderiza el mismo hero (imagen, título, descripción, género, clasificación y botón `Trailer` dentro) y los tests de `core` siguen pasando.
- [x] 2.2 Extraer el botón de compra a `templates/includes/comprar_entradas_button.html`: autenticado → `/compras/<pelicula_id>/`; visitante → `provider_login_url` con `next` a esa página; usarlo en el hero y en las tarjetas de la home — Verificación: tests de `core` que afirman el `href` de cada tarjeta y el `next` del visitante, y el `Login` del nav sigue apuntando a `next='/'`.

## 3. Servicios de compra

- [x] 3.1 Agregar `eliminar_entradas_por_finalizacion(funcion_id)` en `entradas/services.py`, que borra todas las entradas de la función sin tocar sus contadores, disponibilidad ni distribución — Verificación: tests en `entradas/tests.py` de borrado completo, de función sin entradas, de idempotencia, de otra función intacta y de contadores intactos.
- [x] 3.2 Implementar en `compras/services.py` `obtener_pelicula`, `barrer_funciones_vencidas`, `listar_funciones_vendibles` y `preparar_compra`, con barrido atómico `select_for_update` acotado a la película, filtro `funcion_activa=True` + `fin > now` y orden por `inicio` — Verificación: tests en `compras/tests.py` de 404, película inexistente, funciones activas/futuras, exclusión de inactivas y vencidas, orden, barrido de entradas, `funcion_activa=False`, campos de la función intactos, idempotencia y otra película sin tocar.

## 4. Vista, URL y plantilla

- [x] 4.1 Implementar `compra_pelicula(request, pelicula_id)` y su ruta `/compras/<pelicula_id>/`: visitante → login de Google con `next` a esa página; staff → `/gestion/`; cuenta común → render de la compra — Verificación: tests de los tres accesos y del 404.
- [x] 4.2 Crear `templates/compras/compra_pelicula.html` con el hero sin botón de compra, el listado de funciones con inicio, tipo de sala, tipo de sonido, idioma, subtitulada, precio con `$`, disponibilidad y CTA, el estado vacío y el botón `Entradas agotadas` deshabilitado cuando la disponibilidad es 0 — Verificación: tests que renderizan un ítem completo, el estado vacío y el botón agotado sin `href`, y que la página carga `static/css/compras.css` en el `<head>`.
- [x] 4.3 Crear `static/css/compras.css` con el listado en filas alineadas a la izquierda, el CTA a la derecha en desktop y apilado en móvil, y el fondo atenuado del botón agotado con texto de contraste AA — Verificación: Playwright revisa la página en desktop y móvil, el color computado del botón agotado y la ausencia de desbordes.
- [x] 4.4 Renderizar el botón `Comprar entradas` de cada función sin destino en este cambio — Verificación: test que afirma que el ítem de una función con disponibilidad mayor que cero incluye el texto `Comprar entradas` y no tiene `href`.

## 5. Integración y verificación

- [x] 5.1 Correr la suite completa, `manage.py check` y `manage.py makemigrations --check` — Verificación: `docker compose exec web python movie_up/manage.py test compras peliculas salas funciones cuentas entradas core`, `check` y `makemigrations --check` terminan con 0 errores.
- [x] 5.2 Validar la spec del cambio en modo estricto — Verificación: `openspec validate compra-pelicula --strict` sale con código 0.
- [x] 5.3 Verificar en navegador real: visitante desde la home al login con `next` de compra, cuenta común en la compra con el hero y el listado, función agotada, película sin funciones, cuenta administradora redirigida a `/gestion/` y consola limpia — Verificación: registro de pantallas con la URL y el estado observado en cada caso.

## Workflow follow-up

- Presentar el diff pendiente y esperar la aprobación explícita del usuario antes de cualquier `git add`, `git commit` o `git push`.
- Registrar el cambio en el README con el agente `readme-maintainer` cuando el usuario lo solicite.
- Archivar `compra-pelicula` bajo pedido explícito, después de `openspec validate compra-pelicula --strict`.
