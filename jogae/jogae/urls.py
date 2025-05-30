from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app_cadastro_usuario import views
from games.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('cadastro_usuario/', views.registrar_usuario, name='registrar_usuario'),
    path('cadastro_usuario/pagina_sucesso/', views.pagina_sucesso, name='pagina_sucesso'),
    path('login/', views.login_view, name='login'),
    path('', IndexView.as_view(), name='home'),
    path('games/', include("games.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)