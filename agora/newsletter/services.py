from django.core.exceptions import ValidationError

from .models import NewsletterSubscription


def newsletter_signup(*, email: str, location: str) -> NewsletterSubscription:
    if NewsletterSubscription.objects.filter(email=email).exists():
        raise ValidationError("Email already subscribed.")

    subscription = NewsletterSubscription(email=email, location=location)
    subscription.full_clean()
    subscription.save()

    return subscription
