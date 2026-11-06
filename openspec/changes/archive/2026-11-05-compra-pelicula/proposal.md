# Proposal

## Why

Hoy el botón `Comprar entradas` de la portada no tiene destino para una cuenta autenticada: la spec `ui` lo dejó explícitamente "a la espera de la vista de compra". Sin esa vista el cliente no puede elegir una función ni iniciar una compra. Además, una función puede quedar vencida con `funcion_activa=True` y conservar entradas asociadas, y hoy nada las limpia al ritmo del uso.

## What Changes

- **Nueva página de compra por película** en `/compras/<pelicula_id>/`, accesible para cuentas comunes autenticadas. Un visitante es conducido al login con Google con retorno a esa página; una cuenta administradora es redirigida a `/gestion/`; una película inexistente responde 404.
- **Portada reutilizada**: la página abre con el mismo hero de la home (mismas dimensiones, posición y contenido: imagen, título, descripción, género, clasificación y botón `Trailer` dentro), sin el botón de compra.
- **Listado de funciones vendibles**: solo funciones de la película con `funcion_activa=True` y `fin > ahora`, ordenadas por inicio. Cada ítem muestra inicio, tipo de sala, tipo de sonido, idioma, subtitulada, precio con `$`, disponibilidad y botón `Comprar entradas`.
- **Barrido de funciones vencidas al cargar**: antes de listar, las funciones de esa película con `fin <= ahora` eliminan sus entradas con motivo `finalizacion` (sin tocar contadores, disponibilidad ni distribución) y pasan a `funcion_activa=False`. El barrido es atómico, idempotente y acotado a la película.
- **Entradas agotadas**: con disponibilidad 0 el botón queda deshabilitado, con el rojo primario atenuado y el texto `Entradas agotadas`.
- **Estado vacío**: sin funciones vendibles, la página muestra un mensaje en lugar del listado.
- **Enlaces de compra**: los botones de compra de la home apuntan a la página de compra de su película; el `Login` del nav conserva el retorno a `/`.
- **Fuera de alcance**: el comportamiento del botón `Comprar entradas` de cada función (selección de asientos y pago) se define en un cambio posterior; en este cambio el botón se renderiza sin destino.
- **BREAKING**: ninguna.

## Capabilities

### New Capabilities

- `compras`: página de compra por película, portada reutilizada, listado de funciones vendibles, barrido de funciones vencidas, disponibilidad agotada y estado vacío.

### Modified Capabilities

- `ui`: REMOVED del requisito "Gating de Comprar entradas" y ADDED de "Acceso a la compra desde la portada y el nav" (el botón ahora navega a la página de compra y el login iniciado desde la compra retorna a esa página, mientras el `Login` del nav sigue retornando a `/`).
- `funciones`: ADDED del requisito "Desactivación automática de funciones vencidas" (el barrido de la compra desactiva las funciones con fin transcurrido).
- `entradas`: ADDED del requisito "Limpieza masiva por finalización" (el barrido borra todas las entradas de una función vencida sin tocar sus contadores).

## Impact

- **Nueva app `compras`**: `views.py`, `urls.py`, `services.py`, `tests.py` y `templates/compras/compra_pelicula.html`; alta en `INSTALLED_APPS` y `core/urls.py`; el árbol de `AGENTS.md` y `README.md` se actualiza con la skill `django-app-creator`.
- **`movie_up/templates/includes/`**: extracción del hero de `home.html` a un parcial reutilizable y de un parcial para el botón de compra con su gating.
- **`movie_up/static/css/`**: estilos del listado de funciones y del estado agotado sobre los tokens de la paleta.
- **`movie_up/templates/home.html`**: el hero y las tarjetas usan el parcial de compra y apuntan a `/compras/<id>/`.
- **`movie_up/entradas/services.py`**: helper de eliminación masiva por finalización, idempotente y sin tocar los contadores de la función.
- **Sin cambios de modelo ni migraciones**: se usan `Pelicula`, `Funcion`, `Sala` y `Entrada` existentes.
- **Tests**: nuevos de `compras` (acceso, 404, filtrado, orden, barrido, agotado y vacío) y ajuste de `core/tests.py` para los enlaces de compra.
