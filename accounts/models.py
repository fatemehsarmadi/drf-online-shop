from .managers import CustomUserManager
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [AbstractUser.username]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class Profile(models.Model):
    occupation = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255)
    street_number = models.CharField(max_length=10)
    flat_number = models.CharField(max_length=10, blank=True)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)