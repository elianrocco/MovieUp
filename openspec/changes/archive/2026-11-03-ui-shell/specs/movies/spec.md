# Spec Delta

## ADDED Requirements

### Requirement: Acceso restringido al personal en las rutas de gestión
Las rutas de listado, detalle, formulario y borrado de películas SHALL aceptar solo al personal autorizado: un visitante SHALL ser redirigido al inicio de sesión y una cuenta común SHALL ser redirigida a la página principal, sin que el registro sufra cambios.

#### Scenario: Visitante en el listado
- **WHEN** un visitante solicita `/peliculas/`
- **THEN** es redirigido a la pantalla de inicio de sesión

#### Scenario: Cuenta común en el detalle
- **WHEN** una cuenta común solicita `/peliculas/<id>/` con un ID existente
- **THEN** es redirigida a la página principal y no ve el detalle

#### Scenario: Cuenta común intenta editar
- **WHEN** una cuenta común solicita `/peliculas/<id>/update/`
- **THEN** es redirigida a la página principal y el registro queda sin cambios

#### Scenario: Cuenta común intenta borrar
- **WHEN** una cuenta común solicita `/peliculas/<id>/delete/`
- **THEN** es redirigida a la página principal y el registro permanece

#### Scenario: Personal autorizado
- **WHEN** el personal solicita cualquiera de las cuatro rutas
- **THEN** accede y opera normalmente
