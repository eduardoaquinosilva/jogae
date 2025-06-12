from django.urls import path
from . import views


urlpatterns = [
    path('', views.registrar_usuario, name='registrar_usuario'),
    path('pagina_sucesso/', views.pagina_sucesso, name='pagina_sucesso'),
]