# entradas Specification

## Purpose

Representa la entrada comprada por una cuenta para un asiento concreto de una función: su creación interna sin interfaz, su consulta por la cuenta dueña, su validación en puerta mediante un código y su eliminación únicamente automática por reembolso o por finalización de la función.

## Requirements

### Requirement: Creación interna sin interfaz

El sistema SHALL crear entradas únicamente mediante un servicio interno que invoca el proceso de compra, recibiendo la función, la cuenta de la sesión actual, el número de asiento y la etiqueta de fila. El sistema MUST NOT exponer vista, ruta ni formulario de alta de entradas.

#### Scenario: No hay formulario ni ruta de alta

- **WHEN** se solicita la ruta de creación de una entrada
- **THEN** el sistema responde 404 y no existe ningún formulario de alta

#### Scenario: La compra invoca al servicio

- **WHEN** el proceso de compra llama al servicio de creación con una función, la cuenta de la sesión, un número de asiento y una etiqueta de fila válidos
- **THEN** el sistema persiste la entrada con `activa` en `True` y devuelve la entrada creada

### Requirement: Datos persistidos de la entrada

El sistema SHALL persistir por entrada solamente la función, la cuenta, el código, la etiqueta de fila, el número de asiento y el indicador de actividad, con `activa` naciendo en `True`. El sistema MUST NOT guardar precio, fecha ni cualquier otro dato derivado.

#### Scenario: Entrada con los datos mínimos

- **WHEN** se crea una entrada válida
- **THEN** persiste con función, cuenta, código, fila, asiento y `activa` en `True`, sin precio ni fechas

### Requirement: Código de validación único y complejo

El sistema SHALL generar al crear cada entrada un código complejo que no derive del identificador de la entrada, de la función ni de la cuenta, y MUST NOT admitir dos entradas con el mismo código.

#### Scenario: Códigos distintos entre entradas

- **WHEN** se crean varias entradas
- **THEN** cada entrada recibe un código distinto

#### Scenario: Colisión de código

- **WHEN** una creación produciría un código que ya existe
- **THEN** la creación se rechaza y no persiste ninguna entrada

### Requirement: Etiqueta alfabética de la fila

El sistema SHALL identificar cada fila de la distribución por una etiqueta alfabética derivada de su posición: la primera fila es `A`, la segunda es `B`, y tras la `Z` continúa con doble letra (`AA`). El servicio de creación SHALL localizar la celda a modificar con esa convención.

#### Scenario: Primera y segunda fila

- **WHEN** se crea una entrada para las filas 1 y 2
- **THEN** las etiquetas resultantes son `A` y `B`

#### Scenario: Fila más allá de la letra única

- **WHEN** se crea una entrada para la fila 27
- **THEN** la etiqueta resultante es `AA`

#### Scenario: Etiqueta sin fila correspondiente

- **WHEN** la etiqueta recibida no corresponde a ninguna fila de la distribución
- **THEN** la creación se rechaza con un mensaje apto para el usuario y no se persiste nada

### Requirement: Asiento disponible al crear

El sistema SHALL interpretar `n_asiento` como el ordinal 1-based entre las celdas `A` y `R` de la fila, sin contar las celdas `P`; una celda `R` conserva su ordinal aunque ya esté reservada. MUST NOT crear una entrada si ese ordinal no existe o no corresponde a una celda `A`; se rechazan asientos fuera de rango, filas inexistentes y posiciones no disponibles sin modificar ningún dato.

#### Scenario: Celda reservada

- **WHEN** se intenta crear una entrada para una celda cuya letra es `R`
- **THEN** el sistema informa que el asiento ya está reservado y la función queda intacta

#### Scenario: Celda de pasillo

- **WHEN** se intenta crear una entrada para una celda cuya letra es `P`
- **THEN** el sistema informa que la posición no es un asiento y no persiste la entrada

#### Scenario: Pasillo no incrementa el número de asiento

- **WHEN** se crea una entrada para el segundo asiento en una fila `A P A`
- **THEN** `n_asiento=2` identifica la tercera celda y el pasillo no cuenta como asiento

#### Scenario: Asiento reservado conserva su ordinal

- **WHEN** se crea una entrada para el segundo asiento de una fila `R A`
- **THEN** `n_asiento=2` identifica la segunda celda porque la celda `R` sigue contando como asiento

#### Scenario: Número de asiento fuera de rango

- **WHEN** el número de asiento supera la cantidad de celdas `A` y `R` de la fila
- **THEN** el sistema rechaza la creación con un mensaje apto para el usuario

