from typing import Any, ClassVar, LiteralString

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from model_utils.models import TimeStampedModel

import utils.models
from utils.models import SnowflakeIdPrimaryKeyMixin


class AgoraUserManager(BaseUserManager):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "AgoraUser":
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "AgoraUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class AgoraUser(AbstractUser, SnowflakeIdPrimaryKeyMixin):
    email = models.EmailField(_("email address"), unique=True)

    # Names can be blank upon account creation but will be populated after ID verification
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    # Handle can be blank upon account creation but will be populated after ID verification
    handle = models.CharField(
        _("handle"), max_length=150, blank=True, null=True, unique=True, db_index=True
    )
    # Nickname is optional
    nickname = models.CharField(_("nickname"), max_length=150, blank=True)

    # Email address is the username
    username = None  # type: ignore[assignment]

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    # Open bug so ignoring this type:
    # https://github.com/typeddjango/django-stubs/issues/174
    objects: ClassVar[AgoraUserManager] = AgoraUserManager()  # type: ignore[assignment]

    class Meta(AbstractUser.Meta):
        pass

    def get_full_name(self) -> LiteralString:
        """
        Return the first_name plus the last_name, with a space and optional nickname in between.
        """
        nickname = ""
        if self.nickname != "":
            nickname = f"""({self.nickname.strip()})"""
        full_name = f"{self.first_name.strip()} {nickname} {self.last_name.strip()}"
        # Apparently there's some issue with Python typing when using string operations
        return full_name.strip()  # type: ignore

    def clean(self) -> None:
        return super().clean()

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        if self.handle:
            return reverse("user_detail", kwargs={"handle": self.handle})
        return reverse("user_detail", kwargs={"pk": self.pk})


class UserDateOfBirth(models.Model):
    user = models.OneToOneField(AgoraUser, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField(_("day"), blank=True, null=True)
    month = models.PositiveSmallIntegerField(_("month"), blank=True, null=True)
    year = models.PositiveSmallIntegerField(_("year"), blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.year}/{self.month}/{self.day}"


class VerifiableMixin(models.Model):
    verification_code = models.CharField(
        _("verification code"),
        unique=True,
        max_length=255,
        default=utils.models.cuid2_generator,
    )
    verified = models.DateField(_("verified"), blank=True, null=True)

    class Meta:
        abstract = True


# Contact Scope
class UserContactScope(models.Model):
    """A series of attributes that will eventually be claims wrapped in a scope."""

    class AbstractContactClaim(TimeStampedModel):
        contact_scope = models.ForeignKey("user.UserContactScope", on_delete=models.CASCADE)

        class Meta:  # type: ignore
            abstract = True

    user = models.OneToOneField(AgoraUser, on_delete=models.CASCADE)


# Claims for the Contact Scope
class UserEmail(UserContactScope.AbstractContactClaim, VerifiableMixin):  # type: ignore
    """Users can have multiple emails that all need to be verified."""

    email = models.EmailField(_("email address"), blank=True)

    def __str__(self) -> str:
        return self.email


class UserPhoneNumber(UserContactScope.AbstractContactClaim, VerifiableMixin):  # type: ignore
    """Users can have multiple phone numbers that all need to be verified."""

    phone_number = models.CharField(_("phone number"), blank=True, max_length=255)
    country = CountryField(blank=False, help_text="What country is this phone number from?")

    def __str__(self) -> str:
        return self.phone_number


class UserDomain(UserContactScope.AbstractContactClaim, VerifiableMixin):  # type: ignore
    """Users can have multiple domains (e.g. `example.com`) that all need to be verified."""

    domain = models.CharField(_("domain"), blank=True, max_length=255)

    def __str__(self) -> str:
        return self.domain


# Subscription information
class Customer(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.stripe_customer_id


class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)
    expiration_date = models.DateField()

    def __str__(self) -> str:
        return self.stripe_subscription_id


class PaymentMethod(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stripe_payment_method_id = models.CharField(max_length=255)
    issuing_country = CountryField(blank=False)

    def __str__(self) -> str:
        return self.stripe_payment_method_id


# Identity Verification info
class IdentityVerification(TimeStampedModel):
    # Use a foreign key instead of one-to-one as we may want to have users regularly
    # verify they are who they say they are (every couple of years or so)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_identity_verification_session_id = models.CharField(max_length=255)
    verified_at = models.DateTimeField(null=True, default=None, blank=True)
    # Issuing country can be blank until the user has verified their identity
    identity_issuing_country = CountryField(blank=True)
    # In some situations we need more info from the user or they can get rejected
    last_error_code = models.TextField(blank=True, null=True, default=None)
    last_error_message = models.TextField(blank=True, null=True, default=None)

    def __str__(self) -> str:
        return self.stripe_identity_verification_session_id


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(AgoraUser, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user.email}"


class UserSettings(TimeStampedModel):
    class VisibilityStatus(models.TextChoices):
        UNLISTED = "UN", _("Unlisted - accessible via URL only")
        PRIVATE = "PRV", _("Private - visible to verified users only")
        PUBLIC = "PUB", _("Public - visible in directory")

    class Theme(models.TextChoices):
        LIGHT = "light", _("Light")
        DARK = "dark", _("Dark")

    user = models.OneToOneField(AgoraUser, on_delete=models.CASCADE, related_name="settings")
    theme = models.CharField(max_length=10, choices=Theme, default="light")
    visibility = models.CharField(
        max_length=3,
        choices=VisibilityStatus,
        default=VisibilityStatus.UNLISTED,
    )

    def __str__(self) -> str:
        return f"{self.user.email}"
