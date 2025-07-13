from django.urls import path

from . import views

app_name = "profile"
urlpatterns = [
    path("editProfile/", views.EditProfile, name="editProfile"),
    path("friends/", views.Friends, name="friends"),
    path("solicitacoes/", views.Solicitacoes, name="solicitacoes"),
    path("<str:pk>/addFriend/", views.AddFriend, name="addFriend"),
    path("<str:pk>/games/", views.games, name="games"),
    path("<str:pk>/", views.Profile, name="profile"),
]

