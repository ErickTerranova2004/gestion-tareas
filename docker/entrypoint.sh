#!/bin/sh
# Punto de entrada del contenedor Django:
#   1. espera a que PostgreSQL acepte conexiones
#   2. aplica migraciones y recolecta estáticos
#   3. ejecuta el comando recibido (por defecto gunicorn)
set -e

echo "==> Esperando a PostgreSQL en ${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432} ..."
python - <<'PY'
import os, sys, time
import psycopg2

for intento in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "gestion_tareas"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
        ).close()
        print("==> PostgreSQL disponible")
        sys.exit(0)
    except psycopg2.OperationalError:
        time.sleep(1)
print("==> PostgreSQL no respondió a tiempo", file=sys.stderr)
sys.exit(1)
PY

echo "==> Aplicando migraciones"
python manage.py migrate --noinput

echo "==> Recolectando archivos estáticos"
python manage.py collectstatic --noinput -v 0

echo "==> Iniciando: $*"
exec "$@"
