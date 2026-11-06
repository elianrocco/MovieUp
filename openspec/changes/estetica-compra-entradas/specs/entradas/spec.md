# Spec Delta

## ADDED Requirements

### Requirement: Presentación del listado de entradas

El listado SHALL mostrar cada entrada dentro de un rectángulo de bordes redondeados con el dorado del nav, con todos los registros centrados, y SHALL renderizar el enlace de cada registro como un botón con ese mismo dorado y un contorno rojo.

#### Scenario: Registro en rectángulo dorado

- **WHEN** una cuenta con entradas abre el listado
- **THEN** cada entrada aparece dentro de un rectángulo de bordes redondeados con el dorado del nav y los registros aparecen centrados

#### Scenario: Enlace de detalle como botón

- **WHEN** se renderiza el listado
- **THEN** el enlace al detalle de cada registro se muestra como un botón dorado con contorno rojo y conduce al detalle de esa entrada

### Requirement: Presentación del detalle de entrada

El detalle SHALL presentarse con todos los datos centrados, con márgenes entre ellos y dentro de un rectángulo de bordes redondeados con el dorado del nav. El enlace `Volver a mis entradas` SHALL renderizarse como un botón con ese dorado y un contorno rojo, y SHALL aparecer al lado un segundo botón con el texto `Reembolso`.

#### Scenario: Detalle dentro del rectángulo dorado

- **WHEN** se abre el detalle de una entrada
- **THEN** todos sus datos aparecen centrados, con un margen visible entre cada par de datos, dentro de un rectángulo de bordes redondeados con el dorado del nav

#### Scenario: Los dos botones del detalle

- **WHEN** se renderiza el detalle de una entrada
- **THEN** aparecen el botón `Volver a mis entradas` con el dorado del nav y un contorno rojo y, al lado, el botón `Reembolso`

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
