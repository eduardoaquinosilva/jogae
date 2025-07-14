from collections import defaultdict
from .models import FavoriteGamesByUser


def get_collaborative_recommendation(current_user, num_recommendationn=5):
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
