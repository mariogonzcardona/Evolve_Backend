# 📦 Crossfit Backend System

## 📋 Descripción
**Crossfit Backend System** es una aplicación web para la **gestión administrativa de un box de CrossFit y BJJ**. Permite a los administradores gestionar usuarios, inscripciones, control financiero, asistencias y publicación de entrenamientos (WODs). Está construida utilizando **Django** y **Django REST Framework**, con autenticación basada en **JWT** y preparada para consumo de APIs por apps móviles y frontend web (Vue.js).

## 🚀 Tecnologías utilizadas
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker

## ⚙️ Requisitos previos
- Docker y Docker Compose instalados en tu máquina.

## 🛠️ Instalación y configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/mariogonzcardona/crossfit_backend_system.git
cd crossfit_backend_system
```

### 2. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Django
SECRET_KEY='your-secret-key'
DEBUG=True
ENVIRONMENT=local
ALLOWED_HOSTS="*"
CSRF_TRUSTED_ORIGINS="http://127.0.0.1:8000,http://localhost:8000"

# Django DB Connection
DB_HOST=db
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# PostgreSQL
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=your_postgres_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password

# Django Home
ADMIN_URL="http://localhost:8000/admin/"
SWAGGER_URL="http://localhost:8000/swagger/"

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "your_smtp_host"
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = "your_email_password"
DEFAULT_FROM_EMAIL = 'your_email@example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### 3. Construir y levantar los servicios
```bash
docker-compose up --build -d
```

### 4. Aplicar migraciones
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 5. Crear un superusuario
```bash
docker-compose exec crossfit_backend python manage.py createsuperuser
```

## 🔍 Uso
Una vez que todos los servicios estén en funcionamiento, puedes acceder a:

- **Home (en construcción):** [http://localhost:8080](http://localhost:8080/)
- **Administrador de Django:** [http://localhost:8080/admin](http://localhost:8080/admin)
- **Documentación de Swagger:** [http://localhost:8080/swagger](http://localhost:8080/swagger)

## ✅ Ejecución de pruebas
*(Próximamente)*  
Se incluirán pruebas automáticas usando **pytest** y **pytest-django**.

## 📧 Contacto
Si tienes alguna pregunta o problema, por favor contacta a [mariogonzcardona@gmail.com](mailto:mariogonzcardona@gmail.com).

---