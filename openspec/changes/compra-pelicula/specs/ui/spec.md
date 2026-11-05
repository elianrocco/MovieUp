# Spec Delta

## REMOVED Requirements

### Requirement: Gating de Comprar entradas

**Reason**: La vista de compra ya existe: el botón deja de quedarse sin destino y su gating se redefine junto con el retorno del login.

**Migration**: Los botones de compra de la home usan `/compras/<pelicula_id>/`; el `Login` del nav conserva el retorno a `/`.

## ADDED Requirements

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
