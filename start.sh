#!/bin/bash

echo "Esperando a que la base de datos esté disponible..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done

echo "La base de datos está disponible."

# Flags (por default no hacer cosas pesadas)
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"
RUN_COLLECTSTATIC="${RUN_COLLECTSTATIC:-false}"
RUN_FIXTURES="${RUN_FIXTURES:-false}"

echo "📦 Aplicando migraciones? $RUN_MIGRATIONS"
if [ "$RUN_MIGRATIONS" = "true" ]; then
  python /code/manage.py migrate --noinput
fi

echo "📦 Recolectando estáticos? $RUN_COLLECTSTATIC"
if [ "$RUN_COLLECTSTATIC" = "true" ]; then
  python /code/manage.py collectstatic --noinput
fi

echo "📦 Cargar fixtures? $RUN_FIXTURES"
if [ "$RUN_FIXTURES" = "true" ]; then
  python manage.py loaddata fixtures/users_data.json
  python manage.py loaddata fixtures/beneficios.json
  python manage.py loaddata fixtures/direcciones.json
  python manage.py loaddata fixtures/eventos.json
  python manage.py loaddata fixtures/nacionalidades.json
  python manage.py loaddata fixtures/tipos_patrocinio.json
  python manage.py loaddata fixtures/tipos_boletos.json
  python manage.py loaddata fixtures/tipo_boleto_beneficio.json
fi

# 💡 Si estás corriendo pruebas
if [[ "${RUN_TESTS:-false}" == "true" ]]; then
  echo "Entorno de pruebas detectado. No se iniciará el servidor."
  exit 0
fi

# Iniciar el servidor según entorno
if [ "${ENVIRONMENT:-prod}" = "local" ]; then
  echo "🚀 Iniciando el servidor de desarrollo..."
  python manage.py runserver 0.0.0.0:8000
else
  echo "🚀 Iniciando el servidor de producción..."
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
fi
