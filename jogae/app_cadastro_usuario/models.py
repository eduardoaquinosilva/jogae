from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    friends = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="followers")