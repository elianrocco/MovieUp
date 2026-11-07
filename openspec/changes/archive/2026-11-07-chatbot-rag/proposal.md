# Proposal

## Why

MovieUp no tiene ningún canal de ayuda dentro del sitio: las dudas sobre cómo comprar entradas, reembolsar, validar o usar la cuenta se resuelven fuera de la web. Un chatbot RAG con LangChain y Groq puede responder esas preguntas a partir de un documento de conocimiento propio y de los datos actuales de la cartelera, integrado en la web como widget de chat flotante.

## What Changes

- Nueva app Django `chatbot` con un widget de chat flotante (icono abajo a la izquierda + panel lateral) incluido en el shell base: visible en todas las páginas para visitantes y cuentas comunes, oculto para cuentas administradoras.
- Endpoint JSON de consulta al modelo (`POST /chatbot/api/preguntar/`) con contrato de errores `400`/`503`.
- Cadena RAG en un service (Service Layer): fragmentos recuperados desde Chroma con `HuggingFaceEmbeddings` + bloque de datos vivos de la cartelera consultado a la base de datos en cada pregunta + LLM de Groq orquestado por LangChain con un `PROMPT_TEMPLATE` (contexto + historial + pregunta).
- Mensaje inicial: al abrir un chat nuevo, el asistente lista las preguntas que puede responder y el clic en una la envía.
- `ingest.py` en la raíz del proyecto: convierte el documento Markdown de conocimiento en la base vectorial Chroma persistente.
- `chat.py` en la raíz: CLI simple (interactivo y modo pregunta única) que reutiliza el service del chatbot.
- Documento de conocimiento `movie_up/chatbot/data/chatbot.md` con formato `#` título / `##` subtítulo / `###` subtemas y `---` al cerrar cada subtítulo. Cubre los 5 temas estáticos: frecuencia de publicación de películas (promedio de 2 a 4 al mes), compra paso a paso, reembolso paso a paso con sus restricciones, uso de la entrada virtual y datos que se guardan al registrarse con Google.
- Dependencias nuevas en `requirements.txt` (`langchain-community`, `langchain-text-splitters`, `langchain-chroma`, `langchain-huggingface`, `langchain-groq`, `chromadb`, `sentence-transformers`), instaladas dentro de Docker con `docker compose build`.
- Configuración: `GROQ_API_KEY` agregada a `.env` (llega a los contenedores por `env_file`) y `chroma_db/` agregado a `.gitignore`.

## Capabilities

### New Capabilities

- `chatbot`: asistente RAG integrado en la web como widget flotante — visibilidad por rol, mensaje inicial con las preguntas disponibles, endpoint de consulta con contrato de errores, pipeline de ingesta del documento de conocimiento, respuestas basadas en el documento y en los datos actuales de la cartelera.

### Modified Capabilities

Ninguna. El widget se agrega al shell existente de `ui` (nav y footer) sin cambiar sus requisitos.

## Impact

- Código nuevo: `movie_up/chatbot/` (`services.py`, `views.py`, `urls.py`, `templates/`, `static/`, `tests.py`, `data/chatbot.md`), inclusión del widget en el template base del shell, `ingest.py` y `chat.py` en la raíz.
- Configuración: `movie_up/core/settings.py` (INSTALLED_APPS), `movie_up/core/urls.py`, `requirements.txt`, `.env`, `.gitignore`.
- Docker: rebuild de la imagen (el stage builder descarga `torch`/`sentence-transformers`, build más pesado que los previos).
- Externos: API de Groq (requiere `GROQ_API_KEY`) y red en runtime para descargar el modelo de embeddings (~80 MB) en la primera ingesta.
