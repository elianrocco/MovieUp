# Design

## Context

MovieUp is a Django 6.1.1 project with MySQL backend, running inside Docker. The `peliculas` app already exists with boilerplate files (`models.py`, `views.py`, `services.py`, `urls.py`, `admin.py`, `templates/peliculas/`). No other apps exist yet. The project follows MVT + Service Layer pattern: views delegate business logic to `services.py`. All artifacts (code, identifiers, comments) must be in English per project conventions.

The target DB schema for `pelicula` was provided as MySQL DDL. Django will create its own table `peliculas_pelicula` (default naming) rather than mapping to the existing DDL directly.

## Goals / Non-Goals

**Goals:**
- Implement complete CRUD (list, detail, create, update, delete) for the `Pelicula` model.
- Store cover images on the filesystem under `imgs/` at the project root; store only the relative path in the DB.
- Use HTML5 form validation attributes only — no server-side form validation beyond Django's default `ModelForm` behavior.
- Support partial updates (option A): form sends all fields, empty fields are ignored by the service.
- Prepare (commented-out) integration points for a future `funciones` app so the delete operation can later check for associated records.

**Non-Goals:**
- Authentication/authorization (no `@login_required` or role checks — to be added in a later change).
- Pagination, search, or filtering on the list view.
- CSS, JavaScript, or any frontend framework.
- REST API — all endpoints are server-rendered HTML forms.
- Creating the `funciones` app — only prepare commented hooks.
- Mapping to an existing MySQL table via `db_table` — Django creates its own table.

## Decisions

### 1. ImageField with `MEDIA_ROOT` for cover images

**Decision:** Use Django's `ImageField(upload_to='imgs/')` with `MEDIA_ROOT = BASE_DIR / 'imgs'` and `MEDIA_URL = '/imgs/'`.

**Rationale:** Django's built-in file storage handles file I/O, naming conflicts, and path resolution. The DB stores only the relative path (e.g., `imgs/poster_abc123.jpg`), which is exactly what the spec requires. Serving images in development is handled by `django.conf.urls.static`.

**Alternatives considered:**
- Custom `FileField` + manual `os.makedirs`/`open()` — more error-prone, reinvents what Django already does.
- Cloud storage (S3, etc.) — premature for this stage.

### 2. Function-based views (not class-based)

**Decision:** Use function-based views with explicit `@require_http_methods` decorators.

**Rationale:** The project has no existing views to establish a pattern. FBVs are simpler for a basic CRUD, easier to understand for contributors, and map 1:1 to URLs. CBVs would add abstraction without benefit at this scale.

### 3. Service layer receives `request.POST` + `request.FILES`

**Decision:** Services accept a dictionary of form data and the uploaded file separately. Example signature: `create_pelicula(data: dict, image_file) -> Pelicula`.

**Rationale:** Keeps services testable without constructing `HttpRequest` objects. The view handles extraction from `request.POST` / `request.FILES`; the service handles business logic.

### 4. Partial update via dict filtering in service

**Decision:** In `update_pelicula`, iterate over the provided data dict and apply every value that is neither `None` nor `''` — an explicit `False` is a real value and must be applied. For the image: if a new file is provided, delete the old file from disk before saving the new one.

**Rationale:** Simple, explicit, and aligns with option A (user confirmed). No need for a separate `ModelForm` per field. A truthiness check (`if value:`) silently drops `False`, which made it impossible to uncheck `en_cartelera` from Yes to No.

**Trade-off:** `False` and `0` are treated as intended values, so a caller must omit a field (rather than send an empty value) to leave it untouched.

### 5. Commented-out future `funciones` integration

**Decision:** In `delete_pelicula`, include a commented block that would import from `funciones.models` and check for associated records. Add a comment explaining what to uncomment when the app exists.

**Rationale:** The spec explicitly requires preparation without breaking tests. Commented code with clear TODO markers is the standard approach. The block stays commented so no query against `funciones` ever runs while the app does not exist — an uncommented import would break every delete at URL-conf time.

### 10. Templates are plain HTML (no CSS, no JavaScript)

**Decision:** The four templates render bare semantic HTML. Styling and client-side behavior are out of scope for this change.

**Rationale:** Consistent with the Non-Goals. The UI is verified for structure and data binding, not presentation. Adding a design system later is a separate change that does not alter the behavior specified in `specs/movies/spec.md`.

### 6. HTML5 validation only (no custom form classes)

**Decision:** Templates use raw `<form>` with HTML5 attributes: `required`, `maxlength`, `type="date"`, `type="number"`, `type="url"`, `min="1"`. No Django `ModelForm` or `forms.py` — the view reads `request.POST` directly.

**Rationale:** The spec mandates HTML-only validation. Django `ModelForm` would add server-side validation that duplicates HTML5 checks. Keeping it simple: templates handle validation, views handle data extraction, services handle business logic.

**Trade-off:** No server-side validation means a malicious client can bypass HTML5 checks. Acceptable for an internal admin tool at this stage; server-side validation can be added later when auth is implemented.

### 7. URL structure

**Decision:**
```
/peliculas/                  → list
/peliculas/<int:pk>/         → detail
/peliculas/create/           → create (GET/POST)
/peliculas/<int:pk>/update/  → update (GET/POST)
/peliculas/<int:pk>/delete/  → delete (GET confirm / POST execute)
```

**Rationale:** Standard Django CRUD URL pattern. Using `pk` (not `id`) for consistency with Django conventions.

### 8. Model field mapping

**Decision:**
| DDL Field | Django Field | Notes |
|---|---|---|
| `titulo VARCHAR(150) UNIQUE NOT NULL` | `CharField(max_length=150, unique=True)` | |
| `imagen_portada VARCHAR(255) NOT NULL` | `ImageField(upload_to='imgs/')` | DB stores path, not the image |
| `genero VARCHAR(45) NOT NULL` | `CharField(max_length=45)` | |
| `duracion_minutos INT NOT NULL` | `PositiveIntegerField()` | Duration can't be negative |
| `descripcion MEDIUMTEXT NOT NULL` | `TextField()` | Django TextField → LONGTEXT in MySQL (compatible) |
| `clasificacion VARCHAR(10) NOT NULL` | `CharField(max_length=10)` | |
| `fecha_estreno DATE NOT NULL` | `DateField()` | |
| `url_trailer VARCHAR(255) NOT NULL` | `URLField(max_length=255)` | Django URLField → VARCHAR(200) by default; override max_length to 255 |
| *(new)* | `BooleanField(default=False)` | `en_cartelera` |

### 9. `MEDIA_ROOT` location and `.gitignore`

**Decision:** `MEDIA_ROOT = BASE_DIR / 'imgs'`. Add `imgs/` to `.gitignore` (uploaded images shouldn't be versioned).

## Risks / Trade-offs

**[No server-side validation]** → Mitigation: Acceptable for internal admin tool. Add server-side validation when auth/roles are implemented.

**[Image file leaks on delete]** → Mitigation: `delete_pelicula` must explicitly delete the image file from disk when deleting a movie. The service handles this.

**[Image file not cleaned up on update failure]** → Mitigation: In `update_pelicula`, delete the old image only after the new image is successfully saved. If the DB update fails, the old file remains intact.

**[No auth on CRUD endpoints]** → Mitigation: Explicitly out of scope for this change. To be addressed in a separate auth/authorization change.

**[Partial update ignores intentional emptying]** → Mitigation: With option A, empty fields are treated as "not changed." If a user needs to clear a field (e.g., remove a trailer URL), they'd need to enter a placeholder. Acceptable for now; can revisit if needed.
