import factory
from factory.django import DjangoModelFactory

from ... import models


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = models.Customer

    stripe_customer_id = factory.LazyAttribute()


def set_valid_subscription(*, user: models.AgoraUser) -> models.Subscription:
    subscription = models.Subscription()

    subscription.full_clean()
    subscription.save()

    return subscription
