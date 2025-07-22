from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

from django.db.models import Count, Q
from django.contrib.auth import get_user_model

from .models import Game, GameTFIDF
from app_profile.models import Friendship
from app_biblioteca.models import FavoriteGamesByUser

User = get_user_model()


def get_content_based_recommendations(user_favorite_games, num_recommendations=5, return_profile=False):
    
    # Verifica se possui lista de jogos favoritos
    if not user_favorite_games:
        return ([], None) if return_profile else []

    # Coleta dados da matriz TFIDF
    try:
        game_tfidf_data = GameTFIDF.objects.latest('created_at')
        tfidf_matrix = pickle.loads(game_tfidf_data.tfidf_matrix)
        game_index_map = game_tfidf_data.game_index_map
    except GameTFIDF.DoesNotExist:
        # Caso não tenha a matriz, retorna vazio necessário rodar
        # 'docker-compose exec web python manage.py setup_dev_data'
        return ([], None) if return_profile else []

    # Coleta ids dos jogos favoritos
    user_favorite_ids = {str(game.id) for game in user_favorite_games}
    # Verifica os jogos favoritos que estejam no dicionário de jogos de TFIDF
    user_game_indices = [game_index_map[gid] for gid in user_favorite_ids if gid in game_index_map]
    if not user_game_indices:
        return ([], None) if return_profile else []

    # Coleta gosto do usuário
    user_profile = np.asarray(tfidf_matrix[user_game_indices].mean(axis=0))

    # Algoritmo de similaridade de coseno entre o gosto do usuário e a matriz tfidf
    cosine_similarities = cosine_similarity(user_profile, tfidf_matrix)

    # Soma a quantidade de jogos necessários de recomendação com 
    # a quantidade de jogos favoritos para que tenha maior probabilidade
    # de coletar ao menos 'num_recommendations' recomendações válidas
    total_to_fetch = num_recommendations + len(user_favorite_games)
    
    # 'Ordena' retornando os índices dos jogos de menor -> maior similaridade 
    similar_indices = cosine_similarities.argsort().flatten()[-total_to_fetch:]

    # Matriz de jogos volta a forma de ids
    index_to_game_id_map = {v: k for k, v in game_index_map.items()}
    recommended_game_ids = []

    # Necessário reverter pois anteriormente foi 'ordenado' de menor -> maior
    for i in reversed(similar_indices):
        
        # coleta id do jogo
        game_id = index_to_game_id_map.get(i)

        # adiciona somente se o jogo não tiver nos jogos favoritos e 
        # ao chegar no limite máximo de recomendações para o loop
        if game_id and game_id not in user_favorite_ids:
            recommended_game_ids.append(game_id)
        if len(recommended_game_ids) >= num_recommendations:
            break
    
    # Coleta os objetos dos jogos pegos pelo ID
    games_map = {str(g.id): g for g in Game.objects.filter(pk__in=recommended_game_ids)}
    recommended_games = [games_map[gid] for gid in recommended_game_ids if gid in games_map]

    # Retorna os jogos e o gosto do usuário ou somente os jogos
    if return_profile:
        return recommended_games, user_profile
    else:
        return recommended_games


def get_friend_based_recommendations(user, num_recommendations=5):

    # Coleta amigos do usuário
    friends = Friendship.objects.get_friends(user)
    
    # Se não possuir amigo não há o que recomendar
    if not friends:
        return []

    # Coleta ids dos amigos
    friend_ids = [f.id for f in friends]

    # Coleta todos os jogos diferentes de todos os amigos
    friend_favorites = Game.objects.filter(savedInLibrary__user__in=friend_ids).distinct()
    
    # Exclui jogos que já estão favoritados pelo usuário
    user_favorite_ids = user.favoritegamesbyuser.games.values_list('id', flat=True)
    recommendations = friend_favorites.exclude(id__in=user_favorite_ids)

    # Retorna recomendações
    return list(recommendations[:num_recommendations])


def get_collaborative_recommendations(current_user, num_recommendations=5):

    # Verifica os jogos favoritos do usuário atual
    try: 
        current_user_favorite_ids = set(current_user.favoritegamesbyuser.games.values_list('id', flat=True))
        if not current_user_favorite_ids:
            return []
    except FavoriteGamesByUser.DoesNotExist:
        return []


    # Localiza usuários que possuem ao menos 1 jogo em comum com o usuário atual
    # ordenando pela quantidade de jogos em comum
    similar_users = User.objects.filter(
        favoritegamesbyuser__games__id__in=current_user_favorite_ids
    ).exclude(
        pk=current_user.pk
    ).annotate(
        common_games_count=Count('favoritegamesbyuser__games', filter=Q(favoritegamesbyuser__games__id__in=current_user_favorite_ids))
    ).order_by('-common_games_count')[:10]

    # se não localizou nenhum usuário com jogo similar retorna vazio
    if not similar_users:
        return []

    # coleta id dos usuários com jogos similares
    similar_user_ids = [user.id for user in similar_users]

    # Pega todos os jogos diferentes desses usuários, excluindo os jogos que já estão na lista de favoritos do usuário atual
    recommended_games = Game.objects.filter( 
        savedInLibrary__user__id__in=similar_user_ids
    ).exclude(
        id__in=current_user_favorite_ids
    ).distinct()

    return list(recommended_games[:num_recommendations])


