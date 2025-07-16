from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

from collections import defaultdict

from .models import Game
from app_profile.models import Friendship
from app_biblioteca.models import FavoriteGamesByUser


def get_content_based_recommendations(user_favorite_games, all_games, num_recommendations=5):
    if not user_favorite_games:
        return []

    # Importa aqui para evitar circular imports
    from .models import GameTFIDF 

    # Tenta coletar o TFIDF pré-calculado
    try:
        game_tfidf_data = GameTFIDF.objects.latest('created_at')
        tfidf_matrix = pickle.loads(game_tfidf_data.tfidf_matrix)
        game_index_map = game_tfidf_data.game_index_map

        # Verifica se foi adicionado algum jogo novo
        if not all(game.id in game_index_map for game in all_games):
            raise GameTFIDF.DoesNotExist  # Caso tenha localizado jogo novo é necessário recalcular
    except GameTFIDF.DoesNotExist:
        # Se não existir (primeira geração) ou for necessário recalcular

        # Apaga os vetores anteriores
        GameTFIDF.objects.all().delete()

        game_content = []
        for game in all_games:
            genres = ' '.join([genre.name for genre in game.genres.all()])
            tags = ' '.join([tag.name for tag in game.tags.all()])
            content = f"{game.title} {game.description} {genres} {tags}"
            game_content.append(content)

        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(game_content)

        # Cria o mapa de indices de jogos
        game_index_map = {str(game.id): i for i, game in enumerate(all_games)}

        # Salva a matriz
        GameTFIDF.objects.create(
            tfidf_matrix=pickle.dumps(tfidf_matrix),
            game_index_map=game_index_map,
        )

    # Converte os jogos favoritos do usuário para a posição na matriz
    user_game_indices = [game_index_map[game.id] for game in user_favorite_games if game.id in game_index_map]
    if not user_game_indices:  
        return []

    user_profile = np.asarray(tfidf_matrix[user_game_indices].mean(axis=0))

    cosine_similarities = cosine_similarity(user_profile, tfidf_matrix)

    similar_indices = cosine_similarities.argsort().flatten()[-num_recommendations-len(user_favorite_games):-1]

    recommended_games = []
    for i in reversed(similar_indices):
        if all_games[i] not in user_favorite_games:
            recommended_games.append(all_games[i])
        if len(recommended_games) == num_recommendations:
            break
    
    return recommended_games


def get_friend_based_recommendations(user, num_recommendations=5):
    friends = Friendship.objects.get_friends(user)
    if not friends:
        return []

    friend_favorites = set()
    for friend in friends:
        if hasattr(friend, 'favoritegamesbyuser'):
            friend_favorites.update(friend.favoritegamesbyuser.games.all())

    user_favorites = set(user.favoritegamesbyuser.games.all())
    recommendations = list(friend_favorites - user_favorites)

    return list(recommendations)[:num_recommendations]


def get_collaborative_recommendations(current_user, num_recommendationn=5):
    similar_users = defaultdict(int)
    current_user_favorites = set(current_user.favoritegamesbyuser.games.all())

    for favorite in FavoriteGamesByUser.objects.exclude(user=current_user):
        other_user_favorites = set(favorite.games.all())
        common_games = current_user_favorites.intersection(other_user_favorites)
        if common_games:
            similar_users[favorite.user] += len(common_games)
    
    recommendations = set()
    sorted_similar_users = sorted(similar_users.items(), key=lambda item: item[1], reverse=True)

    for user, _ in sorted_similar_users:
        user_favorites = set(user.favoritegamesbyuser.games.all())
        new_recommendations = user_favorites - current_user_favorites
        recommendations.update(new_recommendations)
        if len(recommendations) >= num_recommendationn:
            break
    
    return list(recommendations)[:num_recommendationn]


def get_content_based_rating(user, all_games, num_recommendations=5, return_profile=False):

    # Importa aqui para evitar circular imports
    from .models import GameTFIDF

    # Tenta coletar o TFIDF pré-calculado
    try:
        game_tfidf_data = GameTFIDF.objects.latest('created_at')
        tfidf_matrix = pickle.loads(game_tfidf_data.tfidf_matrix)
        game_index_map = game_tfidf_data.game_index_map

        # Verifica se foi adicionado algum jogo novo
        if not all(game.id in game_index_map for game in all_games):
            raise GameTFIDF.DoesNotExist  # Caso tenha localizado jogo novo é necessário recalcular
    except GameTFIDF.DoesNotExist:
        # Se não existir (primeira geração) ou for necessário recalcular

        # Apaga os vetores anteriores
        GameTFIDF.objects.all().delete()

        game_content = []
        for game in all_games:
            genres = ' '.join([genre.name for genre in game.genres.all()])
            tags = ' '.join([tag.name for tag in game.tags.all()])
            content = f"{game.title} {game.description} {genres} {tags}"
            game_content.append(content)

        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(game_content)

        # Cria o mapa de indices de jogos
        game_index_map = {str(game.id): i for i, game in enumerate(all_games)}

        # Salva a matriz
        GameTFIDF.objects.create(
            tfidf_matrix=pickle.dumps(tfidf_matrix),
            game_index_map=game_index_map,
        )

    # Coleta os indices dos jogos com maior nota dada pelo usuário
    user_game_indices = [
        game_index_map.get(rating.game.id)
        for rating in user.ratings.all()
        if rating.game.average_rating() > 4.5 and rating.game.id in game_index_map
    ]
    if not user_game_indices:
        return [], None

    user_profile = np.asarray(tfidf_matrix[user_game_indices].mean(axis=0)) if user_game_indices else np.zeros((1, tfidf_matrix.shape[1]))

    cosine_similarities = cosine_similarity(user_profile, tfidf_matrix)

    user_favorites = set(user.favoritegamesbyuser.games.all())

    similar_indices = cosine_similarities.argsort().flatten()[-num_recommendations-len(user_favorites):-1]

    recommended_games = []
    for i in reversed(similar_indices):
        
        if all_games[i] not in user_favorites:
            recommended_games.append(all_games[i])
        if len(recommended_games) == num_recommendations:
            break
    
    if return_profile:
        return recommended_games, user_profile
    else:
        return recommended_games
    

def filter_by_similarity(user_profile, games, num_recommendations=10):
    
    # Importa aqui para evitar circular import
    from .models import GameTFIDF

    try:
        # Tenta pegar o último TDFIDF gerado
        game_tfidf_data = GameTFIDF.objects.latest('created_at')
        tfidf_matrix = pickle.loads(game_tfidf_data.tfidf_matrix)
        game_index_map = game_tfidf_data.game_index_map

        # Mapeia os índices dos jogos
        game_indices = [game_index_map[str(game.id)] for game in games if str(game.id) in game_index_map]
        if not game_indices:
            return []
    except GameTFIDF.DoesNotExist:
        # Caso não exista somente retorna os primeiros num_recommendations elementos de games
        return games[:num_recommendations]

    # Filtra a matrix para usar somente os jogos que estão sendo considerados
    filtered_tfidf_matrix = tfidf_matrix[game_indices]

    # Calcula a similaridade por coseno entre o gosto do usuário e o conteúdo dos jogos
    cosine_similarities = cosine_similarity(user_profile, filtered_tfidf_matrix)

    # Os jogos são separados de acordo com a similaridade 
    similar_indices = cosine_similarities.argsort().flatten()[::-1]

    # Retorna o map para a ordem original
    games_by_similarity = [games[game_indices.index(game_index_map[str(games[i].id)])] for i in similar_indices if str(games[i].id) in game_index_map]

    return games_by_similarity[:num_recommendations]