### Requirement: Asiento único por función

El sistema MUST NO registrar dos entradas para la misma función, etiqueta de fila y número de asiento, aun cuando dos creaciones se ejecuten en simultáneo.

#### Scenario: Dos compras simultáneas del mismo asiento

- **WHEN** dos creaciones para el mismo asiento se ejecutan en paralelo
- **THEN** solo una entrada persiste y la otra se rechaza

### Requirement: Actualización de la función al crear

Al crear una entrada, el sistema SHALL incrementar en uno las entradas compradas de la función, decrementar en uno su disponibilidad y cambiar la celda del asiento de `A` a `R` en su distribución, todo en la misma operación atómica.

#### Scenario: Creación exitosa actualiza la función

- **WHEN** la creación de la entrada termina correctamente
- **THEN** las entradas compradas suben en uno, la disponibilidad baja en uno y la celda queda en `R`

#### Scenario: Creación rechazada deja la función intacta

- **WHEN** la creación se rechaza por cualquier validación
- **THEN** entradas compradas, disponibilidad y distribución conservan sus valores previos

### Requirement: Alta condicionada a una función existente y vigente

El sistema MUST NOT crear entradas para una función inexistente ni para una cuya fecha y hora de finalización ya pasó, y SHALL informar el motivo en ambos casos sin persistir nada.

#### Scenario: Función inexistente

- **WHEN** se invoca la creación con un identificador de función que no existe
- **THEN** el sistema informa que la función no existe y no persiste la entrada

#### Scenario: Función finalizada

- **WHEN** se invoca la creación para una función cuya hora de finalización ya transcurrió
- **THEN** el sistema rechaza la creación e informa el motivo

### Requirement: Listado propio de entradas

El sistema SHALL ofrecer un listado que muestre únicamente las entradas de la cuenta de la sesión actual, con datos resumidos de la función y de la sala. El sistema MUST NO mostrar entradas de otras cuentas.

#### Scenario: Cuenta con entradas

- **WHEN** una cuenta con entradas abre el listado
- **THEN** ve sus propias entradas con el título de la película, la sala, el inicio, la fila, el asiento y el estado

#### Scenario: Cuenta sin entradas

- **WHEN** una cuenta sin entradas abre el listado
- **THEN** ve el listado vacío y ninguna entrada ajena

### Requirement: Detalle de la entrada con control de propiedad

El sistema SHALL mostrar el detalle de una entrada solo a la cuenta que la posee. Si la entrada no existe o pertenece a otra cuenta, el sistema SHALL responder 404 sin revelar que la entrada exista.

#### Scenario: Detalle de la propia entrada

- **WHEN** la cuenta dueña solicita el detalle de su entrada
- **THEN** el sistema muestra el detalle completo

#### Scenario: Detalle de una entrada ajena

- **WHEN** una cuenta solicita el detalle de una entrada de otra cuenta
- **THEN** el sistema responde 404

#### Scenario: Detalle de una entrada inexistente

- **WHEN** se solicita el detalle con un identificador que no corresponde a ninguna entrada
- **THEN** el sistema responde 404

### Requirement: Contenido del detalle

El sistema SHALL mostrar en el detalle el código, la fila, el asiento, el estado de actividad, el título y el inicio de la función, y el nombre, el tipo de sala, el tipo de sonido y la capacidad de la sala. El sistema MUST NO mostrar identificadores, distribuciones de salas o de funciones, ni datos técnicos de administración.

#### Scenario: Detalle con datos de cartelera y de sala

- **WHEN** se abre el detalle de una entrada
- **THEN** aparecen el código, la fila, el asiento, el estado, el título de la película, el inicio, y el nombre, tipo de sala, tipo de sonido y capacidad de la sala

#### Scenario: Sin datos técnicos

- **WHEN** se inspecciona el HTML del detalle
- **THEN** no aparecen identificadores, distribuciones ni campos de administración

### Requirement: Validación en puerta por código

El sistema SHALL ofrecer una vista de validación que, recibido un código, lo busque entre las entradas activas, informe si existe o no y, cuando exista, pase `activa` a `False` exactamente una vez. El acceso a la vista SHALL estar limitado al personal autorizado.

#### Scenario: Código de una entrada activa

- **WHEN** se envía el código de una entrada activa
- **THEN** el sistema informa que la entrada existe, muestra sus datos y la entrada queda en `activa=False`

#### Scenario: Código ya validado

- **WHEN** se vuelve a enviar el mismo código después de validar
- **THEN** el sistema informa que no se encontró ninguna entrada activa

