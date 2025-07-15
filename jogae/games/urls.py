from django.urls import path

from . import views

app_name = "games"
urlpatterns = [
    path("", views.indexView, name="index"),
    path("create/", views.CreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.DetailView.as_view(), name="detail"),
]