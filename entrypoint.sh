#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python << END
import sys
import time

import psycopg2

suggest_unrecoverable_after = 30
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
        sys.stderr.write("Esperando a que PostgreSQL esté disponible...\n")

        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write("Esto está tardando más de lo esperado. La siguiente excepción puede indicar un error irrecuperable: '{}'\n".format(error))

    time.sleep(1)
END

>&2 echo 'PostgreSQL está disponible'

# Ejecutar el script start.sh
/code/start.sh

# Ejecutar el comando por defecto (gunicorn)
exec "$@"