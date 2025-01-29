from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from . import selectors
from .decorators import onboarding_not_required


class OnboardingNotRequiredMixin:
    """Means that the user does not need to be fully onboarded to access the view."""

    onboarding_required = False


@onboarding_not_required
def onboarding_billing(request: HttpRequest) -> HttpResponse:
    redirect_route = selectors.next_onboarding_step_route(user=request.user)
    if redirect_route is None:
        return redirect("profile")
    if redirect_route != "onboarding_billing":
        return redirect(redirect_route)
    return HttpResponse()


@onboarding_not_required
def onboarding_identity(request: HttpRequest) -> HttpResponse:
    redirect_route = selectors.next_onboarding_step_route(user=request.user)
    if redirect_route is None:
        return redirect("profile")
    if redirect_route != "onboarding_identity":
        return redirect(redirect_route)
    return HttpResponse()