#### Scenario: Código inexistente

- **WHEN** se envía un código que no corresponde a ninguna entrada activa
- **THEN** el sistema informa que el código no corresponde a ninguna entrada

#### Scenario: Acceso sin autorización

- **WHEN** una cuenta sin personal autorizado solicita la vista de validación
- **THEN** el sistema deniega el acceso

### Requirement: Eliminación solo automática

El sistema MUST NO permitir el borrado manual de entradas: no existirá vista ni acción de administración para eliminarlas. El servicio de eliminación SHALL aceptar únicamente los motivos de reembolso y de finalización de la función.

#### Scenario: Motivo de eliminación no permitido

- **WHEN** se invoca la eliminación con un motivo distinto de reembolso o finalización
- **THEN** el sistema rechaza la operación y la entrada permanece

#### Scenario: Sin vista de borrado

- **WHEN** se solicita la ruta de confirmación de borrado de una entrada
- **THEN** el sistema responde 404

#### Scenario: Entrada inexistente

- **WHEN** se invoca la eliminación con un identificador que no corresponde a ninguna entrada
- **THEN** el sistema responde 404

### Requirement: Reembolso revierte la función sin devolver dinero

Al reembolsar una entrada, el sistema SHALL eliminarla y revertir la función en la misma operación atómica: restar uno a las entradas compradas, sumar uno a la disponibilidad y devolver la celda de `R` a `A`. Esta capacidad MUST NO calcular ni entregar dinero.

#### Scenario: Reembolso correcto

- **WHEN** se reembolsa una entrada activa
- **THEN** la entrada desaparece, la función recupera su disponibilidad y la celda vuelve a `A`

#### Scenario: Reembolso rechazado

- **WHEN** el reembolso falla por cualquier validación
- **THEN** la entrada permanece y la función no cambia

### Requirement: Reembolso restringido a entradas activas

El sistema MUST NO reembolsar una entrada que ya fue validada en puerta. SHALL informar el motivo y conservar la entrada.

#### Scenario: Reembolso de una entrada validada

- **WHEN** se intenta reembolsar una entrada con `activa` en `False`
- **THEN** el sistema rechaza el reembolso, informa el motivo y la entrada permanece

### Requirement: Reembolso con anticipación mínima de 24 horas

El sistema MUST NO reembolsar una entrada cuando la función asociada comienza en menos de 24 horas o ya comenzó, informando el motivo y conservando la entrada. Esta restricción SHALL aplicar únicamente al motivo de reembolso.

#### Scenario: Reembolso con más de 24 horas de anticipación

- **WHEN** se pide un reembolso cuando faltan más de 24 horas para el inicio de la función
- **THEN** el sistema acepta el reembolso

#### Scenario: Reembolso a menos de 24 horas del inicio

- **WHEN** se pide un reembolso cuando faltan menos de 24 horas para el inicio de la función
- **THEN** el sistema rechaza el reembolso, informa el motivo y la entrada permanece

#### Scenario: Función ya iniciada

- **WHEN** se pide un reembolso una vez transcurrido el inicio de la función
- **THEN** el sistema rechaza el reembolso, informa el motivo y la entrada permanece

#### Scenario: Límite exacto de 24 horas

- **WHEN** el inicio de la función ocurre exactamente 24 horas después del momento en que se pide el reembolso
- **THEN** el sistema acepta el reembolso

#### Scenario: La eliminación por finalización no queda restringida

- **WHEN** se elimina una entrada porque la función ya finalizó
- **THEN** el sistema la elimina sin aplicar el límite de anticipación

### Requirement: Finalización no altera la función

Cuando una entrada se elimina por haber llegado la hora de finalización de la función, el sistema SHALL borrarla sin modificar las entradas compradas, la disponibilidad ni la distribución de la función.

#### Scenario: Eliminación por finalización

- **WHEN** se elimina una entrada porque la función ya finalizó
- **THEN** la entrada desaparece y los datos de la función permanecen sin cambios

### Requirement: Limpieza masiva por finalización

Además de la eliminación individual, el sistema SHALL eliminar en una sola operación todas las entradas de una función cuyo fin ya pasó, con el mismo efecto que la eliminación por finalización. La operación MUST ser idempotente, MUST NO aceptar motivos distintos de la finalización y MUST NOT modificar las entradas compradas, la disponibilidad ni la distribución de la función.

#### Scenario: Función vencida con entradas

- **WHEN** se ejecuta la limpieza masiva sobre una función cuyo fin ya pasó y que tiene entradas asociadas
- **THEN** todas las entradas de esa función se eliminan

