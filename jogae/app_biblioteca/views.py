from django.shortcuts import render
from .models import FavoriteGamesByUser
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def Biblioteca(request):
    favorites = FavoriteGamesByUser.objects.get(user=request.user)
    context = {'favorites' : favorites}
    return render(request, 'biblioteca/biblioteca.html', context)