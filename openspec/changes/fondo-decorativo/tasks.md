# Tasks

## 1. Capas del fondo decorativo

- [x] 1.1 Implementar en `movie_up/static/css/base.css` los degradados radiales (más claro arriba, más dorado abajo) y la capa de grano de película en SVG data-URI con opacidad muy baja, como capas de `background` de `body` (D2, D3); verificar con una captura de página completa de la home en Playwright a 1280×900 que ambas capas se distinguen del crema plano y guardarla en `.playwright-mcp/`.
- [x] 1.2 Agregar en `base.css` las cintas verticales a ambos costados: banda en ink de baja opacidad con perforaciones en crema y separadores de fotograma en dorado al 35% (D3, D4); verificar con una captura de página completa que las cintas aparecen a izquierda y derecha sin tapar contenido.
- [x] 1.3 Agregar en `base.css` las cintas cruzadas en diagonal sobre todo el fondo, con alfa menor que las verticales y por debajo de ellas en la pila de `background` (D3, D4); verificar con una captura de página completa que cruzan el fondo detrás del contenido.

## 2. Verificación integrada

- [x] 2.1 Correr la suite completa `python movie_up/manage.py test peliculas salas funciones cuentas entradas compras core estadisticas` con 0 fallos, `python movie_up/manage.py check` con 0 errores y `python movie_up/manage.py makemigrations --check` sin cambios pendientes.
- [x] 2.2 Verificar en Playwright a 1280×900 la home y `/gestion/` con capturas de página completa (nunca de elemento: el `backdrop-filter` del nav produce artefactos): las cuatro capas visibles, texto legible sobre el fondo, un clic real (p. ej. `Trailer` o una pestaña del subNAV) que llega a su destino, consola sin errores; guardar las capturas en `.playwright-mcp/`.

## Workflow follow-up

- Revisar el cambio con el usuario y, tras su aprobación, archivarlo (`openspec validate --specs --strict` previo) actualizando los árboles de AGENTS.md y README.md.
