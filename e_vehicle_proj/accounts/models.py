from django.contrib.auth.models import AbstractUser
from django.db import models

class AppUser(AbstractUser):
    balance = models.DecimalField(default = 0, max_digits = 10, decimal_places = 2)
