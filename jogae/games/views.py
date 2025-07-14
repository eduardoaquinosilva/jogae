from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Game
from .forms import GameForm

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
    """ fields = [
        'title',
        'description',
        'picture',
        'genres',
        'tags'
    ] """
    form_class = GameForm
    template_name = "games/create.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
