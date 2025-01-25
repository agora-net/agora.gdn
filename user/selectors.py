from allauth.mfa.utils import is_mfa_enabled

from . import models


def user_has_mfa_enabled(*, user: models.AgoraUser) -> bool:
    return is_mfa_enabled(user)


def user_subscription(*, user: models.AgoraUser) -> models.Subscription:
    return models.Subscription.objects.get(customer__user=user)


def user_has_valid_subscription(*, user: models.AgoraUser) -> bool:
    try:
        user_subscription(user=user)
    except models.Subscription.DoesNotExist:
        return False
    return True


def user_has_verified_identity(*, user: models.AgoraUser) -> bool:
    return models.IdentityVerification.objects.filter(user=user).exists()
