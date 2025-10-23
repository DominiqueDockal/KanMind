from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    """
    Custom manager for the User model, handling user and superuser creation.
    """

    def create_user(self, email, fullname, password=None, **extra_fields):
        """
        Create and save a User with the given email, fullname, and password.

        Args:
            email (str): The user's email address.
            fullname (str): The user's full name.
            password (str): The user's password.
            extra_fields (dict): Additional fields for the user.

        Returns:
            User: The created User instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, fullname=fullname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, fullname, and password.

        Sets is_staff and is_superuser flags to True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, fullname, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the application.
    
    Fields:
        email (str): Unique user email (used for login).
        fullname (str): Full name of the user.
        is_active (bool): User activation status.
        is_staff (bool): Staff/admin status.

    Authentication:
        USERNAME_FIELD is 'email'
        REQUIRED_FIELDS is ['fullname']

    Uses CustomUserManager for creation.
    """

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]
    objects = CustomUserManager()