#### Scenario: Función vencida sin entradas

- **WHEN** se ejecuta la limpieza masiva sobre una función cuyo fin ya pasó y que no tiene entradas
- **THEN** la operación termina sin errores

#### Scenario: Limpieza idempotente

- **WHEN** se repite la limpieza masiva sobre la misma función
- **THEN** la operación no borra nada nuevo y no produce errores

#### Scenario: Otra función intacta

- **WHEN** se ejecuta la limpieza masiva sobre una función vencida
- **THEN** las entradas de las demás funciones permanecen

#### Scenario: Contadores de la función intactos

- **WHEN** la limpieza masiva elimina las entradas de una función vencida
- **THEN** las entradas compradas, la disponibilidad y la distribución de esa función conservan sus valores previos

### Requirement: Presentación del listado de entradas

El listado SHALL mostrar cada entrada dentro de un rectángulo de bordes redondeados con el dorado del nav, con todos los registros centrados, y SHALL renderizar el enlace de cada registro como un botón con ese mismo dorado y un contorno rojo.

#### Scenario: Registro en rectángulo dorado

- **WHEN** una cuenta con entradas abre el listado
- **THEN** cada entrada aparece dentro de un rectángulo de bordes redondeados con el dorado del nav y los registros aparecen centrados

#### Scenario: Enlace de detalle como botón

- **WHEN** se renderiza el listado
- **THEN** el enlace al detalle de cada registro se muestra como un botón dorado con contorno rojo y conduce al detalle de esa entrada

### Requirement: Encabezado del listado en panel dorado

El listado SHALL mostrar el encabezado `Mis entradas` centrado dentro de un panel dorado del mismo ancho horizontal que las tarjetas de entrada y con un alto vertical delgado que apenas encapsule el texto más un margen pequeño.

#### Scenario: Encabezado en panel dorado

- **WHEN** una cuenta con entradas abre `/entradas/`
- **THEN** el encabezado `Mis entradas` aparece centrado dentro de un panel dorado

#### Scenario: Mismo ancho que las tarjetas y alto delgado

- **WHEN** se renderiza el listado con una o más entradas
- **THEN** el panel del encabezado tiene el mismo ancho horizontal que las tarjetas de entrada y su alto apenas encapsula el texto con un pequeño margen

### Requirement: Orden de los datos en cada tarjeta del listado

Cada tarjeta SHALL centrar todo su contenido, incluido `Ver entrada`. SHALL mostrar el título sin etiqueta, luego Estado e Inicio juntos con etiquetas sobre sus valores y, debajo, Sala/Fila/Asiento juntos con etiquetas sobre sus valores. Ambas filas SHALL mantener todos sus elementos dentro del tercio central.

#### Scenario: Orden y alineación centrada de las filas

- **WHEN** se renderiza una entrada en el listado
- **THEN** el título de la película aparece arriba sin etiqueta; debajo, estado e inicio comparten una fila con cada etiqueta encima del valor; y en la última fila sala, fila y asiento comparten una fila con cada etiqueta encima del valor, con todo el contenido de la tarjeta y el botón `Ver entrada` centrados

#### Scenario: Espaciado máximo dentro del tercio central

- **WHEN** se renderiza una tarjeta en un viewport de escritorio
- **THEN** Estado/Inicio y Sala/Fila/Asiento usan el mismo margen horizontal máximo que mantiene todos sus elementos dentro del tercio central de la tarjeta, sin tocar el primer ni el tercer tercio

#### Scenario: Ancho insuficiente para el espaciado máximo

- **WHEN** el ancho del viewport o el contenido de una entrada impide mantener todos los elementos en una fila dentro del tercio central
- **THEN** los elementos se reacomodan dentro de ese tercio y no invaden las zonas laterales de la tarjeta

### Requirement: Textos de estado de la entrada

El sistema SHALL mostrar el estado de una entrada como `Sin usar` cuando está activa y como `Usada` cuando ya fue validada, en el listado y en el detalle, y MUST NO mostrar `Pendiente de validación` ni `Validada` en esas vistas.

#### Scenario: Entrada sin usar

- **WHEN** se muestra una entrada activa en el listado o en el detalle
- **THEN** el estado aparece como `Sin usar`

#### Scenario: Entrada usada

- **WHEN** se muestra una entrada ya validada en el listado o en el detalle
- **THEN** el estado aparece como `Usada`

#### Scenario: Textos antiguos ausentes

- **WHEN** se inspeccionan el listado y el detalle de entradas
- **THEN** no aparecen los textos `Pendiente de validación` ni `Validada`

