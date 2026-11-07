# chatbot Specification

## Purpose

Permite a los visitantes de MovieUp consultar dudas sobre el sitio desde un widget de chat flotante disponible en todas las páginas: un asistente responde con la información de un documento de conocimiento propio y con los datos actuales de la cartelera, manteniendo el hilo de la conversación.

## Requirements

### Requirement: Widget de chat flotante

El sistema SHALL mostrar en todas las páginas un icono flotante abajo a la izquierda con una imagen; al hacer clic SHALL desplegar un panel lateral izquierdo de aproximadamente un cuarto del ancho de la pantalla con la conversación, el campo de pregunta y el botón de envío. El panel SHALL permitir scroll interno y MUST NOT tapar el nav ni el footer.

#### Scenario: Icono en cualquier vista

- **WHEN** un visitante o una cuenta común navega por cualquier página de la web
- **THEN** el icono flotante aparece abajo a la izquierda de la pantalla

#### Scenario: Panel desplegado

- **WHEN** el usuario hace clic en el icono
- **THEN** se abre un panel lateral a la izquierda con los mensajes de la conversación, el campo de pregunta y el botón de envío, y el contenido del panel hace scroll dentro de él

#### Scenario: El shell sigue visible

- **WHEN** el panel está abierto en cualquier punto del scroll
- **THEN** el nav permanece visible arriba y el footer nunca queda cubierto por el panel

### Requirement: Icono visible solo para no administradores

El icono del chat SHALL ser visible únicamente para visitantes y cuentas comunes; las cuentas administradoras MUST NOT verlo en ninguna página.

#### Scenario: Visitante lo ve

- **WHEN** un visitante navega cualquier página
- **THEN** el icono del chat aparece

#### Scenario: Cuenta común lo ve

- **WHEN** una cuenta común autenticada navega cualquier página
- **THEN** el icono del chat aparece

#### Scenario: Administradora no lo ve

- **WHEN** una cuenta administradora navega cualquier página
- **THEN** la página no muestra el icono del chat

### Requirement: Mensaje inicial con las preguntas disponibles

Al abrirse un chat nuevo, el asistente SHALL mostrar un mensaje con la lista de las preguntas que puede responder, y hacer clic en una de ellas SHALL enviarla como pregunta.

#### Scenario: Chat nuevo con la lista de preguntas

- **WHEN** el usuario abre el panel de un chat sin mensajes
- **THEN** aparece un mensaje del asistente que lista las preguntas que puede responder

#### Scenario: Clic en una pregunta de la lista

- **WHEN** el usuario hace clic en una de las preguntas listadas
- **THEN** la pregunta se envía y comienza la conversación con la respuesta del asistente

### Requirement: Datos actuales de la cartelera

Para las preguntas sobre la cartelera —funciones de una película elegida, películas en cartelera y película más nueva— el asistente SHALL usar los datos actuales de la base de datos consultados en cada pregunta, y no el documento de conocimiento.

#### Scenario: Funciones de una película elegida

- **WHEN** el usuario pregunta por las funciones de una película
- **THEN** la respuesta lista las funciones actuales de esa película según la base de datos

#### Scenario: Películas en cartelera

- **WHEN** el usuario pregunta qué películas hay en cartelera
- **THEN** la respuesta refleja la cartelera actual de la base de datos

#### Scenario: Película más nueva

- **WHEN** el usuario pregunta cuál es la película más nueva
- **THEN** la respuesta se calcula con los datos actuales de la base de datos y no con información del documento

### Requirement: Respuesta basada en el documento de conocimiento

Para las preguntas de ayuda —pasos de compra, reembolso, uso de la entrada, datos de la cuenta y frecuencia de publicación— el asistente SHALL responder usando exclusivamente la información recuperada del documento de conocimiento, sin inventar datos que no estén en él.

#### Scenario: Preguntas de ayuda cubiertas

- **WHEN** el usuario pregunta cómo comprar, cómo reembolsar, cómo usar la entrada, qué datos se guardan al registrarse con Google o cada cuánto se publican películas
- **THEN** la respuesta sigue el contenido del documento de conocimiento

#### Scenario: Pregunta sin respaldo en el documento

- **WHEN** el documento no contiene información para responder la pregunta
- **THEN** el asistente declara que no dispone de esa información en lugar de inventarla

### Requirement: Contexto de conversación reciente

El chatbot SHALL considerar los mensajes recientes de la conversación para responder preguntas de seguimiento.

#### Scenario: Pregunta de seguimiento

- **WHEN** el usuario hace una pregunta que depende de un turno anterior de la misma conversación
- **THEN** la respuesta se genera incluyendo el historial reciente de la conversación

### Requirement: Ingesta del documento de conocimiento

El sistema SHALL disponer de una ingesta que convierte el documento Markdown —formato `#` título, `##` subtítulo, `###` subtemas y `---` al cerrar cada subtítulo— en una base vectorial Chroma persistente, lista para consultas.

#### Scenario: Ingesta exitosa

- **WHEN** se ejecuta la ingesta sobre el documento de conocimiento
- **THEN** la base vectorial queda creada y el chat puede responder con su contenido

#### Scenario: Ingesta sobre un documento nuevo

- **WHEN** se vuelve a ejecutar la ingesta después de editar el documento
- **THEN** la base vectorial refleja la versión más reciente del documento

### Requirement: Endpoint de consulta al chatbot

El sistema SHALL exponer `POST /chatbot/api/preguntar/` que recibe una pregunta y responde con JSON que incluye la respuesta generada por el asistente.

#### Scenario: Consulta válida

- **WHEN** llega una POST con una pregunta
- **THEN** la respuesta es JSON que contiene la respuesta del asistente

### Requirement: Contrato de errores del endpoint

El endpoint SHALL responder `400` cuando falta la pregunta y `503` cuando el servicio de consulta no está disponible (sin base vectorial o sin clave del modelo), siempre con un mensaje de error en JSON.

#### Scenario: Pregunta ausente

- **WHEN** llega una POST sin pregunta
- **THEN** el endpoint responde `400` con un mensaje de error

#### Scenario: Servicio de consulta no disponible

- **WHEN** falta la base vectorial o la clave del modelo
- **THEN** el endpoint responde `503` con un mensaje de error y no genera respuesta

### Requirement: Estados de carga y error en la interfaz

Mientras se genera una respuesta, la interfaz SHALL mostrar un indicador de carga; si el servidor responde con error, SHALL mostrar un mensaje visible en el chat y permitir volver a preguntar.

#### Scenario: Indicador de carga

- **WHEN** se envía una pregunta
- **THEN** se muestra un indicador de carga hasta que llegue la respuesta o falle la petición

#### Scenario: Error visible en el chat

- **WHEN** el endpoint responde con error
- **THEN** el chat muestra el mensaje de error y el usuario puede enviar otra pregunta
