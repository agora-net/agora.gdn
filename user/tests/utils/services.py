from datetime import datetime, timedelta

import factory
from factory.django import DjangoModelFactory

from utils.models import cuid2_generator

from ... import models


class CustomerFactory(DjangoModelFactory):
    class Meta:  # type: ignore
        model = models.Customer

    stripe_customer_id = factory.LazyFunction(lambda: "cus_" + cuid2_generator())


class SubscriptionFactory(DjangoModelFactory):
    class Meta:  # type: ignore
        model = models.Subscription

    customer = factory.SubFactory(CustomerFactory)
    stripe_subscription_id = factory.LazyFunction(lambda: "sub_" + cuid2_generator())
    expiration_date = factory.LazyFunction(lambda: datetime.now() + timedelta(days=365))


class IdentityVerificationFactory(DjangoModelFactory):
    class Meta:  # type: ignore
        model = models.IdentityVerification

    stripe_identity_verification_session_id = factory.LazyFunction(
        lambda: "ivs_" + cuid2_generator()
    )
    identity_issuing_country = factory.Faker("country_code")


def create_valid_subscription(*, user: models.AgoraUser) -> models.Subscription:
    subscription = SubscriptionFactory.create(customer__user=user)

    return subscription


def create_verified_identity(*, user: models.AgoraUser) -> models.IdentityVerification:
    identity = IdentityVerificationFactory.create(user=user)

    return identity
