from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "onboarding/",
        include(
            [
                path("billing/", view=views.onboarding_billing, name="onboarding_billing"),
                path("identity/", view=views.onboarding_identity, name="onboarding_identity"),
            ]
        ),
    )
]
