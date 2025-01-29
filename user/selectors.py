from allauth.mfa.utils import is_mfa_enabled
from django.contrib.auth.models import AnonymousUser
from django.db.models.query import QuerySet

from . import models


def next_onboarding_step_route(user: models.AgoraUser | AnonymousUser) -> str | None:
    """
    Given a user, determine which onboarding step they should be redirected to and
    return the name of the route.

    If the user is fully onboarded, return None.
    """
    route = None

    if user.is_anonymous or not user.is_authenticated:
        return "account_login"

    # Type narrowing - user is now known to be AgoraUser
    assert isinstance(user, models.AgoraUser)

    if not user_has_mfa_enabled(user=user):
        route = "mfa_activate_totp"

    if not user_has_valid_subscription(user=user):
        route = "onboarding_billing"

    if not user_has_verified_identity(user=user):
        route = "onboarding_identity"

    return route


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
