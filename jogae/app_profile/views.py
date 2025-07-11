from django.shortcuts import render

# Create your views here.

def Profile(request):

    context = {}

    return render(request, 'profile/profile.html', context)

def MyGames(request):
    
    context = {}

    return render(request, 'profile/myGames.html', context)

def Friends(request):
    
    context = {}

    return render(request, 'profile/friends.html', context)

def EditProfile(request):
    
    context = {}

    return render(request, 'profile/editProfile.html', context)