from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el correo y contraseña proporcionados.
        """
        if not email:
            raise ValueError("El campo de correo electrónico es obligatorio")
        
        email = self.normalize_email(email).lower()

        if self.model.objects.filter(email=email).exists():
            raise ValueError("Ya existe un usuario con este correo electrónico.")
        
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)  # Por defecto no es staff

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Crea y guarda un superusuario con el correo y contraseña proporcionados.
        """
        email = self.normalize_email(email).lower()
        extra_fields.setdefault('is_staff', True)  # Superusuario siempre es staff
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Superusuario siempre es admin

        if not extra_fields.get('is_staff'):
            raise ValueError("El superusuario debe tener is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
