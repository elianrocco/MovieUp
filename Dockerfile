# syntax=docker/dockerfile:1

# cada FROM crea un mundo totalmente aislado y nuevo
# etapa de construccion: compila las dependencias y las empaqueta como wheels, se usan luego en la etapa final
FROM python:3.14.7-slim-trixie AS builder

# variables de entorno de Python y pip (evita .pyc, logs sin buffer, silencia avisos y desactiva cache)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# instala compilador y cabeceras necesarias para compilar mysqlclient y Pillow
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# crea y accede a la carpeta de trabajo donde se guardaran los paquetes .whl
WORKDIR /wheels

# copia solo el archivo de dependencias (asi se aprovecha la cache de capas) en /wheels
COPY requirements.txt .

# compila cada dependencia y la guarda como wheel en /wheels
RUN pip wheel --wheel-dir /wheels -r requirements.txt


# etapa final: imagen liviana que solo ejecuta la aplicacion
#Ignora por completo todo lo que pasó en la etapa anterior, arranca de cero con una imagen pelada y solo importa el resultado final que obtuvo builder sin dejar compiladores inecesarios que ocupan espacio en la imagen final
FROM python:3.14.7-slim-trixie AS runtime

# variables de entorno de Python y pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# instala la libreria de MySQL para runtime, curl (usado por el healthcheck) y libjpeg para Pillow
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libmariadb3 \
        libjpeg62-turbo \
        curl \
    && rm -rf /var/lib/apt/lists/*

# crea un usuario sin privilegios para no ejecutar la app como root
RUN groupadd --system appuser \
    && useradd --system --gid appuser --create-home appuser

#crea y accede a la carpeta donde estara la app dentro del contenedor
WORKDIR /app 

#trae y copia únicamente los archivos .whl ya compilados desde la etapa anterior
COPY --from=builder /wheels /wheels
# copia el archivo de dependencias a la carpeta de trabajo para instalarlas
COPY requirements.txt .
#instala lo indicado en los archivos copiados, luego borra la carpeta wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

#copia todo el proyecto(no ignorado) en la carpeta app de el contenedor
COPY . .

# da permiso de ejecucion al entrypoint y asigna la carpeta app al usuario appuser
RUN chmod +x /app/docker-entrypoint.sh \
    && chown -R appuser:appuser /app

# desde aca los comandos se ejecutan como appuser (no root)
USER appuser

# documenta que la app queda escuchando en el puerto 8000
EXPOSE 8000

# verifica periodicamente que la app responda en el puerto 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/ || exit 1

# Un ENTRYPOINT en un Dockerfile es un script que define qué comando/s se ejecutará obligatoriamente cada vez que el contenedor comience a correr
# script que espera la base de datos y aplica migraciones antes de arrancar
ENTRYPOINT ["/app/docker-entrypoint.sh"]
# comando por defecto: servidor de desarrollo de Django en 0.0.0.0:8000
CMD ["python", "movie_up/manage.py", "runserver", "0.0.0.0:8000"]
