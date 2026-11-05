# Design

## Context

Ver `proposal.md` (Why) para la motivación. Hechos que condicionan la solución:

- `templates/home.html` arma el hero con las clases `.hero*` de `static/css/components.css`: 75% de ancho, 55vh de alto, contenido abajo a la izquierda con imagen, título, descripción, género, clasificación y botones `Trailer` / `Comprar entradas`. Los botones de compra de la home apuntan hoy a `#` para cuentas autenticadas.
- `Funcion` ya expone `funcion_activa`, `inicio`, `fin`, `idioma`, `subtitulada`, `precio_entrada`, `disponibilidad` y `distribucion`; `Sala` aporta `tipo_sala`, `tipo_sonido` y `capacidad`. No hace falta un modelo nuevo.
- `entradas/services.py` crea entradas solo si `funcion.fin > now` y elimina con el motivo `finalizacion` sin tocar contadores, disponibilidad ni distribución. La spec `entradas` ya define ese comportamiento.
- `core/settings.py` usa `LOGIN_REDIRECT_URL = '/'`, `SOCIALACCOUNT_LOGIN_ON_GET = True` y `TIME_ZONE = 'America/Argentina/Buenos_Aires'`. El `Login` del nav no lleva `next`, así que retorna a `/`.
- `core/urls.py` incluye una URL por app y `base.html` carga los CSS globales; `STATICFILES_DIRS = [BASE_DIR / 'static']`.

## Goals / Non-Goals

**Goals:**

- Una sola fuente de verdad para el hero y para el gating del botón de compra.
- Vista delgada y lógica en `services.py`, como el resto de las apps.
- Barrido de vencidas acotado, atómico e idempotente, sin tocar los contadores de la función.
- Reutilizar los tokens de la paleta y mantener contraste AA también en el botón deshabilitado.

**Non-Goals:**

- Selección de asientos, creación de entradas y pago con Mercado Pago: cambio posterior.
- Limpieza global de funciones vencidas o tarea programada: solo se barre la película que se está comprando.
- Cambios en el CRUD administrativo de películas, funciones o salas.
- Cambios de modelo o migraciones.

## Decisions

**D1 — App nueva `compras` y ruta `/compras/<pelicula_id>/`.** La app no tiene modelos: orquesta `Pelicula`, `Funcion` y `Entrada`. *Por qué:* `peliculas`, `funciones` y `salas` son CRUD administrativos; `entradas` es persistencia interna de tickets; `core` es el shell del sitio. La compra es un contexto propio que va a crecer con asientos, pago y confirmación. *Alternativas descartadas:* colgar la vista de `peliculas` (mezcla catálogo con comercio), de `funciones` (mezcla administración con venta) o de `core` (convierte el shell en la app pública entera).

**D2 — Hero compartido en `templates/includes/pelicula_hero.html`.** El parcial recibe `pelicula` y `mostrar_compra`; la home lo incluye con `mostrar_compra=True` y la compra con `mostrar_compra=False`. Usa las mismas clases `.hero*`, así que tamaño, posición y contenido no pueden divergir. *Por qué:* el requisito pide "el mismo formato" que el hero de la home; duplicar el markup garantiza que en la próxima modificación se desincronice. *Alternativa descartada:* copiar el bloque en la plantilla de compra o resolverlo con CSS.

**D3 — Gating del botón de compra en un parcial.** `templates/includes/comprar_entradas_button.html` recibe `pelicula` y resuelve:
- cuenta autenticada → enlace a `{% url 'compras:compra_pelicula' pelicula.pk %}`;
- visitante → `{% provider_login_url 'google' process='login' next=purchase_url %}`, donde `purchase_url` se obtiene con `{% url ... as purchase_url %}`.

Lo usan el hero y las tarjetas de la home. El `Login` del nav queda sin `next` y conserva el retorno a `/`. *Por qué:* el `next` de la compra no puede filtrarse al login normal; la distinción vive en el origen del clic, no en una preferencia global.

**D4 — Vista delgada y service orquestador.** `compras/views.py` valida el acceso y delega en `compras/services.py`:
- `obtener_pelicula(pelicula_id)` → `Http404` si no existe;
- `barrer_funciones_vencidas(pelicula_id)`;
- `listar_funciones_vendibles(pelicula_id)`;
- `preparar_compra(pelicula_id)` → película + funciones ya barridas y filtradas.

La vista redirige a `/gestion/` si la cuenta es staff y al login con Google con `next` al path si es visitante. Para el login directo se usa `reverse('google_login')` (allauth lo registra como `/accounts/google/login/`) más `process=login` y `next`, la misma URL que emite el tag. *Por qué:* mantiene el contrato de errores (`Http404`/`ValueError`) y la convención de Service Layer del proyecto. *Alternativa descartada:* consultar y filtrar en la vista.

