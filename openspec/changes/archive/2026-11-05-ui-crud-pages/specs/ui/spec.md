# Spec Delta

## ADDED Requirements

### Requirement: Presentación de detalle, formulario y borrado de las páginas CRUD
Las páginas de detalle, formulario y borrado de películas, funciones y salas SHALL renderizar dentro del shell de la web con su nav global, su footer y su paleta, y SHALL presentar su información en una tarjeta centrada de ancho acotado con el contenido alineado a la izquierda.

#### Scenario: Detalle con el shell del sitio
- **WHEN** el personal abre el detalle de una película, una función o una sala
- **THEN** ve el nav global, el footer, la paleta del sitio y la información del registro en una tarjeta centrada

#### Scenario: Formulario con controles del sitio
- **WHEN** el personal abre el formulario de alta o de edición
- **THEN** los campos, las etiquetas y el botón de envío usan los estilos del sitio y el mensaje de error del servicio se muestra dentro del formulario

#### Scenario: Confirmación centrada
- **WHEN** el personal abre la confirmación de borrado
- **THEN** el texto de confirmación aparece centrado junto a los botones de confirmar y cancelar

### Requirement: Acciones de las páginas CRUD como botones
Los enlaces de acción de los listados, detalles y formularios de películas, funciones y salas SHALL renderizarse como botones del sistema, con la acción destructiva en el color de marca y las acciones de navegación en superficie neutra, conservando su comportamiento de enlace.

#### Scenario: Acciones del detalle
- **WHEN** se renderiza el detalle de un registro
- **THEN** Editar, Eliminar y Volver al listado aparecen como botones y no como texto plano

#### Scenario: Acciones del listado
- **WHEN** se renderiza un listado en la gestión o como página completa
- **THEN** Ver, Editar y Eliminar de cada fila y Crear del encabezado aparecen como botones

### Requirement: Carga de operaciones de CRUD dentro de la gestión
En `/gestion/`, al hacer clic en Ver, Editar, Eliminar o Crear dentro de un listado, el cuerpo de la pestaña activa SHALL mostrar el contenido de esa vista sin cambiar la URL ni recargar la página, manteniendo esa pestaña como activa.

#### Scenario: Ver un registro desde la gestión
- **WHEN** la administradora hace clic en Ver de una fila
- **THEN** el cuerpo de la pestaña muestra el detalle del registro y la URL permanece en `/gestion/`

#### Scenario: Editar un registro desde la gestión
- **WHEN** la administradora hace clic en Editar de una fila
- **THEN** el cuerpo de la pestaña muestra el formulario de edición sin salir de la gestión

#### Scenario: Eliminar un registro desde la gestión
- **WHEN** la administradora hace clic en Eliminar de una fila
- **THEN** el cuerpo de la pestaña muestra la confirmación de borrado

#### Scenario: Crear un registro desde la gestión
- **WHEN** la administradora hace clic en Crear del listado
- **THEN** el cuerpo de la pestaña muestra el formulario de alta

#### Scenario: La pestaña activa no cambia
- **WHEN** la operación se realiza con la pestaña `Salas` activa
- **THEN** el subNAV sigue indicando `Salas` y la URL sigue en `/gestion/`

### Requirement: Vuelta al listado con datos frescos
Cada vista cargada dentro de la gestión SHALL ofrecer un control que regresa al listado de la pestaña activa, y ese listado SHALL reflejar el estado actual de los registros.

#### Scenario: Volver desde el detalle o la confirmación
- **WHEN** la administradora activa el control de vuelta desde un detalle o una confirmación
- **THEN** el cuerpo vuelve a mostrar el listado de la pestaña

#### Scenario: Volver cancelando un formulario
- **WHEN** la administradora cancela un formulario de alta o de edición
- **THEN** el cuerpo vuelve al listado sin modificar el registro

#### Scenario: Lista actualizada tras una operación
- **WHEN** la administradora crea, actualiza o elimina un registro dentro del panel
- **THEN** el listado muestra el registro nuevo, sus cambios o su ausencia

### Requirement: Errores del servicio dentro del panel
Cuando el servicio rechaza una operación realizada desde la gestión, el panel SHALL mostrar el mensaje de error dentro de la misma vista, sin cambiar la URL ni abandonar la gestión.

#### Scenario: Error de validación en el formulario
- **WHEN** el servicio rechaza un alta o una edición enviada desde el panel
- **THEN** el formulario se vuelve a mostrar en el panel con el mensaje de error y los datos enviados

#### Scenario: Error de bloqueo al eliminar
- **WHEN** el servicio rechaza el borrado de una función con entradas compradas
- **THEN** la confirmación se vuelve a mostrar en el panel con el motivo del rechazo y el registro permanece

### Requirement: Editor de distribución de salas dentro de la gestión
Al crear o editar una sala dentro del panel de gestión, el editor de distribución SHALL renderizar la cuadrícula con sus celdas y sus colores, SHALL cargar la distribución existente cuando la haya y SHALL conservar la distribución guardada cuando el usuario no la toca.

#### Scenario: Cuadrícula con sus colores de celda
- **WHEN** la administradora abre el formulario de alta o de edición de una sala dentro del panel
- **THEN** las celdas aparecen con sus colores de pasillo, asiento y reservado y se distinguen entre sí

#### Scenario: Ciclo de tipos al hacer clic
- **WHEN** la administradora hace clic en una celda
- **THEN** la celda cambia de tipo y refleja el color correspondiente a ese tipo

#### Scenario: Edición que no toca la cuadrícula
- **WHEN** la administradora abre el formulario de edición dentro del panel y guarda sin tocar la cuadrícula
- **THEN** la distribución guardada y la capacidad de la sala permanecen sin cambios

#### Scenario: Sin JavaScript
- **WHEN** el formulario de sala se envía sin JavaScript
- **THEN** el alta se rechaza con el mensaje de error del servicio y la edición conserva la distribución guardada

### Requirement: Degradación sin JavaScript
Cada acción de Ver, Editar, Eliminar y Crear SHALL conservar un enlace real hacia la ruta existente, y esas rutas SHALL seguir respondiendo como páginas completas con el shell del sitio.

#### Scenario: Detalle sin JavaScript
- **WHEN** el personal abre un detalle con el navegador sin JavaScript
- **THEN** la página completa se renderiza con el shell y la información del registro

#### Scenario: Envío de formulario sin JavaScript
- **WHEN** el personal envía un formulario sin JavaScript
- **THEN** el formulario se procesa en la ruta existente y responde con la página completa correspondiente

### Requirement: Sesión vencida durante una operación en el panel
Cuando la sesión terminó mientras el panel solicitaba contenido, el sistema SHALL llevar al usuario al inicio de sesión conservando el retorno en lugar de mostrar contenido de sesión cerrada dentro del panel.

#### Scenario: Sesión vencida al cargar una vista
- **WHEN** la administradora activa una operación y su sesión ya no es válida
- **THEN** es conducida al inicio de sesión con retorno a `/gestion/`

### Requirement: Estado de carga y foco del contenido del panel
Durante el intercambio de contenido el panel SHALL indicar que está cargando y, al recibir el contenido, SHALL mover el foco al primer encabezado de la vista mostrada.

#### Scenario: Indicador de carga
- **WHEN** la administradora activa una operación y el contenido aún no llegó
- **THEN** el panel muestra un estado de carga accesible

#### Scenario: Foco tras el intercambio
- **WHEN** el panel muestra una vista nueva
- **THEN** el foco pasa al primer encabezado de esa vista
