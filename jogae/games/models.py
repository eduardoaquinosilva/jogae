import uuid
from django.urls import reverse
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

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
    picture = models.ImageField(upload_to="games/", null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def get_absolute_url(self):
        return reverse("games:detail", kwargs={"pk": self.id})

    def average_rating(self):
        return self.ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    def __str__(self):
        return self.title

class Rating(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey("app_cadastro_usuario.User", on_delete=models.CASCADE, related_name='ratings')
    body = models.TextField(blank=True)
    rating = models.FloatField(
        validators = [MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]


class GameTFIDF(models.Model):
    tfidf_matrix = models.BinaryField()  
    game_index_map = models.JSONField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TF-IDF Matrix (Created: {self.created_at})"
