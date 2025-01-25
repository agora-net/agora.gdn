from allauth.account import views as aa_views


class OnboardingNotRequiredMixin:
    """Means that the user does not need to be fully onboarded to access the view."""

    onboarding_required = False


# We subclass the all auth views because we're using a non-standard middleware to enforce onboarding


class LoginView(aa_views.LoginView, OnboardingNotRequiredMixin):
    pass


class SignupView(aa_views.SignupView, OnboardingNotRequiredMixin):
    pass


class SignupByPasskeyView(aa_views.SignupByPasskeyView, OnboardingNotRequiredMixin):
    pass


class ConfirmEmailView(aa_views.ConfirmEmailView, OnboardingNotRequiredMixin):
    pass


class PasswordResetView(aa_views.PasswordResetView, OnboardingNotRequiredMixin):
    pass


class PasswordResetDoneView(aa_views.PasswordResetDoneView, OnboardingNotRequiredMixin):
    pass


class PasswordResetFromKeyView(aa_views.PasswordResetFromKeyView, OnboardingNotRequiredMixin):
    pass


class PasswordResetFromKeyDoneView(
    aa_views.PasswordResetFromKeyDoneView, OnboardingNotRequiredMixin
):
    pass


class LogoutView(aa_views.LogoutView, OnboardingNotRequiredMixin):
    pass


class AccountInactiveView(aa_views.AccountInactiveView, OnboardingNotRequiredMixin):
    pass


class ConfirmEmailVerificationCodeView(
    aa_views.ConfirmEmailVerificationCodeView, OnboardingNotRequiredMixin
):
    pass
