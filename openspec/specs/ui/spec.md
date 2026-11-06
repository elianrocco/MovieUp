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

El subNAV SHALL incluir el botón `Estadísticas` aunque su vista no se define en este cambio.

#### Scenario: Botón presente

- **WHEN** se abre la vista de gestión
- **THEN** el botón `Estadísticas` aparece junto a los otros cuatro en el subNAV

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
