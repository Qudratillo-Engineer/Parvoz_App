from django.urls import path

from .views import LoginView, RegisterView, RedirectView
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LoginView.as_view(), name="logout"),
]