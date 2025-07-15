from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from collections import defaultdict

from .models import Game
from app_profile.models import Friendship
from app_biblioteca.models import FavoriteGamesByUser


def get_content_based_recommendations(user_favorite_games, all_games, num_recommendations=5):
    if not user_favorite_games:
        return []
    
    game_content = []
    for game in all_games:
        genres = ' '.join([genre.name for genre in game.genres.all()])
        tags = ' '.join([tag.name for tag in game.tags.all()])
        content = f"{game.title} {game.description} {genres} {tags}"
        game_content.append(content)
    
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(game_content)

    user_game_indices = [list(all_games).index(game) for game in user_favorite_games]

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