def get_content_based_rating(user, num_recommendations=5, return_profile=False):

    # Coleta dados da matriz TFIDF
    try:
        game_tfidf_data = GameTFIDF.objects.latest('created_at')
        tfidf_matrix = pickle.loads(game_tfidf_data.tfidf_matrix)
        game_index_map = game_tfidf_data.game_index_map
    except GameTFIDF.DoesNotExist:
        # Caso não tenha a matriz, retorna vazio necessário rodar
        # 'docker-compose exec web python manage.py setup_dev_data'
        return ([], None) if return_profile else []
    
    # Coleta as maiores notas dadas pelo usuário (acima de 4.5) e pré carrega os dados do jogo
    high_ratings = user.ratings.filter(rating__gte=4.5).select_related('game')
    if not high_ratings:
        return ([], None) if return_profile else []

    # Coleta indices dos jogos com melhor nota dada pelo usuário
    user_game_ids = {str(rating.game.id) for rating in high_ratings}
    user_game_indices = [game_index_map[gid] for gid in user_game_ids if gid in game_index_map]

    if not user_game_indices:
       return ([], None) if return_profile else []

    # Coleta gosto do usuário
    user_profile = np.asarray(tfidf_matrix[user_game_indices].mean(axis=0))
    
    # Exclui jogos que o usuário já favoritou
    try:
        user_favorite_ids = set(str(g.id) for g in user.favoritegamesbyuser.games.all())
    except FavoriteGamesByUser.DoesNotExist:
        user_favorite_ids = set()


    # Algoritmo de similaridade de coseno entre o gosto do usuário e a matriz tfidf
    cosine_similarities = cosine_similarity(user_profile, tfidf_matrix)

    # Soma a quantidade de jogos necessários de recomendação com 
    # a quantidade de jogos favoritos e já com nota dada 
    # para que tenha maior probabilidade de coletar ao menos 
    # 'num_recommendations' recomendações válidas
    excluded_ids = user_favorite_ids.union(user_game_ids)
    total_to_fetch = num_recommendations + len(excluded_ids)

    # 'Ordena' retornando os índices dos jogos de menor -> maior similaridade 
    similar_indices = cosine_similarities.argsort().flatten()[-total_to_fetch:]


    # Matriz de jogos volta a forma de ids
    index_to_game_id_map = {v: k for k, v in game_index_map.items()}
    recommended_game_ids = []

    # Necessário reverter pois anteriormente foi 'ordenado' de menor -> maior
    for i in reversed(similar_indices):

        # coleta id do jogo
        game_id = index_to_game_id_map.get(i)

        # adiciona somente se o jogo não tiver nos jogos favoritos e 
        # ao chegar no limite máximo de recomendações para o loop
        if game_id and game_id not in excluded_ids:
            recommended_game_ids.append(game_id)
        if len(recommended_game_ids) >= num_recommendations:
            break
    

    # Coleta os objetos dos jogos pegos pelo ID
    games_map = {str(g.id): g for g in Game.objects.filter(pk__in=recommended_game_ids)}
    recommended_games = [games_map[gid] for gid in recommended_game_ids if gid in games_map]

    # Retorna os jogos e o gosto do usuário ou somente os jogos
    if return_profile:
        return recommended_games, user_profile
    else:
        return recommended_games
    

def filter_by_similarity(user_profile, games, num_recommendations=10):

    # Se não foi passado jogo ou não possui o gosto do usuário
    # retorna vazio
    if user_profile is None or not games:
        return [(game, None) for game in games[:num_recommendations]]

    # Coleta dados da matriz TFIDF
    try:
        game_tfidf_data = GameTFIDF.objects.latest('created_at')
        tfidf_matrix = pickle.loads(game_tfidf_data.tfidf_matrix)
        game_index_map = game_tfidf_data.game_index_map
    except GameTFIDF.DoesNotExist:
        # Sem matriz não é possível ordenar por similaridade, retorna a lista
        # truncada com a quantidade de dados passados
        return [(game, None) for game in games[:num_recommendations]]

    # Pega os ids dos jogos considerados na matriz de jogos
    game_ids_in_list = {str(g.id) for g in games}
    game_indices = [game_index_map[gid] for gid in game_ids_in_list if gid in game_index_map]
    if not game_indices:
        return []

    # Coleta a posição do jogo na matriz TF-IDF
    index_to_game_map = {game_index_map[str(g.id)]: g for g in games if str(g.id) in game_index_map}

    # Filtra a matriz TFIDF somente com os jogos que serão
    # verificado seu índice de similaridade
    filtered_tfidf_matrix = tfidf_matrix[game_indices]

    # Calcula índice de similaridade somente com os jogos de interesse
    cosine_similarities = cosine_similarity(user_profile, filtered_tfidf_matrix)
    scores = cosine_similarities[0]

    # 'Ordena' retornando os índices dos jogos de menor -> maior similaridade
    sorted_local_indices = cosine_similarities.argsort().flatten()[::-1]

    # Coleta indices e adiciona os objetos do jogo e o score dele a 'sorted_games_with_scores' para retornar 
    sorted_games_with_scores = []
    for local_idx in sorted_local_indices:
        global_matrix_idx = game_indices[local_idx]
        game = index_to_game_map[global_matrix_idx]
        score = scores[local_idx]
        sorted_games_with_scores.append((game, score))

    return sorted_games_with_scores[:num_recommendations]