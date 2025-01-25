from collections.abc import Callable
from typing import Any

# django-stubs doesn't seem to have the LoginRequiredMiddleware type yet
from django.contrib.auth.middleware import LoginRequiredMiddleware  # type: ignore[attr-defined]
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from . import selectors


class FullyOnboardedUserRequiredMiddleware(LoginRequiredMiddleware):
    """
    By default, all views require the user to be fully onboarded. This middleware
    checks if the user is fully onboarded and redirects them to the appropriate
    onboarding step if they are not.
    """

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: tuple[Any, ...],
        view_kwargs: dict[str, Any],
    ) -> None | HttpResponse:
        if not getattr(view_func, "onboarding_required", True):
            return None

        if not request.user.is_authenticated:
            return redirect("account_login")

        if not selectors.user_has_mfa_enabled(user=request.user):
            return redirect("onboarding_mfa")

        if not selectors.user_has_valid_subscription(user=request.user):
            return redirect("onboarding_billing")

        if not selectors.user_has_verified_identity(user=request.user):
            return redirect("onboarding_identity")

        return None

    # If a user fails the onboarding checks don't bother recording where they were trying to go
    def get_redirect_field_name(self) -> None:
        return None
