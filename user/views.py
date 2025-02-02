from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from . import selectors
from .decorators import onboarding_not_required


@method_decorator(onboarding_not_required, name="dispatch")
class OnboardingBillingView(TemplateView):
    template_name = "user/onboarding/billing.html"
    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("profile")
        if redirect_route != "onboarding_billing":
            return redirect(redirect_route)
        return super().get(request, *args, **kwargs)


onboarding_billing = OnboardingBillingView.as_view()


@method_decorator(onboarding_not_required, name="dispatch")
class OnboardingIdentityView(TemplateView):
    template_name = "user/onboarding/identity.html"
    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("profile")
        if redirect_route != "onboarding_identity":
            return redirect(redirect_route)
        return super().get(request, *args, **kwargs)


onboarding_identity = OnboardingIdentityView.as_view()
