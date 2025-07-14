from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.shortcuts import redirect

from .models import Game
from .forms import GameForm, RatingForm

class IndexView(generic.ListView):
    template_name = "games/index.html"
    context_object_name = "popular_games"

    def get_queryset(self):
        return Game.objects.annotate(avg_rating=Avg('ratings__rating')).order_by("-avg_rating")[:10]


class DetailView(generic.DetailView):
    model = Game
    template_name = "games/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        context['ratings'] = game.ratings.order_by('-created')
        if self.request.user.is_authenticated:
            context['rating_form'] = RatingForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        form = RatingForm(request.POST)
        
        if form.is_valid():
            rating = form.save(commit=False)
            rating.game = self.object
            rating.user = request.user
            rating.save()
            return redirect(self.object.get_absolute_url())
        else:
            context = self.get_context_data()
            context['rating_form'] = form
            return self.render_to_response(context)

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
