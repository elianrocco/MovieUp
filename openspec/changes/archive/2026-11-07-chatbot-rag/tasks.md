# Tasks

## 1. Dependencias y configuración

- [x] 1.1 Agregar a `requirements.txt` los paquetes faltantes (`langchain-community`, `langchain-text-splitters`, `langchain-chroma`, `langchain-huggingface`, `langchain-groq`, `chromadb`, `sentence-transformers`) con versiones exactas compatibles con `langchain==1.4.0` y verificar que `docker compose build` termina sin errores (confirmar que existen ruedas de `torch` para Python 3.14).
- [x] 1.2 Agregar `GROQ_API_KEY` a `.env` (clave provista por el usuario) y `chroma_db/` a `.gitignore`, y verificar con `docker compose exec web printenv GROQ_API_KEY` que la variable llega al contenedor y con `git status` que `chroma_db/` queda ignorada.

## 2. Documento de conocimiento e ingesta

- [x] 2.1 Crear `movie_up/chatbot/data/chatbot.md` con el formato `#` título, `##` subtítulo, `###` subtemas y `---` al cerrar cada subtítulo, cubriendo los 5 temas estáticos (frecuencia de publicación: promedio de 2 a 4 películas al mes; compra paso a paso simulando que la barrera de pago está implementada; reembolso paso a paso con sus restricciones simulando que la barrera de pago está implementada; uso de la entrada virtual mostrando el código en el cine; datos que se guardan al registrarse con Google), y verificar la estructura con un parseo simple (un `#`, subtítulos `##` alineados con las preguntas del widget y un `---` por sección).
- [x] 2.2 Crear `ingest.py` en la raíz (`TextLoader` → `RecursiveCharacterTextSplitter` 500/50 → `HuggingFaceEmbeddings` `all-MiniLM-L6-v2` → `Chroma` en `./chroma_db/`) y verificar con `docker compose exec web python ingest.py movie_up/chatbot/data/chatbot.md` que imprime el número de chunks y deja `chroma_db/` creada.

## 3. Service, endpoint y widget

- [x] 3.1 Crear `movie_up/chatbot/services.py` con `PROMPT_TEMPLATE` (contexto + historial + pregunta), recuperador top-k, LLM de Groq (temperature 0, modelo por `GROQ_MODEL` con default), snapshot vivo de la cartelera (películas en cartelera con sus funciones próximas) que se inyecta en el contexto y `responder(pregunta, historial)`; verificar con tests unitarios que mockean la cadena y las consultas del snapshot (formato del prompt, inclusión del bloque vivo y respuesta enviada) en `manage.py test chatbot`.
- [x] 3.2 Crear `views.py` (POST `/chatbot/api/preguntar/`), `urls.py`, y registrar la app en `INSTALLED_APPS` y `core/urls.py`; verificar con tests del endpoint que responde JSON con `answer` (200), `400` sin pregunta y `503` sin base o clave, todos pasando en `manage.py test chatbot`.
- [x] 3.3 Crear el widget: include en `base.html` y en el shell `admin/base_site.html` con `{% if not user.is_staff %}`, asset de imagen del icono (`static/chatbot/icon.png`) y `static/chatbot/chatbot.{css,js}` con el icono fijo abajo a la izquierda, panel lateral `clamp(280px, 25vw, 420px)` con `top` bajo la navegación (incluido el subnav de gestión) y `bottom` medido por `ResizeObserver` para no tapar el footer, scroll interno de mensajes, mensaje inicial con las preguntas disponibles y clic para enviarlas, burbujas, indicador de carga, mensajes de error, envío de los últimos 10 mensajes como historial y estilos con la paleta del skill `ui-design`; verificar con un test de render que el widget aparece dentro de ambos shells y con `manage.py test chatbot` en verde.
- [x] 3.4 Agregar tests de comportamiento del widget: el icono se renderiza para visitante y cuenta común (también en el login público de Django Admin) y NO se renderiza para cuenta administradora, y el mensaje inicial lista las preguntas disponibles en el panel vacío; verificar con `manage.py test chatbot` en verde.

## 4. CLI en la raíz

- [x] 4.1 Crear `chat.py` en la raíz (modo interactivo y `--question`) que reutiliza `chatbot.services` vía `sys.path` con `django.setup()` (`DJANGO_SETTINGS_MODULE=core.settings`, necesario por el snapshot vivo del ORM); verificar con `docker compose exec web python chat.py --question "<pregunta sobre el documento>"` que imprime JSON con `answer` (requiere `GROQ_API_KEY` y `chroma_db/`).

## 5. Verificación integral

- [x] 5.1 Correr la suite completa `python movie_up/manage.py test --noinput peliculas salas funciones cuentas entradas compras core estadisticas chatbot` con 0 fallos, `manage.py check` con 0 errores y `manage.py makemigrations --check` sin cambios.
- [x] 5.2 Verificar en Playwright a 1280×900 en cualquier página: el icono es visible para visitante; al hacer clic se abre el panel y su caja no intersecta el nav ni el footer (bounding box), con scroll interno; el clic en una pregunta del mensaje inicial obtiene respuesta real con Groq (si hay clave) o muestra el mensaje de error visible (si no la hay); tras iniciar sesión como administrador el icono no aparece; consola sin errores y captura de página completa guardada en `.playwright-mcp/`.

## Workflow follow-up

- Sincronizar el delta `chatbot` a `openspec/specs/` y archivar el change cuando el usuario lo apruebe (`openspec validate --specs --strict` previo).
