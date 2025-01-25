from typing import Any, Protocol, TypeVar


class ViewFunction(Protocol):
    onboarding_required: bool

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


F = TypeVar("F", bound=ViewFunction)


def onboarding_not_required(view_func: F) -> F:
    """
    Decorator for views that removes the need for a user to be fully onboarded.
    """
    view_func.onboarding_required = False
    return view_func
