from django.http import HttpRequest, HttpResponse

from .decorators import onboarding_not_required


class OnboardingNotRequiredMixin:
    """Means that the user does not need to be fully onboarded to access the view."""

    onboarding_required = False


@onboarding_not_required
def onboarding_billing(request: HttpRequest) -> HttpResponse:
    return HttpResponse()


@onboarding_not_required
def onboarding_identity(request: HttpRequest) -> HttpResponse:
    return HttpResponse()
