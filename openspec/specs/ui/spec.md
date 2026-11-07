# ui Specification

## Purpose

Define el shell visual de MovieUp: la navegación y el pie compartidos por todas las vistas, la página principal para visitantes y cuentas comunes y la vista de gestión central del personal, junto con las redirecciones por rol que gobiernan el acceso a cada una.

## Requirements

### Requirement: Nav global con estados de sesión

El sistema SHALL mostrar en todas las vistas un nav con el nombre "MovieUp" centrado y el logotipo pegado a su izquierda, y a la derecha los controles de sesión: enlace `Login` e icono circular para visitantes; foto de cuenta, nombre del usuario y enlace `Logout` para cuentas autenticadas. El logotipo SHALL ser una imagen con marcador de posición mientras el autor no cargue la definitiva.

#### Scenario: Visitante en cualquier vista

- **WHEN** un visitante abre cualquier vista de la web
- **THEN** ve el nav con `Login` e icono circular a la derecha, sin nombre de usuario

#### Scenario: Cuenta autenticada

- **WHEN** una cuenta autenticada navega a cualquier vista
- **THEN** el icono circular muestra su foto, debajo aparece su nombre y el enlace `Login` se muestra como `Logout`

#### Scenario: Botón de entradas para cuentas comunes

- **WHEN** una cuenta común (no administradora) está autenticada
- **THEN** un botón en forma de ticket dorado aparece a la izquierda de `Logout`

#### Scenario: El administrador no ve el botón de entradas

- **WHEN** una cuenta administradora está autenticada
- **THEN** el nav no muestra el botón de ticket

#### Scenario: Acceso al listado de entradas

- **WHEN** una cuenta común hace clic en el botón de ticket
- **THEN** es llevada al listado de sus entradas

### Requirement: Foto de cuenta cargada por el sistema

El sistema SHALL cargar la foto de la cuenta desde el proveedor de inicio de sesión al iniciar sesión y mostrarla en el icono circular del nav. La interfaz MUST NO ofrecer al usuario cargar ni modificar esa imagen.

#### Scenario: Foto desde el proveedor

- **WHEN** un usuario inicia sesión con Google
- **THEN** la foto de su perfil aparece en el icono circular del nav

#### Scenario: Cuenta sin foto disponible

- **WHEN** la sesión inicia y el proveedor no entrega una imagen
- **THEN** el icono circular muestra un marcador de posición sin romper la estructura del nav

### Requirement: Footer global

El sistema SHALL mostrar el mismo pie de página en todas las vistas, con el nombre del autor "Elian" y, debajo, la aclaración de que es un proyecto educativo sin fines de lucro cuyo módulo de pago existe con propósito de aprendizaje y no de negocio.

#### Scenario: Pie en cualquier vista

- **WHEN** se abre cualquier vista de la web
- **THEN** el pie muestra el nombre del autor y debajo la aclaración de proyecto educativo sin fines de lucro

### Requirement: Hero de la página principal

La página principal SHALL mostrar un rectángulo horizontal centrado de poco más de la mitad del alto y tres cuartos del ancho de la pantalla, con la portada de la película en cartelera de fecha de estreno más reciente; en su sector inferior izquierdo SHALL estar el título, la descripción, el género, la clasificación y los botones `Trailer` y `Comprar entradas`.

#### Scenario: Películas en cartelera

- **WHEN** existe al menos una película con `en_cartelera` activo
- **THEN** el hero muestra la de mayor fecha de estreno entre ellas, con todo el contenido dentro del rectángulo y ubicado en el sector inferior izquierdo

#### Scenario: La más reciente no está en cartelera

- **WHEN** la película de mayor fecha de estreno tiene `en_cartelera` inactivo
- **THEN** el hero muestra la película en cartelera de mayor fecha de estreno

#### Scenario: Sin películas en cartelera

