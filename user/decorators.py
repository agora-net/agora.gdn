from collections.abc import Callable
from typing import TypeVar

from django.http import HttpRequest, HttpResponse

F = TypeVar("F", bound=Callable[[HttpRequest], HttpResponse])


def onboarding_not_required(view_func: F) -> F:
    """
    Decorator for views that removes the need for a user to be fully onboarded.
    """
    setattr(view_func, "onboarding_required", False)  # noqa: B010
    return view_func
