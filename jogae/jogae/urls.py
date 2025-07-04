from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from games.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('cadastro_usuario/', include('app_cadastro_usuario.urls')),
    path('', IndexView.as_view(), name='home'),
    path('games/', include("games.urls")),
    path('accounts/', include("app_cadastro_usuario.urls")),
    path('biblioteca/', include("app_biblioteca.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)