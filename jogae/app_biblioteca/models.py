from django.db import models
from app_cadastro_usuario.models import User
from games.models import Game

# Create your models here.

class FavoriteGamesByUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games = models.ManyToManyField(Game, blank=True)