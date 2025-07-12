from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app_cadastro_usuario.forms import UserChangeForm
from games.models import Game


# Create your views here.

@login_required
def Profile(request):

    context = { 'user' : request.user}

    return render(request, 'profile/profile.html', context)

@login_required
def MyGames(request):
    
    games = Game.objects.filter(user=request.user)

    context = {'games' : games}

    return render(request, 'profile/myGames.html', context)

@login_required
def Friends(request):
    
    #following = request.user.friends.all()

    friends = request.user.followers.all()

    #context = {'following' : following, 'friends' : friends}

    context = {'friends' : friends}

    return render(request, 'profile/friends.html', context)

@login_required
def EditProfile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('profile:profile')
    else:
        form = UserChangeForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'profile/editProfile.html', context)