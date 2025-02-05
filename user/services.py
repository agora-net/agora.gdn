from datetime import datetime, timedelta

import stripe
from django.urls import reverse

from utils.typing.request import HttpRequest

from . import models, selectors


def create_stripe_customer(*, user: models.AgoraUser) -> models.Customer:
    existing_customer_objs = stripe.Customer.search(query=f'email:"{user.email}"', limit=20)
    if existing_customer_objs.is_empty:
        stripe_customer_obj = stripe.Customer.create(email=user.email)
    else:
        # Don't know why there are multiple but just pick the first one for now
        stripe_customer_obj = existing_customer_objs.data[0]

    customer_obj = models.Customer(user=user, stripe_customer_id=stripe_customer_obj.id)
    customer_obj.full_clean()
    customer_obj.save()

    return customer_obj


def create_stripe_checkout_session_for_subscription(
    *, request: HttpRequest, stripe_price_id: str
) -> stripe.checkout.Session:
    if request.user.is_anonymous:
        raise ValueError("User must be authenticated to create a subscription")

    user: models.AgoraUser = request.user  # type: ignore

    # Do we have a customer record for this user?
    customer = selectors.customer_obj(for_user=user)
    if customer is None:
        customer = create_stripe_customer(user=user)

    # https://docs.stripe.com/api/checkout/sessions/create
    checkout_session = stripe.checkout.Session.create(
        customer=customer.stripe_customer_id,
        success_url=f"{request.build_absolute_uri(reverse(selectors.OnboardingStep.IDENTITY))}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri(reverse(selectors.OnboardingStep.BILLING)),
        mode="subscription",
        line_items=[
            {
                "price": stripe_price_id,
                "quantity": 1,
            }
        ],
        allow_promotion_codes=True,
        consent_collection={
            "terms_of_service": "required",
            "payment_method_reuse_agreement": {"position": "auto"},
        },
        customer_update={"address": "auto", "name": "auto"},
        expires_at=int((datetime.now() + timedelta(hours=1)).timestamp()),
        payment_method_collection="always",
    )

    return checkout_session
