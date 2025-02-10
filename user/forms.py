from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import models


class StartStripeSubscriptionForm(forms.Form):
    price_id = forms.CharField(
        max_length=128,
        required=True,
    )


RESERVED_HANDLES = {
    # Personal entries
    "ewan",
    # Ambiguous/impersonation risk
    "admin",
    "official",
    "moderator",
    "administrator",
    "support",
    "unknown",
    "anonymous",
    "user",
    "username",
    "default",
    "null",
    "helpdesk",
    "security",
    "contact",
    "verify",
    "auth",
    "login",
    "register",
    "abuse",
    "legal",
    "tos",
    "privacy",
    "sysadmin",
    "root",
    "sudo",
    "superuser",
    "webmaster",
    "host",
    "system",
    "server",
    "undefined",
    "void",
    "generic",
    "placeholder",
    "api",
    "bot",
    "status",
    "staff",
    "service",
    "mail",
    "news",
    "internal",
    "test",
    "example",
    "staging",
    "dev",
    "prod",
    "beta",
    "gamma",
    "alpha",
    "info",
    "adminteam",
    "sales",
    "marketing",
    "feedback",
    "owner",
    "ceo",
    "founder",
    "demo",
    "temp",
    "guest",
    "billing",
    "invoice",
    "payment",
    "survey",
    "notification",
    "alert",
    # Agora specific
    "agora",
    "agoraapp",
    "agorasupport",
    "agoraadmin",
    "getagora",
    "helloagora",
    "agorahelp",
    "agoraofficial",
    "askagora",
}


class DashboardUserForm(forms.Form):
    # A way to break the form into separate groups in the UI
    field_groups = {
        "profile": {
            # The title of the group in the UI
            "title": _("Profile"),
            "help_text": _("Update your profile information."),
            # The fields in the group (order matters)
            # Names must match the field names in the form
            "fields": [],
        }
    }

    # Read-only fields
    first_name = forms.CharField(disabled=True, required=False, label="First name")
    last_name = forms.CharField(disabled=True, required=False, label="Last name")
    year_of_birth = forms.IntegerField(disabled=True, required=False, label="Year of Birth")
    country_verified = forms.CharField(
        disabled=True, required=False, label="Country of Verified ID"
    )

    # Editable fields
    nickname = forms.CharField(required=False, label="Nickname")
    profile_picture = forms.ImageField(required=False, label="Profile Picture")
    handle = forms.CharField(required=False, label="Username for URL (handle)", max_length=150)
    visibility = forms.ChoiceField(
        choices=models.UserSettings.VisibilityStatus.choices,
        initial=models.UserSettings.VisibilityStatus.UNLISTED,
        label="Profile Visibility",
        widget=forms.RadioSelect,
    )
    theme = forms.ChoiceField(
        choices=models.UserSettings.Theme.choices,
        label="Theme",
        widget=forms.RadioSelect,
    )

    def clean_handle(self):
        handle = self.cleaned_data.get("handle", "").strip()
        if handle.lower() in RESERVED_HANDLES:
            raise ValidationError("This handle is reserved. Please choose another.")
        return handle
