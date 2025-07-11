from django.urls import path

from . import views

app_name = "profile"
urlpatterns = [
    path("", views.Profile, name="profile"),
    path("myGames/", views.MyGames, name="myGames"),
    path("editProfile/", views.EditProfile, name="editProfile"),
    path("friends/", views.Friends, name="friends"),
]

