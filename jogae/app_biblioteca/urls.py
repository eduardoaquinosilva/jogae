from django.urls import path
from . import views

app_name = "biblioteca"
urlpatterns = [
    path('', views.Biblioteca, name='homeBiblioteca'),
    path('saveGame/<uuid:pk>', views.saveGame, name='saveGame'),
]