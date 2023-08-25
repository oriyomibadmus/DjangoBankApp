from django.urls import path
from userauth import views

app_name = "userauth"

urlpatterns = [
    path("register/", views.RegisterView, name='register'),
    path("login/", views.LoginView, name="login"),
    path("logout/", views.LogoutView, name="logout"),
]