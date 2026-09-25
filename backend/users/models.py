from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # En el futuro, añadir campos como:
    # organization = models.CharField(max_length=100, blank=True)
    pass