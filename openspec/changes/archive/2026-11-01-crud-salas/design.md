# Design

## Context

Ver `proposal.md` — Why. `salas` es la segunda app de dominio del proyecto y sigue el patrón de `peliculas`: MVT con Service Layer, vistas basadas en funciones y URLs con namespace. La app ya existe como andamio vacío (`models.py`, `views.py`, `urls.py`, `services.py`, `admin.py`, `tests.py`, `templates/salas/`), registrada en `INSTALLED_APPS` como `'salas'`.

Stack verificado: Django 6.1.1 con `mysqlclient` 2.2.8 sobre MySQL 9.7.2. El tipo `JSON` de MySQL está disponible de forma nativa y `JSONField` es parte del core de Django, así que no se agregan dependencias.

Diferencia importante con `peliculas`: esta capability introduce **CSS y JavaScript**. `peliculas` son cuatro templates HTML sin una sola hoja de estilo, así que `salas` va a ser la primera app con estáticos del proyecto. La infraestructura ya existe (`django.contrib.staticfiles` en `INSTALLED_APPS` y `STATIC_URL = 'static/'` en `core/settings.py`), pero no hay ningún archivo en `static/` todavía.

## Goals / Non-Goals

**Goals:**

- Un modelo `Sala` que persista la distribución como documento versionado.
- Un editor de distribución usable: cuadrícula clickeable, tamaño ajustable y colores por tipo.
- Repartir las validaciones: el navegador bloquea lo que puede bloquear, el service revalida todo y cubre lo que el navegador no ve.
- Concentrar en el Service Layer la validación de la matriz y el cálculo de capacidad, de modo que `funciones` pueda reutilizar ambas cosas cuando copie la distribución.

**Non-Goals:**

- Copias de la distribución por función, edición aislada y disponibilidad de butacas: pertenecen a la capability `funciones`.
- Accesibilidad cromática (daltonismo, contraste): el usuario la excluyó explícitamente de esta implementación. Los colores son el único canal visual.
- Framework de frontend o paso de build: JavaScript ES2025 servido tal cual.
- Autenticación y autorización, igual que en `peliculas`.
- Cambiar la capability `movies`.

## Decisions

### 1. `JSONField` para la distribución

**Decision:** `distribucion = models.JSONField()`.

**Rationale:** Es un documento que se lee y se escribe entero, nunca se consulta por celda. MySQL lo almacena y lo valida como JSON nativo, y Django no requiere serialización manual.

**Alternativas consideradas:**

- Tablas `Fila` y `Butaca` normalizadas: permitiría consultar butacas individuales, pero convierte una distribución de 120 butacas en 120 filas por sala y multiplica el problema cuando cada función copie la distribución. Se pospone hasta que las ventas necesiten reservar butacas, si es que lo necesitan.
- `TextField` con JSON serializado a mano: obliga a parsear y serializar en cada lectura, sin validación de la base.

### 2. Filas como strings, no como arrays de caracteres

**Decision:** `{"version": 1, "filas": ["AAPA...", "ARPA..."]}`.

**Rationale:** Un string por fila es compacto, la validación de rectangularidad se reduce a comparar longitudes, y el render es un `for` sobre las filas. Un array de arrays equivaldría a más JSON para la misma información.

**Trade-off:** No hay lugar para metadata por butaca (tipo, numeración). Se resuelve con una nueva versión de la distribución cuando haga falta.

### 3. El número de versión vive dentro del JSON y cuenta revisiones

**Decision:** `distribucion["version"]`, entero que arranca en 1 y se incrementa en 1 cada vez que la distribución cambia.

**Rationale:** Cuando `funciones` copie la distribución va a copiar el JSON completo; si la versión fuera una columna aparte, la copia nacería sin versión o con una desincronizada. Dentro del documento, la versión viaja con el dato.

**Regla de incremento:** el service normaliza la distribución entrante, la compara con la almacenada y recién ahí decide:

- Sin distribución previa (creación): `version = 1`.
- Distribución entrante idéntica a la almacenada: se conserva la versión.
- Distribución entrante distinta: la versión almacenada más 1.

La comparación se hace **después** de normalizar, para que un cambio de espacios o de mayúsculas no cuente como revisión. La versión que envíe el cliente se descarta siempre.

