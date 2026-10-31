# Tasks

## 1. Model & Database

- [x] 1.1 Define `Pelicula` model in `movie_up/peliculas/models.py` with all fields per design mapping (titulo CharField unique, imagen_portada ImageField upload_to='imgs/', genero CharField, duracion_minutos PositiveIntegerField, descripcion TextField, clasificacion CharField, fecha_estreno DateField, url_trailer URLField max_length=255, en_cartelera BooleanField default=False). Verify: `python movie_up/manage.py makemigrations peliculas` generates migration without errors.
- [x] 1.2 Run `python movie_up/manage.py migrate` inside Docker and verify table `peliculas_pelicula` is created in MySQL. Verify: `docker compose exec web python movie_up/manage.py showmigrations peliculas` shows all migrations applied.

## 2. Settings & URL Configuration

- [x] 2.1 Add `MEDIA_ROOT = BASE_DIR / 'imgs'` and `MEDIA_URL = '/imgs/'` to `movie_up/core/settings.py`. Add `imgs/` to `.gitignore`. Verify: settings file contains both variables and .gitignore contains `imgs/`.
- [x] 2.2 Include `peliculas.urls` in `movie_up/core/urls.py` with `path('peliculas/', include('peliculas.urls'))` and add `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` for development serving. Verify: Django starts without import errors.

## 3. Admin Registration

- [x] 3.1 Register `Pelicula` model in `movie_up/peliculas/admin.py` with `admin.site.register(Pelicula)`. Verify: `/admin/` shows Pelicula in the admin interface.

## 4. Service Layer

- [x] 4.1 Implement `list_peliculas()` in `movie_up/peliculas/services.py` returning all Pelicula objects. Implement `get_pelicula(pk)` returning a single Pelicula or raising Http404. Verify: functions return expected data when called from Django shell.
- [x] 4.2 Implement `create_pelicula(data: dict, image_file) -> Pelicula` in services.py. Extract fields from data dict, create Pelicula instance with ImageField handling (Django auto-saves to MEDIA_ROOT). Verify: calling the function with valid data creates a record and an image file appears in `imgs/`.
- [x] 4.3 Implement `update_pelicula(pk, data: dict, image_file=None) -> Pelicula` in services.py. Get pelicula by pk (raise Http404 if not found). Only update fields that are non-empty in data dict. If image_file is provided: save new image, then delete old image file from disk, then update the DB path. Verify: partial update modifies only provided fields; image update replaces file on disk and path in DB; non-existent pk raises Http404.
- [x] 4.4 Implement `delete_pelicula(pk)` in services.py. Get object (raise Http404 if not found). Add commented-out block for future funciones association check with clear TODO comment explaining what to uncomment. Delete the image file from disk, then delete the DB record. Verify: delete removes both DB record and image file; commented code is present and syntactically valid.

## 5. Views

- [x] 5.1 Implement `pelicula_list` view in `movie_up/peliculas/views.py` calling `list_peliculas()` and rendering `peliculas/list.html`. Implement `pelicula_detail` view calling `get_pelicula(pk)` and rendering `peliculas/detail.html`. Verify: GET `/peliculas/` returns 200 with list template; GET `/peliculas/<pk>/` returns 200 with detail template; GET `/peliculas/999/` returns 404 for non-existent pelicula.
- [x] 5.2 Implement `pelicula_create` view: GET renders `peliculas/form.html` with empty context; POST extracts data from `request.POST` and image from `request.FILES['imagen_portada']`, calls `create_pelicula()`, redirects to list. Verify: GET `/peliculas/create/` shows form; POST with valid data creates record and redirects.
- [x] 5.3 Implement `pelicula_update` view: GET renders `peliculas/form.html` with pelicula context; POST extracts only non-empty fields from `request.POST` and optional image from `request.FILES`, calls `update_pelicula()`, redirects to detail. Verify: GET shows form pre-filled; POST with partial data updates only provided fields; GET/POST `/peliculas/999/update/` returns 404 for non-existent pelicula.
- [x] 5.4 Implement `pelicula_delete` view: GET renders `peliculas/confirm_delete.html`; POST calls `delete_pelicula(pk)` and redirects to list. Verify: GET shows confirmation; POST deletes record and image file, redirects to list.

## 6. URL Patterns

- [x] 6.1 Configure URL patterns in `movie_up/peliculas/urls.py`: `''` → list, `'<int:pk>/'` → detail, `'create/'` → create, `'<int:pk>/update/'` → update, `'<int:pk>/delete/'` → delete. Verify: all 5 URL patterns resolve to correct views without errors.

## 7. Templates

- [x] 7.1 Create `movie_up/peliculas/templates/peliculas/list.html` with HTML table showing titulo, genero, duracion_minutos, fecha_estreno, en_cartelera for each pelicula. Include links to detail, create. Verify: template renders a table with pelicula data when context contains `peliculas` queryset.
- [x] 7.2 Create `movie_up/peliculas/templates/peliculas/detail.html` showing all pelicula fields including imagen_portada (rendered as `<img src="{{ pelicula.imagen_portada.url }}">`). Include links to update and delete. Verify: template displays all fields correctly.
- [x] 7.3 Create `movie_up/peliculas/templates/peliculas/form.html` with HTML form using `method="POST"` and `enctype="multipart/form-data"`. Create mode: all fields have `required` attribute. Update mode: fields pre-filled, no `required`. HTML5 validation: `maxlength` per field, `type="date"` for fecha_estreno, `type="number" min="1"` for duracion_minutos, `type="url"` for url_trailer, `type="file" accept="image/*"` for imagen_portada. Use `{% if pelicula %}` to toggle create vs update mode. Verify: create form rejects empty fields via browser; update form allows partial submission.
- [x] 7.4 Create `movie_up/peliculas/templates/peliculas/confirm_delete.html` showing pelicula titulo and a confirmation form with POST method. Verify: template displays pelicula info and confirmation button.

## 8. Integration Verification

- [x] 8.1 Start Docker with `docker compose up --build`, create a pelicula via the create form, verify it appears in the list and detail views, verify image file exists in `imgs/` directory. Update the pelicula with partial data, verify only provided fields changed. Update with new image, verify old image is deleted and new image is saved. Delete the pelicula, verify both DB record and image file are removed.
