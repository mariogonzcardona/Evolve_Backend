#!/bin/bash

echo "Esperando a que la base de datos esté disponible..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done

echo "La base de datos está disponible."

echo "📦 Aplicando migraciones..."
python /code/manage.py migrate --noinput

echo "📦 Ejecutando makemigrations (por si hay cambios)..."
python /code/manage.py makemigrations --noinput

echo "📦 Recolectando estáticos..."
python /code/manage.py collectstatic --noinput

echo "📦 Cargando datos iniciales..."
python manage.py loaddata fixtures/users_data.json
python manage.py loaddata fixtures/beneficios.json
python manage.py loaddata fixtures/direcciones.json
python manage.py loaddata fixtures/eventos.json
python manage.py loaddata fixtures/nacionalidades.json
python manage.py loaddata fixtures/tipos_patrocinio.json
python manage.py loaddata fixtures/tipos_boletos.json
python manage.py loaddata fixtures/tipo_boleto_beneficio.json

# 💡 Si estás corriendo pruebas
if [[ "$RUN_TESTS" == "true" ]]; then
  echo "Entorno de pruebas detectado. No se iniciará el servidor."
  exit 0
fi

# Iniciar el servidor según entorno
if [ "$ENVIRONMENT" = "local" ]; then
  echo "🚀 Iniciando el servidor de desarrollo..."
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "🚀 Iniciando el servidor de producción..."
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
fi