**Trade-off asumido:** el campo deja de identificar la forma del documento y pasa a identificar la cantidad de revisiones. Si en el futuro la forma cambia, va a hacer falta un campo aparte que describa la estructura. Un solo entero no puede contar dos cosas.

### 4. `capacidad` derivada en el service, no calculada por la base

**Decision:** El service cuenta `A` y `R` y persiste el resultado en la columna `capacidad`.

**Rationale:** La DDL exige la columna, así que tiene que ser un campo real y no un `@property`. Una columna generada por MySQL obligaría a escribir funciones JSON en la migración, fuera del alcance del ORM y difíciles de versionar.

**Riesgo asumido:** cualquier escritura que evite el service deja la capacidad desactualizada. Se mitiga haciendo que todas las escrituras pasen por el service y cubriéndolo con tests.

### 5. Una única función de validación reutilizable

**Decision:** Un validador de matriz en `services.py` que devuelve la distribución normalizada o levanta `ValueError` con un mensaje accionable.

**Rationale:** `funciones` va a necesitar exactamente la misma validación al copiar y al editar su copia. Duplicarla ahora garantiza que las dos versiones diverjan.

### 6. Unicidad de nombre validada en el service, en creación **y** actualización

**Decision:** Verificar `nombre` duplicado antes de guardar, en ambas operaciones, excluyendo la propia sala de la comparación.

**Rationale:** El modelo declara `unique=True` como red de seguridad, pero dejar que reviente en el `save()` produce un `IntegrityError` y un 500. `peliculas` ya validó esto solo en la creación y además olvidó excluir el propio registro; acá se corrige el patrón completo desde el principio.

### 7. Actualización parcial con reemplazo total de la distribución

**Decision:** Los campos escalares se aplican solo si vienen con valor; si viene `distribucion`, reemplaza la anterior entera.

**Rationale:** Fusionar matrices no tiene semántica razonable: una celda cambiada de `A` a `P` puede alterar dimensiones. Reemplazar es predecible y además es lo que una copia por función va a necesitar.

**Regla de filtrado:** se omiten `None` y `''`, y se aplica cualquier otro valor, incluido `False` o `0`. Repetir el chequeo por truthiness de la primera versión de `update_pelicula` rompería este campo igual que rompió `en_cartelera`.

**Nota:** la cuadrícula envía siempre la distribución completa, así que "opcional" aplica de verdad solo a nombre, tipo de sala y tipo de sonido.

### 8. Editor de distribución: cuadrícula con JavaScript y CSS

**Decision:** Un widget propio, sin framework y sin build: `static/salas/js/grid.js` y `static/salas/css/salas.css`, servidos con `{% load static %}`.

**Funcionamiento:**

- El servidor no dibuja el editor: entrega el estado inicial con `{{ distribucion|json_script:"distribucion-inicial" }}`, o nada en la creación.
- El JS construye una cuadrícula de 10 filas por 10 columnas con todas las celdas en Pasillo cuando no hay estado inicial, o con las dimensiones y tipos guardados cuando lo hay.
- Cada celda es un `<button type="button">` con `data-tipo`. El clic alterna `P` → `A` → `R` → `P` y actualiza su clase.
- Dos `<input type="number" min="1" max="100">` más un botón de aplicación redimensionan la cuadrícula en el cliente.
- Al enviar, el JS serializa el estado a un `<input type="hidden" name="distribucion">` con la forma `{"version": N, "filas": [...]}`.
- La vista de detalle reutiliza `salas.css` y las mismas clases de celda: el servidor emite la cuadrícula ya renderizada y no carga `grid.js`. Sin interacción no hay nada que el script aporte, y la cuadrícula se ve igual que en el editor.

**Redimensionado:** se conservan las celdas de la intersección, las nuevas nacen en Pasillo y las que quedan fuera del nuevo tamaño se descartan. Es el comportamiento menos sorpresivo y coincide con lo que el usuario espera al expandir una sala.

**Rationale:** Es el único camino para cumplir el requisito de cuadrícula clickeable con colores y tamaño variable. El `<textarea>` que proponía la versión anterior de este diseño quedó descartado porque era la salida forzada de la restricción "HTML puro", que este change levanta.

**Mapeo único carácter → clase:** el mapeo vive en dos lugares por la naturaleza de cada capa — un filtro de template `celda_clase` en Python y una constante en `grid.js` — y un test verifica que ambos devuelven las mismas tres clases para `P`, `A` y `R`. La duplicación queda reducida al cascarón del marcado.

