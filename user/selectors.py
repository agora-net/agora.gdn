from enum import Enum

import stripe
from allauth.mfa.utils import is_mfa_enabled
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.utils import timezone

from . import models


class OnboardingStep(str, Enum):
    LOGIN = "account_login"
    MFA = "mfa_activate_totp"
    BILLING = "onboarding_billing"
    IDENTITY = "onboarding_identity"
    IDENTITY_PENDING = "onboarding_identity_pending"


class UserVerificationStatus(str, Enum):
    MISSING = "missing"
    VERIFIED = "verified"
    PENDING = "pending"
    MORE_INFO_REQUIRED = "more_info_required"
    REJECTED = "rejected"


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

    identity_verification_status = user_identity_verification_status(user=user)

    if identity_verification_status == UserVerificationStatus.MISSING:
        return OnboardingStep.IDENTITY

    if identity_verification_status == UserVerificationStatus.PENDING:
        return OnboardingStep.IDENTITY_PENDING

    if identity_verification_status == UserVerificationStatus.REJECTED:
        raise NotImplementedError("Handle rejected identity verification")

    if identity_verification_status == UserVerificationStatus.MORE_INFO_REQUIRED:
        raise NotImplementedError("Handle more info required for identity verification")

    return None


def user_has_mfa_enabled(*, user: models.AgoraUser) -> bool:
    return is_mfa_enabled(user)


def user_subscriptions(*, user: models.AgoraUser) -> "QuerySet[models.Subscription]":
    return models.Subscription.objects.filter(customer__user=user)


def user_has_valid_subscription(*, user: models.AgoraUser) -> bool:
    return user_subscriptions(user=user).filter(expiration_date__gte=timezone.now().date()).exists()


def user_has_verified_identity(*, user: models.AgoraUser) -> bool:
    now = timezone.now()
    return models.IdentityVerification.objects.filter(user=user, verified_at__lte=now).exists()


def user_identity_verification_status(*, user: models.AgoraUser) -> UserVerificationStatus:
    user_identity_verification_queryset = models.IdentityVerification.objects.filter(user=user)

    if not user_identity_verification_queryset.exists():
        return UserVerificationStatus.MISSING

    if user_identity_verification_queryset.filter(verified_at__isnull=True).exists():
        return UserVerificationStatus.PENDING

    if (
        user_identity_verification_queryset.filter(last_error_code__isnull=False)
        .exclude(last_error_code="")
        .exists()
    ):
        return UserVerificationStatus.REJECTED

    return UserVerificationStatus.VERIFIED


def user_from_email(*, email: str) -> models.AgoraUser:
    return models.AgoraUser.objects.get(email=email)


def stripe_price_details() -> stripe.Price:
    """Stripe is our source of truth so use the Stripe API to get the price details."""
    stripe_lookup_key = "standard_annual"
    cache_lookup_key = f"stripe:price:{stripe_lookup_key}"

    cached_price = cache.get(cache_lookup_key)
    if cached_price is not None:
        return cached_price

    matching_price_list = stripe.Price.search(query=f'lookup_key:"{stripe_lookup_key}"')
    if matching_price_list.is_empty:
        raise ValueError(f"No price found for lookup key {stripe_lookup_key}")

    if len(matching_price_list.data) != 1:
        raise ValueError(f"Multiple prices found for lookup key {stripe_lookup_key}")

    # Pyright doesn't like this but we narrow the type using Price.search so we know this is a Price
    stripe_price: stripe.Price = matching_price_list.data[0]  # type: ignore

    cache.set(cache_lookup_key, stripe_price, timeout=60 * 60 * 24)

    return stripe_price


def customer_obj(*, for_user: models.AgoraUser) -> models.Customer | None:
    try:
        return for_user.customer
    except models.AgoraUser.customer.RelatedObjectDoesNotExist:
        return None
