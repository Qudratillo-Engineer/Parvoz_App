from django.urls import path

from .views import AccessDeniedView, LoginView, RegisterView, RedirectView, Logout
urlpatterns = [
    path("access-denied/", AccessDeniedView.as_view(), name="access_denied"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", Logout.as_view(), name="logout"),
]