### 9. Guards de funciones: condicionales y comentados

**Decision:** Tanto `update_sala` como `delete_sala` incluyen un bloque `TODO` comentado que consulta funciones activas cuando la app exista.

**Rationale:** La app `funciones` no existe, no hay modelo `Funcion` ni campo de estado. Un import a un módulo inexistente rompe el arranque, así que el bloque va comentado con el mismo patrón que `delete_pelicula`. Los requisitos de la spec están redactados en forma condicional para que se activen solos cuando la asociación exista.

**Consecuencia:** hoy no hay forma de verificar esos dos guards con tests contra datos reales. Se cubren con un test que verifica que la operación no falla cuando no hay funciones.

### 10. `tipo_sala` y `tipo_sonido` como texto libre

**Decision:** `CharField(max_length=45)` sin `choices`, con normalización de espacios.

**Rationale:** La DDL los define como VARCHAR libre y el usuario confirmó que solo requieren validación de tipo de dato. Inventar una lista de choices sería decidir el dominio por él.

**Consecuencia aceptada:** "3D", "3d" y "3 D" conviven y el sistema no lo impide. Cuando `funciones` defina precios diferenciados, un typo se convierte en un error de facturación.

### 11. `R` es "Reservado" y tiene dos motivos

**Decision:** `R` se nombra **Reservado** en la interfaz y el código, y significa siempre "butaca que no se ofrece a la venta". El motivo cambia según el nivel del dato.

| Nivel | Por qué está reservada | Origen |
|---|---|---|
| `Sala.distribucion` | Motivo permanente y físico: rota, sin visibilidad, ocupada por el proyector o bloqueada por normativa. | Se define al crear o editar la sala. |
| Copia en `Función` | Motivo temporal: la butaca ya no está disponible para esa función. | Heredada de la distribución, vendida a un cliente o bloqueada manualmente. |

**Rationale:** Una butaca rota lo está para todas las funciones; una butaca vendida lo está solo para una. Unificar ambos estados en el nivel de la sala obligaría a editar la sala cada vez que se vende una entrada.

**Consecuencia para `funciones`:** la copia nace con las `R` de la distribución y la operación de venta convierte `A` en `R` únicamente en esa copia. La sala nunca refleja una venta.

**Trade-off asumido:** por copy-on-create, marcar una butaca como rota en una sala no la invalida en las funciones ya creadas. `funciones` va a necesitar una operación de resincronización explícita. Se resuelve en esa capability, no en esta.

### 12. Validación en dos niveles: navegador primero, service siempre

**Decision:** Cada regla se implementa donde puede implementarse, y el service revalida todo lo que llega.

| Validación | Navegador | Service | Motivo |
|---|---|---|---|
| Nombre, tipo de sala y tipo de sonido obligatorios | `required` | Sí | Nativo; el service no confía en el cliente. |
| Largo máximo de 45 caracteres | `maxlength` | Sí | Nativo, pero un POST manipulado lo evade. |
| Ancho y alto entre 1 y 100 | `min` y `max` en `number` | Sí | Nativo, misma razón. |
| Nombre único | No puede | Sí | Requiere consultar la base. |
| Existencia del registro | No puede | Sí | Requiere consultar la base. |
| Al menos una butaca | No puede | Sí | El navegador no interpreta la matriz. |
| Rectangularidad y alfabeto | Estructural | Sí | La cuadrícula no genera filas desiguales; el service no asume que el cliente sea la cuadrícula. |
| Capacidad y versión | No puede | Sí | Son derivadas y el cliente nunca las dicta. |
| Funciones activas | No puede | Sí | Requiere consultar otra tabla. |

**Rationale:** El navegador da respuesta inmediata sin round-trip; el service es la única barrera que sobrevive a un `curl`. Implementar solo en el navegador deja la puerta abierta; implementar solo en el service degrada la experiencia con un viaje al servidor por cada error de tipeo.

### 13. Colores por tipo de celda

**Decision:** Pasillo gris, Asiento azul, Reservado dorado, aplicados con una clase CSS por tipo.

**Rationale:** Es la codificación que pidió el usuario. Se resuelve con clases (`celda--pasillo`, `celda--asiento`, `celda--reservado`) y no con estilos inline, para que el color viva en una sola hoja y el JS solo cambie la clase.

