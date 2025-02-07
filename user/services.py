from datetime import datetime, timedelta

import phonenumbers
import stripe
from django.conf import settings
from django.urls import reverse

from user.decorators import idempotent_webhook
from utils.typing.request import HttpRequest

from . import logger, models, selectors


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


def create_subscription(
    *, customer: models.Customer, stripe_subscription_id: str, expiration_date: datetime
) -> models.Subscription:
    logger.debug(f"Creating subscription for customer {customer.id}")
    subscription = models.Subscription(
        customer=customer,
        stripe_subscription_id=stripe_subscription_id,
        expiration_date=expiration_date,
    )
    subscription.full_clean()
    subscription.save()

    logger.debug(f"Created subscription {subscription.id} for customer {customer.id}")

    return subscription


def create_verified_phone_number(
    *, user_id: int, phone_number: str, verified_at: datetime | None = None
) -> models.UserPhoneNumber:
    parsed_phone_number_obj = phonenumbers.parse(phone_number)
    country_code = phonenumbers.region_code_for_number(parsed_phone_number_obj)

    user_phone_number = models.UserPhoneNumber(
        user=user_id,
        phone_number="REDACTED:STRIPE_IDENTITY",
        country=country_code,
        verified=verified_at,
    )
    user_phone_number.full_clean()
    user_phone_number.save()

    return user_phone_number


def update_user_first_last_names(
    *, user_id: int, first_name: str | None, last_name: str | None
) -> models.AgoraUser:
    user = models.AgoraUser.objects.get(id=user_id)
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    user.full_clean()
    user.save()

    return user


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
    checkout_session_obj = stripe.checkout.Session.create(
        client_reference_id=str(user.id),
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

    return checkout_session_obj


def create_identity_verification(
    *,
    user: models.AgoraUser,
    stripe_identity_verification_session_id: str,
    identity_issuing_country: str | None,
) -> models.IdentityVerification:
    identity_verification = models.IdentityVerification(
        user=user,
        stripe_identity_verification_session_id=stripe_identity_verification_session_id,
        identity_issuing_country=identity_issuing_country,
    )
    identity_verification.full_clean()
    identity_verification.save()

    return identity_verification


def create_stripe_identity_verification_session(
    *, request: HttpRequest
) -> stripe.identity.VerificationSession:
    if request.user.is_anonymous:
        raise ValueError("User must be authenticated to create a verification session")

    user: models.AgoraUser = request.user  # type: ignore

    verification_session_obj = stripe.identity.VerificationSession.create(
        client_reference_id=str(user.id),
        provided_details={
            "email": user.email,
        },
        related_customer=user.customer.stripe_customer_id,
        verification_flow=settings.STRIPE_VERIFICATION_FLOW_ID,
        return_url=request.build_absolute_uri(reverse(selectors.OnboardingStep.IDENTITY_PENDING)),
    )

    create_identity_verification(
        user=user,
        stripe_identity_verification_session_id=verification_session_obj.id,
        identity_issuing_country=None,
    )

    return verification_session_obj


def create_user_date_of_birth(
    *, user_id: int, day: int | None, month: int | None, year: int | None
) -> models.UserDateOfBirth:
    user_date_of_birth = models.UserDateOfBirth(user=user_id, day=day, month=month, year=year)
    user_date_of_birth.full_clean()
    user_date_of_birth.save()

    return user_date_of_birth


@idempotent_webhook(prefix="stripe:checkout_session_completed", id_field="checkout_session_id")
def handle_checkout_session_completed(*, checkout_session_id: str) -> None:
    logger.info(f"Handling checkout session completed event for {checkout_session_id}")
    # https://docs.stripe.com/checkout/fulfillment?payment-ui=stripe-hosted#create-fulfillment-function
    # Retrieve the Checkout Session from the API with line_items expanded
    checkout_session_obj = stripe.checkout.Session.retrieve(
        id=checkout_session_id,
        expand=["line_items", "subscription"],
    )

    if checkout_session_obj.status == "expired":
        return

    if checkout_session_obj.payment_status != "unpaid":
        user_id_str = str(checkout_session_obj.client_reference_id)
        try:
            user_id = int(user_id_str)
        except ValueError as e:
            raise ValueError(f"Invalid user ID: {user_id_str}") from e

        stripe_customer_id = str(checkout_session_obj.customer)
        customer_obj, _ = models.Customer.objects.get_or_create(
            user=user_id, stripe_customer_id=stripe_customer_id
        )

        line_items = checkout_session_obj.line_items
        if line_items is None or line_items.is_empty:
            raise ValueError("No line items in checkout session")

        # Todo(kisamoto): Handle individual line items, for now just assume our single product

        subscription_obj = checkout_session_obj.subscription
        if subscription_obj is None:
            raise ValueError("No subscription object in checkout session")
        # One year from the checkout session completion date
        subscription_end_date = datetime.fromtimestamp(
            subscription_obj.current_period_end
        ) + timedelta(days=365)

        create_subscription(
            customer=customer_obj,
            stripe_subscription_id=subscription_obj.id,
            expiration_date=subscription_end_date,
        )


@idempotent_webhook(
    prefix="stripe:identity_verification_session_completed",
    id_field="verification_session_id",
)
def handle_identity_verification_completed(*, verification_session_id: str) -> None:
    verification_session_obj = stripe.identity.VerificationSession.retrieve(
        id=verification_session_id, expand=["verified_outputs"]
    )

    # Todo(kisamoto): Handle problems with verification

    if verification_session_obj.status == "verified":
        # We don't have a "verified_at" field so we'll use the created field
        verification_datetime = datetime.fromtimestamp(verification_session_obj.created)

        user_id_str = str(verification_session_obj.client_reference_id)
        try:
            user_id = int(user_id_str)
        except ValueError as e:
            raise ValueError(f"Invalid user ID: {user_id_str}") from e

        verified_outputs: stripe.identity.VerificationSession.VerifiedOutputs = (
            verification_session_obj.verified_outputs
        )  # type: ignore
        identity_issuing_country_code = (
            verified_outputs.address.country if verified_outputs.address else None
        )

        # There's a chance we can get lots of verified outputs so wherever
        # possible we'll update the user's information

        if verified_outputs.dob:
            create_user_date_of_birth(
                user_id=user_id,
                day=verified_outputs.dob.day,
                month=verified_outputs.dob.month,
                year=verified_outputs.dob.year,
            )

        if verified_outputs.first_name or verified_outputs.last_name:
            update_user_first_last_names(
                user_id=user_id,
                first_name=verified_outputs.first_name,
                last_name=verified_outputs.last_name,
            )

        if verified_outputs.phone:
            create_verified_phone_number(
                user_id=user_id,
                phone_number=verified_outputs.phone.number,
                verified_at=verification_datetime,
            )

        identity_verification_obj, _ = models.IdentityVerification.objects.get_or_create(
            user=user_id,
            stripe_identity_verification_session_id=verification_session_id,
            defaults={
                "verified_at": verification_datetime,
                "identity_issuing_country": identity_issuing_country_code,
            },
        )


def handle_invoice_paid_webhook_event(*, invoice: stripe.Invoice) -> None:
    pass
