from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserAccountManager(BaseUserManager): #custom
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email')
        if not password:
            raise ValueError('Password is required')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email')
        if not password:
            raise ValueError('Password is required')

        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user        

class UserAccount(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserAccountManager()

    def get_full_name(self):
        return self.name + " "+ self.surname
    
    def __str__(self):
        return self.get_full_name()
