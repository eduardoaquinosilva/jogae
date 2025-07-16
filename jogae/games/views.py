from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, F
from django.shortcuts import redirect, render

from .models import Game
from .forms import GameForm, RatingForm

from .recommendation_utils import (
    get_content_based_recommendations,
    get_collaborative_recommendations,
    get_friend_based_recommendations,
    get_content_based_rating
)

""" class IndexView(generic.ListView):
    template_name = "games/index.html"
    context_object_name = "popular_games"

    def get_queryset(self):
        return Game.objects.annotate(avg_rating=Avg('ratings__rating')).order_by("-avg_rating")[:10]
        return Game.objects.order_by("rating")[:10] """

def indexView(request):
    user = request.user
    search_query = request.GET.get('q', '')
    sort_param = request.GET.get('orderby', None)
    
    games_to_display = None

    if search_query:

        games_to_display = Game.objects.filter(title__icontains=search_query)
    
    else:

        if not hasattr(user, 'favoritegamesbyuser') or not user.favoritegamesbyuser.games.exists():

            games_to_display = Game.objects.annotate(avg_rating=Avg('ratings__rating')).order_by("-avg_rating")
        else:

            user_favorites = list(user.favoritegamesbyuser.games.all())
            all_games_list = list(Game.objects.all())
            
            content_recs = get_content_based_recommendations(user_favorites, all_games_list)
            collab_recs = get_collaborative_recommendations(user)
            friend_recs = get_friend_based_recommendations(user)
            
            combined_recs = content_recs + friend_recs + collab_recs
            
            final_recommendations = []
            seen_pks = {game.pk for game in user_favorites}

            for game in combined_recs:
                if game.pk not in seen_pks:
                    final_recommendations.append(game)
                    seen_pks.add(game.pk)
            
            games_to_display = final_recommendations

    if sort_param:
        if isinstance(games_to_display, list):
            
            if sort_param == 'title':
                games_to_display = sorted(games_to_display, key=lambda game: game.title)
            elif sort_param == 'rating':
                
                game_ids = [game.id for game in games_to_display]
                
                games_with_ratings = Game.objects.filter(pk__in=game_ids).annotate(
                    avg_rating=Avg('ratings__rating')
                ).order_by('-avg_rating')
                games_to_display = list(games_with_ratings)

        else:
            if sort_param == 'title':
                games_to_display = games_to_display.order_by('title')
            elif sort_param == 'rating':
                games_to_display = games_to_display.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')

    if not isinstance(games_to_display, list):
        final_list = games_to_display[:10]
    else:
        final_list = games_to_display[:10]

    context = {
        'popular_games': final_list,
        'search_query': search_query,
    }
    
    return render(request, 'games/index.html', context)


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
