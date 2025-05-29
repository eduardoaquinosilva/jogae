from django.contrib import admin
from django.urls import path, include

app_name="auth"
urlpatterns = [
    path('', include("django.contrib.auth.urls")),
]