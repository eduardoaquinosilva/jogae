from django.urls import path

from . import views

app_name = "games"
urlpatterns = [
    path("<uuid:pk>/", views.DetailView.as_view(), name="detail"),
]