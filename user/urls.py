from django.urls import include, path

from . import views

url_patterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("inactive/", views.AccountInactiveView.as_view(), name="inactive"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    # path("reauthenticate/", name="account_reauthenticate"),
    path(
        "onboarding/",
        include(
            [
                path("confirm-email/", views.ConfirmEmailView.as_view(), name="confirm_email"),
                # path("mfa/", name="onboarding_mfa"),
                # path("billing/", name="onboarding_billing"),
                # path("identity/", name="onboarding_identity"),
            ]
        ),
    ),
]
