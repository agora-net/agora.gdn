import stripe
from django.conf import settings
from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.responses import codes_2xx, codes_4xx, codes_5xx

from . import logger

api = NinjaAPI()


class StripeWebhookResponse(Schema):
    pass


@api.post(
    "/stripe",
    response={
        codes_2xx: StripeWebhookResponse,
        codes_4xx: StripeWebhookResponse,
        codes_5xx: StripeWebhookResponse,
    },
)
def stripe_webhook(request: HttpRequest):
    payload = request.body
    event = None
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    if webhook_secret is None:
        logger.error("Stripe webhook secret is not set")
        return 400, {}
    event = None

    # verify the signature
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        # Invalid payload
        logger.error(f"Error parsing payload: {str(e)}")
        return 400, {}
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return 400, {}

    if event is None:
        logger.error("Event is None (for unknown reasons)")
        return 400, {}

    # Handle the event
    if event.type == "checkout.session.completed" or event.type == "invoice.paid":
        raise NotImplementedError()
    else:
        logger.warning(f"Unhandled event type: {event.type}")

    return 200, {}
