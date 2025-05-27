from django.contrib import admin
from django.urls import path, include
from app_cadastro_usuario import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('cadastro_usuario/', views.registrar_usuario, name='registrar_usuario'),
    path('cadastro_usuario/pagina_sucesso', views.pagina_sucesso, name='pagina_sucesso'),
    path('games/', include("games.urls"))
]
