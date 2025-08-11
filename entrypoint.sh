#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Esperar a que PostgreSQL esté disponible
echo "Esperando a que PostgreSQL esté disponible..."
python << END
import sys, time, psycopg2

start = time.time()
while True:
    try:
        psycopg2.connect(
            dbname="${DB_NAME}",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_HOST}",
            port="${DB_PORT}",
        )
        break
    except psycopg2.OperationalError as error:
        sys.stderr.write("PostgreSQL aún no está disponible...\n")
        if time.time() - start > 30:
            sys.stderr.write(f"Esto está tardando demasiado. Error: {error}\n")
    time.sleep(1)
END

>&2 echo '✅ PostgreSQL está disponible'

# Ejecutar el script de inicio
exec /code/start.sh