**D5 — Barrido de vencidas antes del listado.** Dentro de `transaction.atomic`, se bloquean con `select_for_update()` las funciones de la película con `fin <= timezone.now()` y, por cada una:
1. se eliminan todas sus entradas con un helper nuevo `entradas_services.eliminar_entradas_por_finalizacion(funcion_id)`, que hace `Entrada.objects.filter(funcion_id=...).delete()` sin tocar los contadores de la función;
2. se fija `funcion_activa=False`.

El barrido procesa también funciones ya inactivas, para limpiar entradas que hayan quedado colgadas. *Por qué:* una función vencida no puede recibir entradas nuevas (`crear_entrada` rechaza `fin <= now`), así que el borrado masivo es seguro; el helper evita N+1 y la repetición es idempotente. *Alternativa descartada:* recorrer entrada por entrada con `eliminar_entrada(..., 'finalizacion')`, que hace un `select_for_update` por fila y puede fallar si otra carga ya la borró.

La regla de estado vive en la spec `funciones` ("Desactivación automática de funciones vencidas") y la de borrado en `entradas` ("Limpieza masiva por finalización"); `compras` solo aporta el disparador, el orden (antes del listado), la atomicidad y el alcance a la película. El código sigue en `compras/services.py` como orquestador y en `entradas/services.py` como helper; no se duplica la lógica en las otras apps.

**D6 — Listado vendible.** `Funcion.objects.filter(pelicula_id=..., funcion_activa=True, fin__gt=timezone.now()).select_related('sala').order_by('inicio')`. *Por qué:* replica la ventana de venta de `crear_entrada`, así todo lo listado se puede comprar. Una función que ya empezó pero todavía no terminó sigue listada, igual que la permite el servicio de entradas. *Alternativa descartada:* filtrar solo por `funcion_activa`, que mostraría funciones que fallarían al comprar.

**D7 — Botón agotado sin navegación y con contraste.** Con `disponibilidad == 0` se renderiza un `<span class="btn btn--buy btn--sold-out" aria-disabled="true">Entradas agotadas</span>`, sin `href`. El estilo atenúa el fondo con `color-mix(in oklch, var(--primary) 45%, var(--surface))`, mantiene el texto en `--text` y agrega `cursor: not-allowed`. *Por qué:* bajar la opacidad de todo el botón también baja el contraste del texto y rompe la regla AA; atenuar solo el fondo conserva la lectura. *Alternativa descartada:* un `<a href="#">` deshabilitado, que sigue siendo navegable y activable por teclado.

**D8 — Estilos propios en `static/css/compras.css`.** Se carga desde `{% block head %}` de la plantilla de compra. Listado en filas alineadas a la izquierda con el CTA a la derecha en desktop y apilado en móvil; sin tocar `components.css` ni duplicar tokens. *Por qué:* aísla el layout de la compra y respeta la regla de no centrar listados.

**D9 — Precio y fecha.** La fecha se muestra con `date:"d/m/Y H:i"` (hora de Buenos Aires) y el precio con `$` + `floatformat:2`. *Por qué:* es el formato que ya usan los listados administrativos; el separador de miles es-AR queda fuera de este cambio.

## Risks / Trade-offs

- [El barrido muta datos en un `GET`] → es idempotente, atómico, acotado a la película y solo afecta funciones vencidas; si más adelante se necesita cobertura global, conviene un comando programado.
- [Dos cargas simultáneas de la compra] → `select_for_update()` sobre las funciones vencidas y borrado masivo idempotente; una segunda carga no encuentra entradas y no falla.
- [El hero de la home y el de la compra se desincronizan] → un único parcial y verificación en navegador de ambas páginas.
- [El botón agotado pierde contraste al atenuarlo] → atenuar solo el fondo y mantener el texto oscuro; verificar AA en navegador.
- [El listado muestra una función que empieza en minutos y el usuario no llega] → la ventana de venta es la misma que ya valida `crear_entrada`; si se quiere cortar antes del inicio, es una regla de negocio aparte.
- [Una película fuera de cartelera con funciones activas sigue accesible por URL directa] → la home solo enlaza las de cartelera; la página no restringe por `en_cartelera` y no se inventa un 404 adicional.

## Migration Plan

Sin migraciones de esquema ni de datos. Orden de implementación:

1. Crear la app `compras` con `startapp`, registrarla en `INSTALLED_APPS`, incluirla en `core/urls.py`, crear `urls.py`, `services.py` y `templates/compras/.gitkeep`.
2. Extraer el hero y el botón de compra a parciales y actualizar la home.
3. Implementar el barrido, el listado, la vista y la plantilla de compra con sus estilos.
4. Tests de acceso, 404, filtrado, orden, barrido, agotado y vacío; verificación en navegador.

Rollback: revertir el commit del lote; no hay estado persistido más allá de los efectos intencionales del barrido.

## Open Questions

Ninguna pendiente que cambie el alcance, el enfoque o las tareas.
