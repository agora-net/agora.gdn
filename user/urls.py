from django.urls import include, path

from . import selectors, views, webhooks

urlpatterns = [
    path(
        "onboarding/",
        include(
            [
                path(
                    "billing/", view=views.onboarding_billing, name=selectors.OnboardingStep.BILLING
                ),
                path(
                    "identity/pending",
                    view=views.onboarding_identity_pending,
                    name=selectors.OnboardingStep.IDENTITY_PENDING,
                ),
                path(
                    "identity/",
                    view=views.onboarding_identity,
                    name=selectors.OnboardingStep.IDENTITY,
                ),
            ]
        ),
    ),
    path("webhooks/", webhooks.api.urls),
]
