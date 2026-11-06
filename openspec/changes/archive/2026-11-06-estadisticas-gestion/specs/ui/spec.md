# Spec Delta

## MODIFIED Requirements

### Requirement: Botón Estadísticas presente

El subNAV SHALL incluir el botón `Estadísticas` habilitado; al precionarlo SHALL cargar el apartado de estadísticas en el cuerpo de la vista de gestión sin cambiar la URL, con el mismo mecanismo de paneles que los CRUDs de la sección.

#### Scenario: Botón presente

- **WHEN** se abre la vista de gestión
- **THEN** el botón `Estadísticas` aparece junto a los otros cuatro en el subNAV, habilitado

#### Scenario: Carga sin cambio de URL

- **WHEN** se hace clic en `Estadísticas`
- **THEN** el apartado de estadísticas se muestra en el cuerpo de la vista de gestión y la URL permanece en `/gestion/`
