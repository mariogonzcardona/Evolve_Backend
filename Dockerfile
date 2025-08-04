# Usar una imagen base oficial de Python
FROM python:3.11

# Evitar el buffering de salida de Python
ENV PYTHONUNBUFFERED=1

# Crear y establecer el directorio de trabajo en el contenedor
WORKDIR /code

# Instalar netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt /code/

# Instalar requirements de producción (en todos los entornos)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . /code/

# Dar permisos a scripts
RUN chmod +x /code/entrypoint.sh /code/start.sh

# Establecer entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]

# Comando por defecto (puede ser sobrescrito en docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
