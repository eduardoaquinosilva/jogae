from django.urls import path, include

from . import views

app_name="auth"
urlpatterns = [
    path('', include("django.contrib.auth.urls")),
    path('signup/', views.SignUpView.as_view(), name="signup")
]