**Trade-off explícito:** el color es el único canal de información. Una persona con daltonismo no distingue azul de dorado. El usuario excluyó la accesibilidad cromática de esta implementación, así que no se agrega letra ni patrón redundante. Queda anotado para un change futuro.

## Risks / Trade-offs

**[La versión ya no identifica la forma del documento]** → Es un contador de revisiones. Si la forma del JSON cambia, hará falta un campo de esquema separado; el validador es el único punto que conoce la forma.

**[Los guards de funciones no son verificables todavía]** → Requisitos redactados en forma condicional y bloques `TODO` comentados; se activan cuando exista la app `funciones`.

**[La capacidad puede desincronizarse]** → Todas las escrituras pasan por el service y los tests cubren creación, actualización y reemplazo de distribución.

**[El formulario de creación nace inválido]** → La cuadrícula por defecto es 10×10 todo Pasillo, y una distribución sin butacas se rechaza. El usuario está obligado a pintar al menos una butaca antes del primer guardado. Es el resultado inevitable de la regla "al menos una butaca" combinada con el estado inicial pedido.

**[El color es el único canal]** → Decisión aceptada por el usuario; documentada en la decisión 13 para que no se lea como olvido.

**[Primera app con estáticos del proyecto]** → `salas` va a verse distinto de `peliculas`, que no tiene CSS. Se acepta la inconsistencia transitoria en lugar de reescribir templates ajenos a este change.

**[Payload de hasta 100×100]** → El tope acota el campo oculto a unos 10.000 caracteres más el JSON mínimo; irrelevante para un POST.

**[Sin autenticación, cualquiera puede borrar una sala]** → Fuera de alcance, igual que en `peliculas`. Se resuelve en el change de autenticación.

**[Actualización parcial no permite vaciar un campo]** → Misma limitación aceptada en `peliculas`; se revisa si aparece la necesidad.

**[Los cambios de la sala no alcanzan a las funciones existentes]** → Es el comportamiento elegido (copy-on-create). `funciones` necesita resincronización explícita; ver decisión 11.

## Contrato de datos

La forma del JSON es el contrato que `funciones` va a consumir y copiar. Se define una sola vez acá.

### Forma

```json
{
  "version": 1,
  "filas": [
    "PPAAAPAAAPP",
    "PPAAAPAAAPP",
    "PPARAPAAAPP",
    "PPAAAPAAAPP",
    "PPAAAPAARPP"
  ]
}
```

- `version`: entero mayor o igual a 1. Cuenta las revisiones de la distribución: arranca en 1 y sube uno por cada cambio real. Nunca lo dicta el cliente.
- `filas`: lista no vacía de strings de igual longitud. Máximo 100 filas y 100 columnas.

### Alfabeto

| Carácter | Nombre | Color | Cuenta en `capacidad` |
|---|---|---|---|
| `P` | Pasillo | Gris | No |
| `A` | Asiento | Azul | Sí |
| `R` | Reservado | Dorado | Sí |

### Ejemplo

Distribución de 5 filas por 11 columnas, con pasillo central en la columna 6 y márgenes laterales:

```
      1 2 3 4 5 6 7 8 9 10 11
1     P P A A A P A A A  P  P
2     P P A A A P A A A  P  P
3     P P A R A P A A A  P  P
4     P P A A A P A A A  P  P
5     P P A A A P A A R  P  P
```

Conteo: 28 `A` + 2 `R` = capacidad 30. Las 25 `P` no cuentan. 28 + 2 + 25 = 55 = 5 × 11.

### Fórmulas

- `capacidad = cantidad(A) + cantidad(R)`. Es aforo total: incluye las butacas reservadas.
- `disponibles = capacidad - cantidad(R)`. Se calcula sobre la copia de la función, nunca sobre la sala.
- `version` nueva = 1 si no había distribución; igual a la anterior si la distribución no cambió; la anterior más 1 si cambió.

## Migration Plan

1. `makemigrations salas` genera la migración inicial de `Sala`.
2. `migrate` crea la tabla `salas_sala` con la columna JSON.
3. Sin migración de datos: la tabla nace vacía.
4. Rollback: revertir la migración elimina la tabla. No hay datos previos que preservar porque es la primera versión de la capability.
