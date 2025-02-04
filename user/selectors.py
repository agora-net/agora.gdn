from enum import Enum

import stripe
from allauth.mfa.utils import is_mfa_enabled
from django.contrib.auth.models import AnonymousUser
from django.db.models.query import QuerySet

from . import models


class OnboardingStep(str, Enum):
    LOGIN = "account_login"
    MFA = "mfa_activate_totp"
    BILLING = "onboarding_billing"
    IDENTITY = "onboarding_identity"


def next_onboarding_step_route(user: models.AgoraUser | AnonymousUser) -> str | None:
    """
    Given a user, determine which onboarding step they should be redirected to and
    return the name of the route.

    If the user is fully onboarded, return None.
    """
    if user.is_anonymous or not user.is_authenticated:
        return OnboardingStep.LOGIN

    # Type narrowing - user is now known to be AgoraUser
    assert isinstance(user, models.AgoraUser)

    if not user_has_mfa_enabled(user=user):
        return OnboardingStep.MFA

    if not user_has_valid_subscription(user=user):
        return OnboardingStep.BILLING

    if not user_has_verified_identity(user=user):
        return OnboardingStep.IDENTITY

    return None


def user_has_mfa_enabled(*, user: models.AgoraUser) -> bool:
    return is_mfa_enabled(user)


def user_subscriptions(*, user: models.AgoraUser) -> "QuerySet[models.Subscription]":
    return models.Subscription.objects.filter(customer__user=user)


def user_has_valid_subscription(*, user: models.AgoraUser) -> bool:
    return user_subscriptions(user=user).exists()


def user_has_verified_identity(*, user: models.AgoraUser) -> bool:
    return models.IdentityVerification.objects.filter(user=user).exists()


def user_from_email(*, email: str) -> models.AgoraUser:
    return models.AgoraUser.objects.get(email=email)


def stripe_price_details() -> stripe.Price:
    """Stripe is our source of truth so use the Stripe API to get the price details."""
    lookup_key = "standard_annual"

    matching_price_list = stripe.Price.search(query=f"lookup_key:{lookup_key}")
    if matching_price_list.is_empty:
        raise ValueError(f"No price found for lookup key {lookup_key}")

    if len(matching_price_list.data) != 1:
        raise ValueError(f"Multiple prices found for lookup key {lookup_key}")

    # Pyright doesn't like this but we narrow the type using Price.search so we know this is a Price
    return matching_price_list.data[0]  # type: ignore
