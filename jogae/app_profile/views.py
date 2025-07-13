from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from app_cadastro_usuario.forms import UserChangeForm
from django.db.models import Q
from .models import Friendship
from games.models import Game

User = get_user_model()

# Create your views here.

@login_required
def Profile(request,pk):

    user = get_object_or_404(User, username=pk)

    friendship_status = None
    if user != request.user:
        friendship = Friendship.objects.filter(
            (Q(from_user=request.user, to_user=user) | Q(from_user=user, to_user=request.user))
        ).first()

        if not friendship or friendship.status == Friendship.Status.DECLINED:
            friendship_status = 'NOT_FRIENDS'
        elif friendship.status == Friendship.Status.PENDING:
            friendship_status = 'PENDING'
        elif friendship.status == Friendship.Status.ACCEPTED:
            friendship_status = 'FRIENDS'

    context = { 
        'user' : user,
        'friendship_status': friendship_status
    }

    return render(request, 'profile/profile.html', context)

@login_required
def games(request,pk):
    
    user = get_object_or_404(User,username=pk)

    games = Game.objects.filter(user=user)

    context = {'games' : games}

    return render(request, 'profile/games.html', context)

@login_required
def Friends(request):
    # Use the manager to get a list of friend user objects
    friends = Friendship.objects.get_friends(request.user)

    # Get pending requests sent to the current user for them to accept/decline
    pending_requests = Friendship.objects.filter(to_user=request.user, status=Friendship.Status.PENDING)

    context = {
        'friends': friends,
        'pending_requests': pending_requests
    }

    return render(request, 'profile/friends.html', context)

@login_required
def EditProfile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('profile:profile', pk=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'profile/editProfile.html', context)

@login_required
def AddFriend(request, pk):

    to_user = get_object_or_404(User, username=pk)
    from_user = request.user

    if to_user == from_user:
        messages.error(request, "Você não pode adicionar a si mesmo como amigo.")
        return redirect('profile:profile', pk=to_user.username)

    
    existing_friendship = Friendship.objects.filter(
        (Q(from_user=from_user, to_user=to_user) | Q(from_user=to_user, to_user=from_user))
    ).first()

    if not existing_friendship:
        Friendship.objects.create(from_user=from_user, to_user=to_user)
        messages.success(request, f"Pedido de amizade enviado para {to_user.username}.")
    elif existing_friendship.status == Friendship.Status.DECLINED:
        # Se tiver sido recusado, pode ser feito novas tentativas de solicitação de amizade
        existing_friendship.from_user = from_user
        existing_friendship.to_user = to_user
        existing_friendship.status = Friendship.Status.PENDING
        existing_friendship.save()
        messages.success(request, f"Pedido de amizade enviado para {to_user.username}.")
    elif existing_friendship.status == Friendship.Status.PENDING:
        messages.info(request, f"Um pedido de amizade para {to_user.username} já está pendente.")
    elif existing_friendship.status == Friendship.Status.ACCEPTED:
        messages.info(request, f"Você já é amigo de {to_user.username}.")
    
    return redirect('profile:profile', pk=to_user.username)

@login_required
def Solicitacoes(request):
    user = request.user

    if request.method == 'POST':
        solicitacao_id = request.POST.get('solicitacao_id')
        # Ensure the request is for the logged-in user to prevent others from acting on their behalf
        friend_request = get_object_or_404(Friendship, id=solicitacao_id, to_user=user)

        if 'accept' in request.POST:
            friend_request.status = Friendship.Status.ACCEPTED
            friend_request.save()
            messages.success(request, f"Você e {friend_request.from_user.username} agora são amigos.")
        elif 'reject' in request.POST:
            friend_request.status = Friendship.Status.DECLINED
            friend_request.save()
            messages.info(request, f"Você rejeitou o pedido de amizade de {friend_request.from_user.username}.")
        
        return redirect('profile:solicitacoes')

    pending_requests = Friendship.objects.filter(to_user=user, status=Friendship.Status.PENDING)

    context = {
        'pending_requests': pending_requests
    }

    return render(request, 'profile/solicitacoes.html', context)