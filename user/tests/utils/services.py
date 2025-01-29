import factory
from factory.django import DjangoModelFactory

from ... import models


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = models.Customer

    # stripe_customer_id = factory.LazyAttribute()


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = models.Subscription

    customer = factory.SubFactory(CustomerFactory)
    # stripe_subscription_id = factory.LazyAttribute()
    # expiration_date = factory.LazyAttribute()


def set_valid_subscription(*, user: models.AgoraUser) -> models.Subscription:
    subscription = models.Subscription()

    subscription.full_clean()
    subscription.save()

    return subscription


def set_verified_identity(*, user: models.AgoraUser) -> models.IdentityVerification:
    identity = models.IdentityVerification()

    identity.full_clean()
    identity.save()

    return identity
