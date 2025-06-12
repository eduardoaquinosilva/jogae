from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Game

class IndexView(generic.ListView):
    template_name = "games/index.html"
    context_object_name = "popular_games"

    def get_queryset(self):
        return Game.objects.order_by("rating")[:10]

class DetailView(generic.DetailView):
    model = Game
    template_name = "games/detail.html"


class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Game
    fields = [
        'title',
        'description',
        'picture'
    ]
    template_name = "games/create.html"