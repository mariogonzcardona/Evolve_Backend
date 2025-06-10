# Usar una imagen base oficial de Python
FROM python:3.11

# Evitar el buffering de salida de Python
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=local

# Crear y establecer el directorio de trabajo en el contenedor
WORKDIR /code

# Instalar netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

# Copiar los requirements
COPY requirements.txt requirements-dev.txt /code/


# Instalar requirements de producción
RUN pip install --no-cache-dir -r requirements.txt

# Instalar requisitos de desarrollo si estamos en entorno local
RUN if [ "$ENVIRONMENT" = "local" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

# Copiar el resto del código de la aplicación
COPY . /code/

# Copiar el script entrypoint y el script de inicio
COPY entrypoint.sh /code/entrypoint.sh
COPY start.sh /code/start.sh

# Hacer que los scripts sean ejecutables
RUN chmod +x /code/entrypoint.sh /code/start.sh

# Establecer el entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "inventory.wsgi:application"]