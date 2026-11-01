# Proposal

## Why

MovieUp ya gestiona su catálogo de películas, pero no puede vender una entrada sin un lugar físico donde proyectar. `salas` es el segundo dominio del sistema y el bloqueante directo de `funciones`: una función es la combinación de una película, una sala y un horario. Sin salas no se puede avanzar hacia ventas.

A diferencia de una película, una sala no es un registro plano: su valor está en la distribución física de butacas. Por eso la entidad introduce el primer dato estructurado del proyecto, la distribución, que las funciones van a copiar y modificar de forma aislada. También introduce la primera interfaz interactiva: cargar una matriz de butacas por texto libre es impracticable, así que el editor necesita CSS y JavaScript.

## What Changes

- Nuevo modelo `Sala` en `movie_up/salas/models.py` con los campos de la tabla `sala`: `nombre` (VARCHAR 45), `distribucion` (JSON), `tipo_sala` (VARCHAR 45), `tipo_sonido` (VARCHAR 45) y `capacidad` (entero sin signo).
- `distribucion` almacena un documento `{"version": N, "filas": ["AAPA...", ...]}`: una matriz de M filas × N columnas, cada celda uno de tres caracteres (`P` Pasillo, `A` Asiento, `R` Reservado), con un máximo de 100×100.
- **Editor de distribución en cuadrícula:** tamaño ajustable entre 1 y 100 por lado, arranca en 10×10 con todas las celdas en Pasillo, y cada clic alterna Pasillo, Asiento y Reservado. Los colores son gris, azul y dorado respectivamente.
- **Primeros estáticos del proyecto:** una hoja de estilos y un script sin framework ni build, servidos por `django.contrib.staticfiles`, que ya está configurado.
- `capacidad` es un valor **derivado**: se recalcula en la capa de servicio en cada creación y actualización contando las celdas `A` y `R`, e ignorando las `P`. Nunca se acepta desde el formulario.
- `version` es un **contador de revisiones**: arranca en 1 y sube uno cada vez que la distribución cambia realmente; si se reenvía la misma, se conserva. El cliente nunca la dicta.
- **Validación en dos niveles:** el navegador bloquea campos obligatorios vacíos, largos excedidos y dimensiones fuera de rango; el service revalida esas reglas y agrega las que el navegador no puede verificar (nombre único, existencia del registro, composición de la matriz, funciones activas).
- Validación de la matriz en el service: forma rectangular, filas de igual longitud, alfabeto restringido, tope de tamaño y al menos una butaca.
- Unicidad de `nombre`: el sistema rechaza crear o actualizar una sala con un nombre ya existente, sin rechazar el nombre actual de la propia sala.
- Service layer en `services.py` con las cinco operaciones CRUD, siguiendo la convención del proyecto: `list_salas()`, `get_sala(pk)`, `create_sala(data)`, `update_sala(pk, data)` y `delete_sala(pk)`.
- Vistas basadas en funciones, URLs con namespace `salas` y registro del modelo en el admin de Django.
- **Guards condicionales** para impedir actualizar o eliminar una sala con funciones activas: bloque `TODO` comentado con el mismo patrón que `delete_pelicula`, porque la app `funciones` todavía no existe.
- Inclusión de `salas.urls` en `movie_up/core/urls.py`.

## Capabilities

### New Capabilities

- `salas`: gestión del catálogo de salas físicas del complejo, incluida su distribución versionada de butacas, el editor visual de la cuadrícula, el cálculo derivado de capacidad, la validación en dos niveles y las reglas de integridad que habilitan la futura planificación de funciones.

### Modified Capabilities

(Ninguna: la capability `movies` no cambia de comportamiento. La relación con salas aparece recién con `funciones`, y se declarará en el delta de esa capability.)

## Impact

- **Código**: `movie_up/salas/` (models.py, services.py, views.py, urls.py, admin.py, tests.py, templates/salas/, static/salas/). Cambio en `movie_up/core/urls.py` para incluir las rutas.
- **Frontend**: primera app con CSS y JavaScript del proyecto. `peliculas` queda sin estilos, así que la inconsistencia visual es transitoria y aceptada.
- **Base de datos**: nueva tabla `salas_sala` con una columna JSON. Requiere migración inicial. MySQL 9.7.2 soporta el tipo JSON de forma nativa.
- **APIs**: endpoints HTTP bajo `/salas/` (GET y POST), server-rendered, sin API REST.
- **Dependencias**: ninguna nueva. `JSONField` viene incluido en Django 6.1.1 y los estáticos usan la infraestructura existente.
- **Sistemas**: backend Django, base de datos y una capa de presentación nueva. No toca autenticación ni pagos.
- **Contrato hacia adelante**: la forma del JSON es un contrato que `funciones` va a consumir y copiar. `version` cuenta revisiones y viaja dentro del documento para que cada copia conserve su historia. Además, la semántica de `R` (Reservado, butaca no ofrecida a la venta) es parte del contrato.
