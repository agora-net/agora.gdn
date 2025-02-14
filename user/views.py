from typing import Any

import nh3
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from utils.typing.request import HttpRequest

from . import forms, logger, selectors, services
from .decorators import onboarding_not_required
from .models import IdentityVerification


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
            return redirect("dashboard")
        if redirect_route != selectors.OnboardingStep.BILLING:
            return redirect(redirect_route)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore [reportIncompatibleMethodOverride]
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("dashboard")
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

        return redirect(to=stripe_checkout_session.url or selectors.OnboardingStep.BILLING)


onboarding_billing = OnboardingBillingView.as_view()


@method_decorator(onboarding_not_required, name="dispatch")
class OnboardingIdentityView(TemplateView):
    template_name = "user/onboarding/identity.html"
    http_method_names = ["get", "post"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore [reportIncompatibleMethodOverride]
        # First off, check and process the session if we can
        unsafe_checkout_session_id = str(request.GET.get("session_id", ""))
        sanitized_checkout_session_id = nh3.clean(unsafe_checkout_session_id)

        if sanitized_checkout_session_id:
            try:
                services.handle_checkout_session_completed(
                    checkout_session_id=sanitized_checkout_session_id
                )
            except ValueError as e:
                logger.error("Error processing checkout session", exc_info=e)
                messages.error(
                    request=request,
                    message="Error processing checkout session, please come back later",
                )
                return redirect(selectors.OnboardingStep.BILLING)

        # We would then know if we have a subscription or not, then decide if we need to redirect
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("dashboard")
        if redirect_route != selectors.OnboardingStep.IDENTITY:
            return redirect(redirect_route)  # type: ignore

        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore [reportIncompatibleMethodOverride]
        redirect_route = selectors.next_onboarding_step_route(user=request.user)
        if redirect_route is None:
            return redirect("dashboard")
        if redirect_route != selectors.OnboardingStep.IDENTITY:
            return redirect(redirect_route)

        verification_session_obj = services.create_stripe_identity_verification_session(
            request=request
        )

        return redirect(verification_session_obj.url or selectors.OnboardingStep.IDENTITY)


onboarding_identity = OnboardingIdentityView.as_view()


@method_decorator(onboarding_not_required, name="dispatch")
class OnboardingIdentityPendingView(TemplateView):
    """Identity verification can take some time.
    When a user is redirected here after completing the verification process, check to
    see if we have verification data in the database (added via webhook).

    If not, the template can show a message and poll in the background with a gradually increasing
    backoff.

    If we do have verification data the user can progress."""

    template_name = "user/onboarding/identity_pending.html"
    http_method_names = ["get"]


onboarding_identity_pending = OnboardingIdentityPendingView.as_view()


class UserDashboardView(View):
    template_name = "user/dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user

        profile = getattr(user, "profile", None)
        settings = getattr(user, "settings", None)
        # Read read-only fields from user and related models
        dob = getattr(user, "userdateofbirth", None)
        year_of_birth = dob.year if dob and dob.year else ""
        # For verified country
        # assume using latest IdentityVerification with a value (modify as needed)
        identity = (
            IdentityVerification.objects.filter(user=user, verified_at__isnull=False)
            .order_by("-verified_at")
            .first()
        )
        country_verified = identity.identity_issuing_country.name if identity else ""
        form = forms.DashboardUserForm(
            initial={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "year_of_birth": year_of_birth,
                "country_verified": country_verified,
                "nickname": user.nickname,
                "handle": user.handle or "",
                "visibility": getattr(profile, "visibility", "unlisted") if profile else "unlisted",
                "theme": getattr(settings, "theme", "light") if settings else "light",
            }
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        form = forms.DashboardUserForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            # Update user fields
            user.nickname = cd.get("nickname", user.nickname)
            user.handle = cd.get("handle", user.handle) or None
            user.save()

            # Update or create profile
            profile, _ = user.profile.get_or_create(user=user)
            if "profile_picture" in request.FILES:
                profile.profile_picture = request.FILES["profile_picture"]
            profile.visibility = cd.get("visibility", profile.visibility)
            profile.save()

            # Update or create settings
            settings, _ = user.settings.get_or_create(user=user)
            settings.theme = cd.get("theme", settings.theme)
            settings.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("user-dashboard")
        messages.error(request, "Please correct errors below.")
        return render(request, self.template_name, {"form": form})


dashboard = UserDashboardView.as_view()
