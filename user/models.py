from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from model_utils.models import TimeStampedModel


class AgoraUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    # Names can be blank upon account creation but will be populated after ID verification
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    # Nickname is optional
    nickname = models.CharField(_("nickname"), max_length=150, blank=True)

    # Email address is the username
    username = None  # type: ignore[assignment]

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space and optional nickname in between.
        """
        nickname = ""
        if self.nickname != "":
            nickname = f"""({self.nickname.strip()})"""
        full_name = f"{self.first_name.strip()} {nickname} {self.last_name.strip()}"
        return full_name.strip()

    def clean(self):
        return super().clean()


class VerifiableMixin(models.Model):
    verification_code = models.CharField(
        _("verification code"),
        blank=True,
        unique=True,
        max_length=255,
    )
    verified = models.DateField(_("verified"), blank=True, null=True)

    class Meta:
        abstract = True


# Contact Scope
class UserContactScope(models.Model):
    """A series of attributes that will eventually be claims wrapped in a scope."""

    class AbstractContactClaim(TimeStampedModel):
        contact_scope = models.ForeignKey("user.UserContactScope", on_delete=models.CASCADE)

        class Meta:
            abstract = True

    user = models.OneToOneField(AgoraUser, on_delete=models.CASCADE)


# Claims for the Contact Scope
class UserEmail(UserContactScope.AbstractContactClaim, VerifiableMixin):
    """Users can have multiple emails that all need to be verified."""

    email = models.EmailField(_("email address"), blank=True)

    def __str__(self):
        return self.email


class UserPhoneNumber(UserContactScope.AbstractContactClaim, VerifiableMixin):
    """Users can have multiple phone numbers that all need to be verified."""

    phone_number = models.CharField(_("phone number"), blank=True, max_length=255)
    country = CountryField(blank=False, help_text="What country is this phone number from?")

    def __str__(self):
        return self.phone_number


class UserDomain(UserContactScope.AbstractContactClaim, VerifiableMixin):
    """Users can have multiple domains (e.g. `example.com`) that all need to be verified."""

    domain = models.CharField(_("domain"), blank=True, max_length=255)

    def __str__(self):
        return self.domain


# Subscription information
class Customer(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)

    def __str__(self):
        return self.stripe_customer_id


class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)

    def __str__(self):
        return self.stripe_subscription_id


# Identity Verification info
class IdentityVerification(TimeStampedModel):
    # Use a foreign key instead of one-to-one as we may want to have users regularly
    # verify they are who they say they are (every couple of years or so)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_identity_verification_session_id = models.CharField(max_length=255)
    identity_issuing_country = CountryField(blank=False)

    def __str__(self):
        return self.stripe_identity_verification_session_id
