from .models import Friendship


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
