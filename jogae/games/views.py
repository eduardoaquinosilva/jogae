from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
<<<<<<< Updated upstream
from django.db.models import Avg, F
from django.shortcuts import redirect
=======
from django.shortcuts import render
>>>>>>> Stashed changes

from .models import Game
from .forms import GameForm, RatingForm

from .recommendation_utils import (
    get_content_based_recommendations,
    get_collaborative_recommendations,
    get_friend_based_recommendations
)

""" class IndexView(generic.ListView):
    template_name = "games/index.html"
    context_object_name = "popular_games"

    def get_queryset(self):
<<<<<<< Updated upstream
        return Game.objects.annotate(avg_rating=Avg('ratings__rating')).order_by("-avg_rating")[:10]
=======
        return Game.objects.order_by("rating")[:10] """

def indexView(request):
    user = request.user

    if not hasattr(user, 'favoritegamesbyuser') or not user.favoritegamesbyuser.games.exists():
        recommendations = Game.objects.order_by('-rating')[:10]
        return render(request, 'games/index.html', {'popular_games': recommendations})
    
    user_favorites = list(user.favoritegamesbyuser.games.all())
    all_games = list(Game.objects.all())

    content_recs = get_content_based_recommendations(user_favorites, all_games)
    collab_recs = get_collaborative_recommendations(user)
    friend_recs = get_friend_based_recommendations(user)

    combined_recs = friend_recs + collab_recs + content_recs

    final_recommendations = []
    seen_games = set(user_favorites)

    for game in combined_recs:
        if game not in seen_games and game not in final_recommendations:
            final_recommendations.append(game)
            seen_games.add(game)
    
    return render(request, 'games/index.html', {'popular_games': final_recommendations[:10]})
>>>>>>> Stashed changes


class DetailView(generic.DetailView):
    model = Game
    template_name = "games/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()

        ordering = self.request.GET.get('orderby', 'recentes') 

        if ordering == 'recentes':
            context['ratings'] = game.ratings.order_by('-created')

        if ordering == 'rating':
            context['ratings'] = game.ratings.order_by('-rating')

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
