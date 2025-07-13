from .models import Friendship

def friends_list(request):
    """
    Makes the user's friends list available in the context of all templates.
    """
    if request.user.is_authenticated:
        friends = Friendship.objects.get_friends(request.user)
        return {'friends_for_sidebar': friends}
    return {}