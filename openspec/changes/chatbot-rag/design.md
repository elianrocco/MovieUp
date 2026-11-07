# Design

## Context

MovieUp es Django 6.1 (MVT + Service Layer en `services.py` por convención), con front sin build (HTML/CSS/JS plano), Docker multi-stage y variables por `env_file` de compose. Ya usa `langchain==1.4.0` en `requirements.txt` sin ninguna integración concreta. El shell tiene un nav `position: sticky` (z-index 100, ~76 px) y un footer estático al final del contenido: el widget debe convivir con ambos sin taparlos. El ejemplo `rag-chat` (repo hermano) aporta el patrón a seguir (`ingest.py` MD → chunks → embeddings → Chroma y `chat.py` PROMPT_TEMPLATE + retriever + LLM), simplificado a lo esencial. Ver propuesta para el motivo.

## Goals / Non-Goals

**Goals:**
- Widget de chat en todas las páginas con respuestas grounded en el documento de conocimiento y en los datos actuales de la cartelera.
- Pipeline de ingesta reproducible con un solo comando dentro del contenedor.
- Cadena RAG + snapshot vivo centralizados en un service reutilizable por la vista y por el CLI.
- Contrato de errores (400/503) y visibilidad por rol verificables por tests sin red.

**Non-Goals:**
- Persistencia server-side de conversaciones (JSON, sesiones, tablas nuevas).
- Streaming de respuestas, subida de archivos ni múltiples documentos.
- Subida de imágenes para el icono (es un asset estático) ni configuración del widget por usuario.
- Fine-tuning o ajuste de modelos; otros proveedores LLM (Ollama, OpenAI).
- Registro/login obligatorio para usar el chat (ver D6).

## Decisions

**D1 — App Django `chatbot` con Service Layer.** Toda la lógica (RAG + snapshot vivo) vive en `movie_up/chatbot/services.py`; `views.py` solo orquesta request → service → respuesta JSON, según la convención del proyecto (vistas delgadas). *Alternativa:* lógica en la vista — viola la convención y dificulta reutilizarla desde `chat.py`.

**D2 — Pipeline de ingesta con los 5 temas estáticos.** `TextLoader` (utf-8) → `RecursiveCharacterTextSplitter` (chunk 500, overlap 50, separadores `["\n## ", "\n### ", "\n", ". ", " "]` — las fronteras por subtítulo primero) → `HuggingFaceEmbeddings` con `sentence-transformers/all-MiniLM-L6-v2` (~80 MB, corre sin API externa) → `Chroma.from_documents` en `./chroma_db/`. La carpeta queda en la raíz del repo dentro del bind mount `.:/app`, así persiste en el host, está en `.gitignore` y se regenera con una ingesta. El documento cubre: frecuencia de publicación (promedio de 2 a 4 películas al mes), compra paso a paso (simulando que la barrera de pago está implementada), reembolso paso a paso con restricciones (simulando que la barrera de pago está implementada), uso de la entrada virtual (mostrar el código en el cine) y datos guardados tras registrarse con Google. *Alternativas:* FAISS (más configuración, sin ganancia acá), embeddings de OpenAI (otra key y costo por consulta).

**D3 — LLM vía Groq.** `ChatGroq(temperature=0, model=os.getenv("GROQ_MODEL", <default verificado en implementación>), api_key=os.getenv("GROQ_API_KEY"))`. La key vive en `.env` y llega a ambos servicios por `env_file` de compose — sin `python-dotenv`. *Alternativa:* Ollama (el ejemplo lo soporta) — descartada: el usuario pidió Groq.

**D4 — `PROMPT_TEMPLATE` con `{context}`, `{history}` y `{question}`.** `{context}` se compone de los fragmentos RAG + el bloque de datos vivos (D7). El historial lo mantiene el cliente: el JS envía los últimos 10 mensajes en cada POST y el endpoint queda stateless (sin tablas ni sesiones nuevas). *Alternativa:* persistir conversaciones como el ejemplo (archivos JSON) — descartada por simpleza; se puede añadir después sin tocar specs.

**D5 — `ingest.py` y `chat.py` en la raíz.** `ingest.py` es un clon simplificado del ejemplo (recibe la ruta del `.md`, por defecto `movie_up/chatbot/data/chatbot.md`). `chat.py` importa `chatbot.services` agregando `movie_up/` al `sys.path` y ejecutando `django.setup()` con `DJANGO_SETTINGS_MODULE=core.settings` — el setup es necesario porque `services.py` consulta el ORM para el snapshot vivo (D7), y de esta forma el CLI responde con la misma cadena que la web. *Alternativa:* management commands de Django — más ceremonia de la necesaria.

