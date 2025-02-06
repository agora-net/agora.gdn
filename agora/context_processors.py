from django.conf import settings
from django.http import HttpRequest


def stripe_keys(request: HttpRequest) -> dict[str, str]:
    return {"STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY}
