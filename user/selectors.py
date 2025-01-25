from allauth.mfa.utils import is_mfa_enabled
from django_stubs_ext.db.models import QuerySet

from . import models


def user_has_mfa_enabled(*, user: models.AgoraUser) -> bool:
    return is_mfa_enabled(user)


def user_subscriptions(*, user: models.AgoraUser) -> "QuerySet[models.Subscription]":
    return models.Subscription.objects.filter(customer__user=user)


def user_has_valid_subscription(*, user: models.AgoraUser) -> bool:
    return user_subscriptions(user=user).exists()


def user_has_verified_identity(*, user: models.AgoraUser) -> bool:
    return models.IdentityVerification.objects.filter(user=user).exists()
