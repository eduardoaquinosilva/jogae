
from django.db import models

# Create your models here.

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=100)
