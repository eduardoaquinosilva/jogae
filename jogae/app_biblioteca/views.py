from django.shortcuts import render, get_object_or_404, redirect
from .models import FavoriteGamesByUser
from django.contrib.auth.decorators import login_required
from games.models import Game
from django.db.models import Avg, F
# Create your views here.

@login_required
def Biblioteca(request):
    
    # Coleta a lista de jogos favoritos
    try:
        user_favorites = FavoriteGamesByUser.objects.get(user=request.user)
        game_list = user_favorites.games.all()
    except FavoriteGamesByUser.DoesNotExist:
        game_list = Game.objects.none()

    # Coleta pesquisa de usuário e ordenação
    search_query = request.GET.get('q', '')
    ordering = request.GET.get('orderby', 'title') 

    # Filtra jogos da lista pela pesquisa
    if search_query:
        game_list = game_list.filter(title__icontains=search_query)

    # Ordena de acordo com o que foi solicitado
    if ordering == 'rating':
        game_list = game_list.annotate(avg_rating=Avg('ratings__rating')).order_by(F('avg_rating').desc(nulls_last=True))
    else:
        game_list = game_list.order_by('title')

    context = {
    'games': game_list,
    'search_query': search_query,
    }
    
    return render(request, 'biblioteca/biblioteca.html', context)

@login_required
def saveGame(request,pk):

    # Coleta jogo de acordo com a chave passada
    gameToAdd = get_object_or_404(Game, id=pk)

    # Coleta lista de jogos favoritos ou cria uma nova caso ainda não haja para aquele usuário
    userFavorites, created = FavoriteGamesByUser.objects.get_or_create(user=request.user)

    # Adiciona jogo a lista
    userFavorites.games.add(gameToAdd)

    return redirect('biblioteca:homeBiblioteca')