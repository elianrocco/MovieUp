#!/bin/sh
# interprete del script: se ejecuta con sh (POSIX)

# aborta el script si algun comando falla
set -e

# solo inicializa si estamos en un proyecto Django (existe manage.py)
if [ -f "movie_up/manage.py" ]; then
    # solo espera la base de datos si se definio la variable DB_HOST
    if [ -n "$DB_HOST" ]; then
        # usa el puerto de DB_PORT o 3306 por defecto
        DB_PORT="${DB_PORT:-3306}"
        echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
        # contador de intentos de conexion
        attempts=0
        # reintenta abrir una conexion TCP a la base hasta que responda
        until python -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('${DB_HOST}', ${DB_PORT}))" 2>/dev/null; do
            # suma un intento
            attempts=$((attempts + 1))
            # si llega a 60 intentos, corta
            if [ "$attempts" -ge 60 ]; then
                echo "Database not reachable after 60 attempts, aborting."
                # sale con error
                exit 1
            fi
            # espera 1 segundo antes de reintentar
            sleep 1
        done
    fi

    # las migraciones son archivos que funcionan como un historial de cambios de la reprecentacion de la bd en el codigo de python
    # aplica las migraciones de Django sin pedir confirmacion(actualiza la BD real segun el historial de cambios)
    python movie_up/manage.py migrate --noinput
fi

# reemplaza el proceso actual por el comando CMD del Dockerfile
exec "$@"
