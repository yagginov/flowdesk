from django.urls import path, include

from accounts.views import (
    SignUpView,
    ActivateAccountView,
    PreLogoutView,
    UserDetailView,
    UserUpdateView,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
)

app_name = "accounts"

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("signup/", SignUpView.as_view(), name="sign-up"),
    path("user/update/", UserUpdateView.as_view(), name="user-update"),
    path(
        "password/change/", CustomPasswordChangeView.as_view(), name="password-change"
    ),
    path(
        "password/change/done/",
        CustomPasswordChangeDoneView.as_view(),
        name="password-change-done",
    ),
    path("pre-logout/", PreLogoutView.as_view(), name="pre-logout"),
    path(
        "activate/<str:uid>/<str:token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