- **WHEN** no hay ninguna película con `en_cartelera` activo
- **THEN** la página principal muestra un estado vacío en lugar del hero

### Requirement: Grid de películas en cartelera

Debajo del hero y con un margen, la página principal SHALL listar todas las películas con `en_cartelera` activo (incluida la del hero) en filas de hasta 3 tarjetas verticales de la mitad del alto y un cuarto del ancho del rectángulo del hero; cada tarjeta SHALL mostrar dentro la portada con título, género y clasificación, sin descripción, y mostrar los botones `Trailer` y `Comprar entradas` fuera de la tarjeta, justo debajo.

#### Scenario: Reparto en filas de hasta tres

- **WHEN** hay más de tres películas en cartelera
- **THEN** las filas siguientes a la primera contienen tres tarjetas una al lado de la otra y la primera admite de una a tres

#### Scenario: Botones fuera de la tarjeta

- **WHEN** se renderiza una tarjeta del grid
- **THEN** sus botones `Trailer` y `Comprar entradas` aparecen debajo del rectángulo, fuera de él

#### Scenario: Película fuera de cartelera excluida

- **WHEN** una película tiene `en_cartelera` inactivo
- **THEN** no aparece en el grid

### Requirement: Botón Trailer

La página principal SHALL ofrecer el botón `Trailer` en el hero y en cada tarjeta del grid, y al hacer clic SHALL conducir al usuario a la URL del tráiler de esa película.

#### Scenario: Trailer desde el hero

- **WHEN** el usuario hace clic en `Trailer` dentro del hero
- **THEN** se abre la URL del tráiler de esa película

#### Scenario: Trailer desde una tarjeta

- **WHEN** el usuario hace clic en `Trailer` debajo de una tarjeta
- **THEN** se abre la URL del tráiler de esa película

### Requirement: Control de rol sobre la página principal

La página principal SHALL estar disponible para visitantes y cuentas comunes; una cuenta administradora que la solicite SHALL ser redirigida a la vista de gestión.

#### Scenario: Visitante o común en la portada

- **WHEN** un visitante o una cuenta común abre la página principal
- **THEN** la página se muestra normalmente

#### Scenario: Administrador en la portada

- **WHEN** una cuenta administradora abre la página principal
- **THEN** es redirigida a la vista de gestión

### Requirement: Estructura de la vista de gestión

El sistema SHALL ofrecer una vista de gestión, visible en toda su duración con el nav global y el footer, que incluya un subNAV pegado debajo del nav con 5 botones repartidos de manera pareja: `Películas` seleccionado por defecto, `Funciones`, `Salas`, `Cuentas` y `Estadísticas`.

#### Scenario: Apertura de la gestión

- **WHEN** una cuenta administradora abre la vista de gestión
- **THEN** ve el nav, el footer y el subNAV con `Películas` seleccionado por defecto y el listado de películas en el cuerpo

#### Scenario: SubNAV permanente

- **WHEN** la administradora cambia de pestaña
- **THEN** el subNAV sigue visible con los cinco botones

### Requirement: Cambio de contenido en el mismo lugar

Al hacer clic en `Películas`, `Funciones` o `Salas`, el cuerpo de la vista de gestión SHALL mostrar el contenido del listado correspondiente sin cambiar la URL ni recargar la página.

#### Scenario: Listado de funciones

- **WHEN** la administradora hace clic en `Funciones`
- **THEN** el cuerpo muestra el listado de funciones y la URL no cambia

#### Scenario: Listado de salas

- **WHEN** la administradora hace clic en `Salas`
- **THEN** el cuerpo muestra el listado de salas y la URL no cambia

#### Scenario: Vuelta a películas

- **WHEN** la administradora hace clic en `Películas` después de otra pestaña
- **THEN** el cuerpo vuelve a mostrar el listado de películas

### Requirement: Cuentas dentro del shell

