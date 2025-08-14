# Usar una imagen base oficial de Python
FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Instalar netcat-openbsd y dos2unix (temporalmente)
RUN apt-get update && apt-get install -y netcat-openbsd dos2unix && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código (sin los scripts todavía)
COPY . /code/

# Convertir a formato LF y dar permisos
RUN dos2unix /code/entrypoint.sh /code/start.sh && \
    chmod +x /code/entrypoint.sh /code/start.sh

# Establecer entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