### Requirement: Presentación del detalle de entrada

El detalle SHALL presentarse dentro de un rectángulo de bordes redondeados con el dorado del nav, con el título de la película fuera de los paneles y cada otro dato en un panel blanco que llene el ancho de su columna sin exceder el margen interior dorado. Sus etiquetas SHALL quedar centradas fuera del panel sobre el valor centrado. El enlace `Volver a mis entradas` SHALL ser un botón dorado con contorno rojo, junto a un botón `Reembolso` de igual alto.

#### Scenario: Detalle dentro del rectángulo dorado

- **WHEN** se abre el detalle de una entrada
- **THEN** el título de la película aparece fuera de los paneles y cada dato aparece en su propio panel blanco que llena el ancho disponible de la columna sin sobrepasar el margen interior dorado, con su etiqueta centrada fuera del panel y arriba del valor centrado

#### Scenario: Fila de sala, fila y asiento

- **WHEN** se renderiza el detalle
- **THEN** sala, fila y asiento aparecen en una misma fila en ese orden con un margen mediano entre ellos

#### Scenario: Fila de tipo de sala, tipo de sonido y capacidad

- **WHEN** se renderiza el detalle
- **THEN** tipo de sala, tipo de sonido y capacidad de la sala aparecen en una misma fila en ese orden con un margen mediano entre ellos

#### Scenario: Los dos botones del detalle

- **WHEN** se renderiza el detalle de una entrada
- **THEN** aparecen el botón `Volver a mis entradas` con el dorado del nav y un contorno rojo y, al lado, el botón `Reembolso` con el mismo alto que el primero

### Requirement: Reembolso desde el detalle de la entrada

El sistema SHALL ofrecer el reembolso mediante `POST /entradas/<entrada_id>/reembolso/`, invocable desde el detalle de la propia entrada y aplicando las restricciones de reembolso ya definidas. En éxito SHALL eliminar la entrada, revertir la función y volver al listado; en cualquier rechazo SHALL mostrar el motivo en el detalle sin modificar ningún dato. La ruta MUST responder 405 a métodos distintos del `POST`.

#### Scenario: Reembolso exitoso

- **WHEN** la cuenta dueña envía el reembolso de una entrada activa con más de 24 horas de anticipación
- **THEN** la entrada se elimina, la función se revierte y el navegador vuelve al listado de entradas

#### Scenario: Rechazo visible en el detalle

- **WHEN** el reembolso se rechaza porque la entrada ya fue validada o porque el inicio está a menos de 24 horas
- **THEN** el detalle muestra el motivo del rechazo, la entrada permanece y su función queda intacta

#### Scenario: Entrada ajena o inexistente

- **WHEN** una cuenta envía un reembolso para una entrada que no posee o que no existe
- **THEN** el sistema responde 404 sin eliminar ninguna entrada

#### Scenario: La ruta no reembolsa por GET

- **WHEN** se solicita la ruta de reembolso con el método GET
- **THEN** el sistema responde 405 y ninguna entrada se elimina

### Requirement: Presentación de la vista de validación

La vista de validación SHALL mostrar su encabezado, su formulario y el resultado dentro de un panel blanco centrado horizontalmente en la página, y el botón de envío `Validar` SHALL ser de color dorado.

#### Scenario: Contenido en panel blanco centrado

- **WHEN** se abre la vista de validación
- **THEN** el encabezado y el formulario aparecen dentro de un panel blanco centrado en la página

#### Scenario: Botón Validar dorado

- **WHEN** se muestra el formulario de validación
- **THEN** el botón `Validar` tiene el color dorado de la paleta

#### Scenario: Resultado dentro del panel

- **WHEN** se envía un código y la vista muestra el resultado
- **THEN** el mensaje y los datos de la entrada aparecen dentro del mismo panel

### Requirement: Datos de entrada validados en filas etiquetadas

Tras una validación exitosa, la vista SHALL mostrar cada dato de la entrada como un par etiqueta/valor en una fila, con la etiqueta a la izquierda del valor y seguida de dos puntos, y SHALL dejar una separación vertical uniforme entre filas.

#### Scenario: Etiquetas a la izquierda de cada valor

- **WHEN** se muestran los datos de una entrada validada
- **THEN** cada etiqueta aparece a la izquierda de su valor y termina con dos puntos

#### Scenario: Separación entre los datos

- **WHEN** se muestran varias filas de datos de una entrada validada
- **THEN** hay una separación visual pequeña y uniforme entre las filas
