# estadisticas Specification

## Purpose

Permite al personal consultar métricas de ventas dentro de la vista de gestión: recaudación por género en un gráfico de barras, listado de películas ordenado por recaudación con su película líder destacada y selector de periodo semanal, mensual y anual, sin salir de `/gestion/`.

## Requirements

### Requirement: Apartado de estadísticas en la vista de gestión

El sistema SHALL habilitar el botón `Estadísticas` del subNAV de `/gestion/` para que, al precionarlo, cargue el apartado de estadísticas en el cuerpo de la página sin cambiar la URL, con el mismo mecanismo de paneles que los CRUDs de la sección.

#### Scenario: Botón habilitado que carga el apartado sin cambiar la URL

- **WHEN** el personal hace clic en `Estadísticas` dentro de `/gestion/`
- **THEN** el apartado de estadísticas aparece en el cuerpo de la página y la URL permanece en `/gestion/`

#### Scenario: Cambio de vuelta a otro apartado

- **WHEN**, con el apartado de estadísticas visible, el personal hace clic en `Películas`
- **THEN** el apartado de estadísticas se oculta, el panel de películas aparece y la URL permanece en `/gestion/`

### Requirement: Gráfico de recaudación por género

Dentro de un panel blanco, el apartado SHALL mostrar un Common Baseline Bar Chart con una barra por cada género de película registrado; cada barra SHALL medir como máximo el 10% del ancho de pantalla y reducirse cuando haya muchas barras para que todas quepan sin scroll. Las barras SHALL ser de color dorado.

#### Scenario: Una barra por género registrado que todas caben sin scroll

- **WHEN** hay varios géneros de película registrados
- **THEN** cada género tiene su barra, ninguna barra supera el 10% del ancho de pantalla y todas caben en el gráfico sin scroll

#### Scenario: Barras doradas

- **WHEN** se muestra el gráfico
- **THEN** todas las barras tienen el color dorado de la paleta

### Requirement: Altura de las barras por recaudación con tope

La altura de cada barra SHALL crecer en función de la recaudación total de su género —suma, por cada función asociada, de `entradas_compradas` por `precio_entrada`— con un paso fijo por cada 2000 de recaudación y sin superar el 30% del alto total de la pantalla.

#### Scenario: La barra crece con la recaudación y llega a su tope

- **WHEN** dos géneros tienen recaudaciones distintas dentro del periodo activo
- **THEN** el género con mayor recaudación tiene la barra más alta y ninguna barra supera el 30% del alto de la pantalla

#### Scenario: La barra se acota pero el total mostrado no

- **WHEN** la recaudación de un género supera el punto en el que su barra alcanza el tope
- **THEN** su barra queda en la altura máxima y el total de recaudación mostrado refleja el valor real completo

### Requirement: Etiquetas del gráfico

El gráfico SHALL mostrar el nombre de cada género debajo de la línea base de la que parten las barras, y encima de cada barra su total de recaudación.

#### Scenario: Género debajo de la línea base y total encima de la barra

- **WHEN** se muestra el gráfico
- **THEN** el nombre de cada género aparece debajo de la línea central y el total de recaudación de ese género aparece encima de su barra

### Requirement: Listado de películas por recaudación

Debajo del gráfico, el sistema SHALL mostrar un listado de todas las películas; cada registro SHALL estar en un panel blanco con márgenes en todos sus lados y mostrar en una sola línea el título, el género, la cantidad de entradas vendidas (suma de `entradas_compradas` de sus funciones) y la recaudación (suma de la recaudación de cada una de sus funciones).

#### Scenario: Cada película con sus cuatro datos en una línea

- **WHEN** hay películas registradas
- **THEN** cada película aparece en un panel blanco con márgenes en todos sus lados y sus cuatro datos en la misma línea

#### Scenario: Listado sin películas

- **WHEN** no hay películas registradas
- **THEN** el listado muestra un estado vacío en lugar de registros

### Requirement: Orden y distintivo de mayor recaudación

El listado SHALL estar ordenado de mayor a menor recaudación total y la película con mayor recaudación SHALL mostrar un distintivo en dorado que la identifica como la de mayor recaudación.

#### Scenario: Película líder con distintivo dorado

- **WHEN** hay películas registradas
- **THEN** la primera del listado muestra el distintivo dorado y el resto figura ordenado de forma descendente

### Requirement: Selector de periodo semanal, mensual y anual

Entre el gráfico y el listado, alineado a la derecha, el sistema SHALL mostrar un botón que cicla entre el modo semanal, el mensual y el anual en cada clic. Cada modo SHALL considerar solo las funciones cuyo inicio cae dentro de la semana en curso (lunes a domingo, hora Argentina, con los días ya pasados incluidos), el mes en curso o el año en curso respectivamente, y el filtro SHALL aplicarse tanto al gráfico como al listado sin cambiar la URL.

#### Scenario: El botón cicla los tres modos

- **WHEN** el personal hace clic sucesivamente en el botón de periodo
- **THEN** el modo cambia de semanal a mensual, de mensual a anual y de anual a semanal, mostrando siempre el modo actual

#### Scenario: El cambio altera solo las funciones consideradas

- **WHEN** se cambia de modo existiendo funciones con inicio en distintas semanas, meses y años
- **THEN** los datos del gráfico y del listado se recalculan usando únicamente las funciones cuyo inicio cae en el periodo activo, y la URL permanece en `/gestion/`

#### Scenario: Semana en curso completa

- **WHEN** el modo semanal está activo y hay funciones con inicio en días ya pasados y en días futuros de la misma semana (lunes a domingo, hora Argentina)
- **THEN** se consideran todas las funciones de esa semana

### Requirement: Cálculo sobre funciones activas e inactivas

Todos los cálculos del apartado —recaudación por género, entradas vendidas y recaudación del listado— SHALL considerar tanto las funciones activas como las inactivas.

#### Scenario: La función inactiva se incluye en los totales

- **WHEN** una función no activa tiene entradas vendidas con inicio dentro del periodo activo
- **THEN** su recaudación se suma en la barra de su género y en el registro de su película
