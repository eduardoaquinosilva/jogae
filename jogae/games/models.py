import uuid
from django.urls import reverse
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    user = models.ForeignKey("app_cadastro_usuario.User", on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    rating = models.FloatField(
        validators = [MinValueValidator(0), MaxValueValidator(5)],
        default=2.5
    )
    picture = models.ImageField(upload_to="games/", null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def get_absolute_url(self):
        return reverse("games:detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.title