**D6 — Widget en el shell base, sin tapar el nav ni el footer.** El include del widget vive en el template base y se envuelve en `{% if not user.is_staff %}`: visitantes y cuentas comunes ven el icono, administradores no. Posicionamiento: icono y panel `position: fixed` a la izquierda; `top` bajo el nav sticky (offset ~76 px) y `bottom` igual a la altura del footer medida en el cliente con `ResizeObserver` — el footer es estático, así que un `bottom: 0` fijo lo taparía al llegar al fin del scroll y la altura medida evita la intersección en cualquier punto. Ancho del panel `clamp(280px, 25vw, 420px)` (~320 px a 1280×900) con scroll interno solo en la zona de mensajes. El icono muestra un asset de imagen estático (`static/chatbot/icon.png`), reemplazable por archivo. Estilos con la paleta del skill `ui-design` y botones en el rango 40–56 px; el chat queda público (sin login) para no romper el flujo de visitante. *Alternativas:* panel `bottom: 0` (taparía el footer), hacer sticky el footer (modificaría la spec `ui`), hardcodear una altura de footer (rompe con footers variables o responsivos).

**D7 — Snapshot vivo de la cartelera en cada consulta.** Antes de invocar la cadena, `services.py` consulta las películas en cartelera y sus funciones próximas/activas (fecha, hora, sala, precio, entradas disponibles) y agrega el bloque a `{context}`. Así los temas "funciones de una película elegida", "películas en cartelera" y "película más nueva" responden datos reales en el momento de la consulta, sin re-ingestar el `.md`. Se limita el bloque a funciones próximas/activas para acotar su tamaño. *Alternativas:* re-ingesta periódica del `.md` (los datos se vuelven viejos entre ingesta y consulta y no responde "la película más nueva" en el momento), tool-calling del LLM hacia los models (más complejo de lo necesario para este volumen de datos).

**D8 — Mensaje inicial estático.** La lista de las preguntas disponibles vive hardcodeada en el template/JS, alineada con los subtítulos `##` del `.md`; al abrir el panel sin mensajes se muestra como mensaje del asistente y el clic en una la envía. Cero llamadas al LLM al abrir el chat. *Alternativas:* derivar la lista de los subtítulos del `.md` en la ingesta (metadata extra sin necesidad), generarla con el LLM (costo y latencia en cada apertura).

**D9 — Tests sin red.** `tests.py` mockea `services.responder` y las consultas del snapshot para cubrir: contrato del endpoint (`200` con `answer`, `400` sin pregunta, `503` sin base/clave), visibilidad del icono (visitante y cuenta común lo ven, administrador no), mensaje inicial en el panel vacío y render del widget dentro del shell. La verificación E2E con Groq real queda para Playwright con la key provista por el usuario.

## Risks / Trade-offs

- [Build pesado: `sentence-transformers`/`torch` aumentan GBs y el stage builder se reconstruye al tocar `requirements.txt`] → aceptar el tiempo de build; verificar ruedas para Python 3.14 en el primer build y, si faltan, anclar el índice CPU-only de torch.
- [Clave de Groq expuesta al uso público del chat (costo/abuso)] → D6 acepta el trade-off; mitigación simple: exigir login después si el usuario lo pide.
- [Primera ingesta descarga el modelo de embeddings (~80 MB) en runtime] → requiere red en el contenedor (ya necesaria para el build); una sola vez por volumen.
- [Respuestas alucinadas si el prompt no es estricto] → el template pide responder solo con el contexto y el escenario "pregunta sin respaldo" lo cubre en specs y tests.
- [`chroma_db/` generada localmente puede desincronizarse del `.md`] → la tarea de verificación corre la ingesta después de cada cambio del documento.
- [El snapshot vivo crece con el número de funciones] → limitar el bloque a funciones próximas/activas y agruparlas por película.
- [La lista de preguntas del JS puede desalinearse de los subtítulos del `.md`] → la tarea de contenido exige que coincidan y la verificación final las compara.

## Migration Plan

1. `requirements.txt` + rebuild (`docker compose build`).
2. `.env` con `GROQ_API_KEY` y `GROQ_MODEL` opcional; reiniciar compose.
3. Correr `ingest.py` dentro del contenedor para crear `chroma_db/`.
4. Deploy aditivo: include del widget en el template base, ruta nueva, sin migraciones ni cambios de datos. Rollback: revertir el commit y rebuild; `chroma_db/` es prescindible (regenerable).
