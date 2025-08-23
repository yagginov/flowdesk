from django.urls import path, include

from accounts.views import SignUpView, ActivateAccountView, PreLogoutView

app_name = "accounts"

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("signup/", SignUpView.as_view(), name="sign-up"),
    path("pre-logout/", PreLogoutView.as_view(), name="pre-logout"),
    path(
        "activate/<str:uid>/<str:token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
]
