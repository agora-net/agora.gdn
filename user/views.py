from typing import Any

import nh3
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from utils.typing.request import HttpRequest

from . import forms, selectors, services
from .decorators import onboarding_not_required


@method_decorator(onboarding_not_required, name="dispatch")
class OnboardingBillingView(TemplateView):
    template_name = "user/onboarding/billing.html"
    http_method_names = ["get", "post"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stripe_price = selectors.stripe_price_details()

        context["stripe_price_id"] = stripe_price.id
        context["stripe_price_amount"] = (stripe_price.unit_amount or 0) / 100

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore [reportIncompatibleMethodOverride]
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("profile")
        if redirect_route != selectors.OnboardingStep.BILLING:
            return redirect(redirect_route)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore [reportIncompatibleMethodOverride]
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("profile")
        if redirect_route != selectors.OnboardingStep.BILLING:
            return redirect(redirect_route)

        form = forms.StartStripeSubscriptionForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Invalid form data")
            return self.get(request, *args, **kwargs)

        unsafe_price_id = form.cleaned_data["price_id"]

        sanitized_price_id = nh3.clean(unsafe_price_id)

        stripe_checkout_session = services.create_stripe_checkout_session_for_subscription(
            request=request, stripe_price_id=sanitized_price_id
        )

        return redirect(stripe_checkout_session.url)


onboarding_billing = OnboardingBillingView.as_view()


@method_decorator(onboarding_not_required, name="dispatch")
class OnboardingIdentityView(TemplateView):
    template_name = "user/onboarding/identity.html"
    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore [reportIncompatibleMethodOverride]
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("profile")
        if redirect_route != selectors.OnboardingStep.IDENTITY:
            return redirect(redirect_route)  # type: ignore
        return super().get(request, *args, **kwargs)


onboarding_identity = OnboardingIdentityView.as_view()
