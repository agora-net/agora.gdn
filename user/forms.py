from django import forms
from django.core.exceptions import ValidationError

from . import models


class StartStripeSubscriptionForm(forms.Form):
    price_id = forms.CharField(
        max_length=128,
        required=True,
    )


RESERVED_HANDLES = {"admin", "agora", "official", "test", "example", "ewan"}


class DashboardUserForm(forms.Form):
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
    )
    theme = forms.ChoiceField(
        choices=(
            ("light", "Light Mode"),
            ("dark", "Dark Mode"),
        ),
        label="Theme",
    )
    is_unlisted = forms.BooleanField(required=False, label="Unlisted Profile")

    def clean_handle(self):
        handle = self.cleaned_data.get("handle", "").strip()
        if handle.lower() in RESERVED_HANDLES:
            raise ValidationError("This handle is reserved. Please choose another.")
        return handle
