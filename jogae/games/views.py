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
    get_content_based_rating,
    filter_by_similarity
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
    
    # games_queryset para quando possui algum dado de busca ou ordenação
    games_queryset = None
    # games_list_with_scores para coletar os jogos recomendados e seu score de similaridade
    games_list_with_scores = []

    # se possuir alguma busca coleta jogos que atingem o item buscado
    if search_query:
        games_queryset = Game.objects.filter(title__icontains=search_query)
    else:
        # Caso não possuir busca efetua processo de recomendação
        
        # View padrão, para usuários que não estão autentificados ou não possuem jogos favoritos 
        if not user.is_authenticated or not hasattr(user, 'favoritegamesbyuser') or not user.favoritegamesbyuser.games.exists():
            games_queryset = Game.objects.annotate(avg_rating=Avg('ratings__rating')).order_by("-avg_rating")
        else:
            # View personalizada para aqueles que estão logados e possuem jogos favoritos
            user_favorites = list(user.favoritegamesbyuser.games.all())

            # Coleta as recomendações baseada em:
            # conteúdo comparado com os jogos favoritos | coletando também o gosto do usuário
            content_recs, user_profile = get_content_based_recommendations(user_favorites, return_profile=True)
            # usuários com gostos similares
            collab_recs = get_collaborative_recommendations(user)
            # amigos
            friend_recs = get_friend_based_recommendations(user)
            # conteúdo dos jogos com maiores ratings 
            rating_recs = get_content_based_rating(user, num_recommendations=5, return_profile=False)
            
            # Combina as recomendações
            combined_recs = rating_recs + content_recs + friend_recs + collab_recs

            final_recommendations = []
            # Coleta jogos que estejam nos jogos favoritos do usuário
            seen_pks = {game.pk for game in user_favorites}

            # Adiciona jogos a lista final que não estejam na lista de favoritos 
            for game in combined_recs:
                if game.pk not in seen_pks:
                    final_recommendations.append(game)
                    seen_pks.add(game.pk)


            # Se foi coletado o perfil do usuário filtra dentre todos os jogos que foram coletados recomendados
            # os 10 que possuem a maior similaridade com o gosto do usuário
            if user_profile is not None:
                # retorna uma tupla de (jogo, score de similaridade)
                games_list_with_scores = filter_by_similarity(user_profile, final_recommendations, num_recommendations=len(final_recommendations))
            else:
                # Se não possui o gosto do usuário retorna uma tupla de (jogos, score nulo)
                games_list_with_scores = [(game, None) for game in final_recommendations]

            # Se ainda não tiver os 10 jogos, completa com jogos populares
            if len(games_list_with_scores) < 10:
                needed = 10 - len(games_list_with_scores)
                # coleta jogos que foram colocados na lista dos mais recomendados
                current_pks = {game.pk for game, score in games_list_with_scores}
                seen_pks.update(current_pks)
                # pega os melhores jogos por rating e retira os jogos que ja foram colocados
                filler_games = Game.objects.annotate(
                    avg_rating=Avg('ratings__rating')
                ).exclude(pk__in=seen_pks).order_by('-avg_rating')[:needed]
                games_list_with_scores.extend([(game, None) for game in filler_games])

    # Aplica os parâmetros de organização
    if sort_param:
        if games_queryset is not None:
            if sort_param == 'title':
                games_queryset = games_queryset.order_by('title')
            elif sort_param == 'rating':
                games_queryset = games_queryset.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
        else:
            if sort_param == 'title':
                games_list_with_scores = sorted(games_list_with_scores, key=lambda item: item[0].title)
            elif sort_param == 'rating':

                # dicionário de jogos
                score_map = {game.id: score for game, score in games_list_with_scores}
                # coletando somente os ids dos jogos
                game_ids = list(score_map.keys())
                # fazendo uma filtragem pelos jogos mais bem avaliados 
                games_with_ratings = Game.objects.filter(pk__in=game_ids).annotate(
                    avg_rating=Avg('ratings__rating')
                ).order_by('-avg_rating')
                # Recolocando jogos na nova ordem
                games_list_with_scores = [(game, score_map.get(game.id)) for game in games_with_ratings]

    # Preparando o contexto
    if games_queryset is not None:
        final_list = [(game, None) for game in games_queryset[:10]]
    else:
        final_list = games_list_with_scores[:10]

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
