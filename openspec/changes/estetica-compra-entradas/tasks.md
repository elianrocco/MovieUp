# Tasks

## Lote 1 — Compras

## 1. Listado de funciones en una sola línea

- [ ] 1.1 Cambiar `.funcion-item__meta` en `movie_up/static/css/compras.css` de un grid fijo de 4 columnas a `flex` con wrap y items a ancho de contenido, quitando los media queries de columnas de ese bloque; verificar en navegador desktop (1280×900) con Playwright que los siete datos de cada ítem comparten la misma fila (misma coordenada `top`) y que `docker compose exec web python movie_up/manage.py test compras` sigue pasando.

## 2. Paneles de la vista de selección

- [ ] 2.1 Envolver el encabezado + cuadrícula, las filas de datos y el resumen en wrappers `.panel--gold` y `.panel--light` en `movie_up/templates/compras/seleccion_asientos.html` y crear sus estilos en `compras.css` (`margin-inline: 10vw`, `border-radius: 12px`, `--gold` con el título en `--on-gold`, `--surface` en los blancos, panel de datos sin margen superior para quedar pegado al dorado, `margin-block` en el del resumen, y `.seleccion` sin `width: 75%`), verificando con tests de plantilla (clases de los tres paneles) y con Playwright desktop: ancho del panel igual al 80% de la ventana, contacto entre el panel dorado y el blanco de datos, margen arriba y abajo del resumen y consola sin errores.

## 3. Pantalla de éxito con botón dorado

- [ ] 3.1 Agregar `.btn--gold` (fondo `--gold`, texto `--on-gold`, hover en opacidad) y `.btn--gold-outline` (mismo fondo + contorno `--primary`) en `movie_up/static/css/components.css`, y pasar `.exito` a columna en `compra_exitosa.html` + `compras.css` con el botón `Mis entradas` debajo del mensaje, centrado, con margen pequeño arriba y la clase `.btn--gold`; verificar con test de plantilla (orden mensaje→botón y clases) y con Playwright desktop que el botón queda debajo y centrado sobre fondo dorado con `href="/entradas/"`.

## Lote 2 — Entradas

## 4. Listado de entradas en tarjetas doradas

- [ ] 4.1 Crear `movie_up/entradas/static/entradas/css/entradas.css` y cargarlo con `{% block head %}` en `entradas/list.html`; reconverter la tabla en un `<ul>` de `.entrada-card` con fondo `--gold`, `border-radius: 12px`, registros centrados, campos con la etiqueta encima y el enlace `Ver entrada` con la clase `.btn--gold-outline`; verificar que los tests de listado existentes de `movie_up/entradas/tests.py` pasan sin tocarlos, que un test nuevo de clases (rectángulo dorado, botón con contorno) pasa, y con Playwright desktop dejar captura del listado con registros centrados y consola sin errores.

## 5. Detalle de entrada en panel dorado con dos botones

- [ ] 5.1 Envolver el `<dl>` de `entradas/detail.html` en `.panel--gold` con los datos centrados y `gap` entre items, cargar `entradas.css` con `{% block head %}` y agregar los estilos del detalle; reemplazar la navegación por una fila centrada con el enlace `Volver a mis entradas` en `.btn--gold-outline` y, al lado, un `<form method="post">` con `{% csrf_token %}` cuyo botón `Reembolso` usa el mismo perfil; verificar con test de plantilla (ambos botones, formulario con token) y que los tests de detalle existentes pasan sin cambios, más captura Playwright desktop.

## 6. Reembolso funcional desde el detalle

- [ ] 6.1 Agregar la ruta `entradas:entrada_reembolsar` (`<int:pk>/reembolso/`) y la vista con `@login_required` + `@require_POST` que resuelve la entrada con `obtener_entrada` (ajena o inexistente → 404), llama a `eliminar_entrada(entrada.pk, 'reembolso')`, re-renderiza el detalle con `.error-message` cuando el servicio lanza `ValueError` y redirige a `entradas:entrada_list` en éxito; verificar con tests: el éxito borra la entrada, revierte la función (disponibilidad, entradas compradas y celda `R`→`A`) y redirige al listado; una entrada validada o con inicio a menos de 24 horas muestra el motivo y permanece; la entrada ajena responde 404; el GET responde 405; el POST sin sesión redirige al login.

## 7. Verificación de integración

- [ ] 7.1 Correr la suite completa `docker compose exec web python movie_up/manage.py test peliculas salas funciones cuentas entradas compras core`, más `manage.py check` y `manage.py makemigrations --check --dry-run`, y verificar que todo pasa sin errores ni migraciones pendientes.
- [ ] 7.2 Repetir la verificación Playwright final **solo en desktop** (1280×900) de los dos recorridos — compras: listado en una línea → paneles → selección → éxito; entradas: listado en tarjetas → detalle → reembolso real por POST con datos temporales limpiados al terminar — con consola sin errores y capturas nuevas en `.playwright-mcp/`.

## Workflow follow-up

- Validar con `openspec validate estetica-compra-entradas --strict` y `openspec validate --specs --strict` antes de archivar.
- Archivar el cambio con `openspec archive estetica-compra-entradas` cuando el usuario lo pida, y actualizar los árboles de `AGENTS.md`/`README.md`.
- No invocar al agente `readme-maintainer` (instrucción explícita del usuario).