El botón `Cuentas` SHALL mostrar en el cuerpo el panel de cuentas de Django integrado con el shell de la web: nav global, subNAV, footer y paleta de colores del sitio.

#### Scenario: Panel de cuentas integrado

- **WHEN** la administradora hace clic en `Cuentas`
- **THEN** el panel de cuentas de Django aparece en el cuerpo con el nav, el subNAV, el footer y la paleta de la web

### Requirement: Botón Estadísticas presente

El subNAV SHALL incluir el botón `Estadísticas` habilitado; al precionarlo SHALL cargar el apartado de estadísticas en el cuerpo de la vista de gestión sin cambiar la URL, con el mismo mecanismo de paneles que los CRUDs de la sección.

#### Scenario: Botón presente

- **WHEN** se abre la vista de gestión
- **THEN** el botón `Estadísticas` aparece junto a los otros cuatro en el subNAV, habilitado

#### Scenario: Carga sin cambio de URL

- **WHEN** se hace clic en `Estadísticas`
- **THEN** el apartado de estadísticas se muestra en el cuerpo de la vista de gestión y la URL permanece en `/gestion/`

### Requirement: Acceso restringido a la vista de gestión

La vista de gestión SHALL estar limitada al personal autorizado: una cuenta común SHALL ser redirigida a la página principal y un visitante SHALL ser redirigido al inicio de sesión.

#### Scenario: Visitante en la gestión

- **WHEN** un visitante solicita la vista de gestión
- **THEN** es redirigido a la pantalla de inicio de sesión

#### Scenario: Cuenta común en la gestión

- **WHEN** una cuenta común solicita la vista de gestión
- **THEN** es redirigida a la página principal

### Requirement: Acceso a la compra desde la portada y el nav

El botón `Comprar entradas` (del hero o de cualquier tarjeta) SHALL conducir a `/compras/<pelicula_id>/` cuando hay sesión iniciada. Sin sesión SHALL conducir al login con Google conservando como destino de retorno esa página de compra, sin renderizar la pantalla intermedia de acceso. El `Login` del nav MUST NOT heredar ese retorno: sigue volviendo a `/`.

#### Scenario: Compra con sesión

- **WHEN** una cuenta autenticada hace clic en `Comprar entradas` desde el hero o desde una tarjeta
- **THEN** es conducida a la página de compra de esa película

#### Scenario: Compra sin sesión

- **WHEN** un visitante hace clic en `Comprar entradas` desde el hero o desde una tarjeta
- **THEN** es conducido directamente al flujo de inicio de sesión con Google con retorno a la página de compra de esa película, sin que se muestre la pantalla intermedia de acceso

#### Scenario: Login normal del nav

- **WHEN** un visitante hace clic en `Login` en el nav
- **THEN** es conducido al flujo de inicio de sesión con Google con retorno a la página principal

#### Scenario: Cada tarjeta conserva su película

- **WHEN** el usuario hace clic en `Comprar entradas` de una tarjeta del grid
- **THEN** la página de compra corresponde a la película de esa tarjeta y no a la del hero

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

### Requirement: Botón de validación en el nav

El sistema SHALL mostrar en el nav de todas las vistas, al extremo izquierda, un botón dorado con enlace a la vista de validación de entradas, visible únicamente para cuentas administradoras.

#### Scenario: Administradora en cualquier vista

- **WHEN** una cuenta administradora navega a cualquier vista
- **THEN** el botón dorado aparece al extremo izquierdo del nav

#### Scenario: Cuenta común no lo ve

- **WHEN** una cuenta común autenticada navega a cualquier vista
- **THEN** el nav no muestra el botón de validación

#### Scenario: Visitante no lo ve

- **WHEN** un visitante navega a cualquier vista
- **THEN** el nav no muestra el botón de validación

#### Scenario: Clic en el botón

- **WHEN** la administradora hace clic en el botón de validación
- **THEN** es conducida a la vista de validación de entradas
