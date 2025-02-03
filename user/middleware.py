from collections.abc import Callable
from typing import Any

# django-stubs doesn't seem to have the LoginRequiredMiddleware type yet
from django.conf import settings
from django.contrib.auth.middleware import LoginRequiredMiddleware  # type: ignore[attr-defined]
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

from utils.typing.request import HttpRequest

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
        # If a decorator on the view function has disabled the onboarding check, skip it
        if not getattr(view_func, "onboarding_required", True):
            return None

        # If the user is trying to access a page that doesn't require onboarding, skip it
        exempt_routes = getattr(settings, "AGORA_ONBOARDING_NOT_REQUIRED_ROUTES", [])
        try:
            resolved = resolve(request.path)
            if resolved.url_name in exempt_routes:
                return None
        except Resolver404:
            pass

        if any(request.path.startswith(route) for route in exempt_routes):
            return None

        route = selectors.next_onboarding_step_route(user=request.user)

        if route is not None:
            return redirect(route)

        return None

    # If a user fails the onboarding checks don't bother recording where they were trying to go
    def get_redirect_field_name(self) -> None:
        return None
