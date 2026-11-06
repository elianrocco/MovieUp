# Proposal

## Why

Las vistas de compra y de entradas quedaron funcionalemente completas pero visualmente desnudas: el listado de funciones parte los datos en dos líneas, la vista de selección de asientos muestra cuadrícula, datos y resumen sueltos sobre el fondo sin jerarquía, y `/entradas/` (lista y detalle) ni siquiera carga CSS. Además, el detalle no ofrece ninguna acción para reembolsar aunque el servicio de reembolso ya existe y funciona.

## What Changes

- **Listado de funciones en una sola línea**: cada ítem de `/compras/<id>/` muestra sus siete datos en la misma fila, sin salto entre `Idioma` y `Subtitulada`.
- **Paneles de la vista de selección**: `Elija sus asientos` y la cuadrícula dentro de un rectángulo redondeado **dorado** (token `--gold`, el mismo del botón `Mis entradas` del nav) con margen del 10% del ancho de pantalla a cada lado y padding vertical apenas suficiente; debajo, las filas de datos dentro de un rectángulo redondeado **blanco** del mismo ancho, **pegado por arriba** al panel dorado y con margen entre filas; el resumen (cantidad, total y confirmación) en un tercer rectángulo blanco idéntico **con margen arriba y abajo**.
- **Botón de éxito debajo del mensaje**: en la pantalla de compra realizada, `Mis entradas` pasa a estar debajo de `Compra realizada con éxito, puede ver sus entradas en`, centrado, con un margen pequeño arriba y con el **dorado** del nav en lugar del rojo.
- **Listado de `/entradas/` estilado**: cada registro dentro de un rectángulo dorado redondeado, los registros centrados y el enlace al detalle convertido en un botón dorado con contorno rojo. La app `entradas` gana su propio CSS.
- **Detalle de `/entradas/<id>/` estilado**: todo centrado, con márgenes entre los items y dentro de un rectángulo dorado; `Volver a mis entradas` pasa a botón dorado con contorno rojo y se agrega al lado un segundo botón `Reembolso`.
- **Reembolso funcional desde el detalle**: el botón `Reembolso` envía un `POST` a una ruta nueva que invoca el servicio existente `eliminar_entrada(motivo='reembolso')`; en éxito vuelve al listado, y en cualquier rechazo (entrada validada o inicio a menos de 24 horas) muestra el motivo en el detalle sin modificar ningún dato.
- **Solo escritorio**: la app es solo para PC; toda la verificación de este cambio es de escritorio (sin pruebas móviles).
- **BREAKING**: ninguna.

## Capabilities

### New Capabilities

- (ninguna: la estética de compra pertenece a `compras` y la de entradas a `entradas`)

### Modified Capabilities

- `compras`: MODIFIED de "Datos de cada función" (los siete datos del ítem en una sola línea), "Cuadrícula de asientos de la función" (encabezado y grilla dentro del panel dorado), "Datos de solo lectura de la compra" (filas dentro del panel blanco pegado al dorado) y "Resumen de la compra" (resumen dentro de un panel blanco con márgenes); MODIFIED de "Vista de compra realizada" (botón debajo del mensaje, centrado y dorado).
- `entradas`: ADDED de "Presentación del listado de entradas" (registros en rectángulos dorados centrados y enlace de detalle como botón dorado con contorno rojo), "Presentación del detalle de entrada" (todo centrado en rectángulo dorado con dos botones) y "Reembolso desde el detalle de la entrada" (disparador funcional del servicio de reembolso existente).

## Impact

- **`movie_up/static/css/compras.css`**: paneles dorado y blancos con bordes redondeados, una sola línea en el listado de funciones, botón de éxito dorado.
- **`movie_up/templates/compras/`**: wrappers de panel en `compra_pelicula.html` y `seleccion_asientos.html`, y reordenamiento vertical del bloque de éxito en `compra_exitosa.html`.
- **Nueva CSS de la app `entradas`**: `movie_up/entradas/static/entradas/css/entradas.css` cargado con `{% block head %}` en `list.html` y `detail.html`.
- **`movie_up/entradas/templates/entradas/`**: tabla reconvertida en tarjetas doradas centradas, detalle dentro de rectángulo dorado con botones, y formulario de reembolso con `{% csrf_token %}`.
- **`movie_up/entradas/{urls,views}.py`**: ruta y vista `POST` de reembolso que delega en `eliminar_entrada` sin tocar `services.py` ni los modelos.
- **Sin migraciones**: no cambian modelos ni datos.
- **Tests**: `entradas/tests.py` (reembolso desde el detalle: éxito, rechazos, propiedad y método) y `compras/tests.py` (paneles y una sola línea), más verificación Playwright **solo desktop**.
