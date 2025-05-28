import uuid
from django.urls import reverse
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    rating = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        default=2.5
    )
    picture = models.ImageField(upload_to="games/", null=True, blank=True)

    def get_absolute_url(self):
        return reverse("games:detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.title