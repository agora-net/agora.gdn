from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from . import models as user_models


class SubscriptionInline(admin.StackedInline):
    model = user_models.Subscription
    readonly_fields = ["stripe_subscription_id", "expiration_date"]
    extra = 0


class PaymentMethodInline(admin.StackedInline):
    model = user_models.PaymentMethod
    readonly_fields = ["stripe_payment_method_id", "issuing_country"]
    extra = 0


class UserProfileInline(admin.StackedInline):
    model = user_models.UserProfile
    extra = 0


class UserSettingsInline(admin.StackedInline):
    model = user_models.UserSettings
    extra = 0


class IdentityVerificationInline(admin.StackedInline):
    model = user_models.IdentityVerification
    readonly_fields = ["stripe_identity_verification_session_id", "identity_issuing_country"]
    extra = 0


class UserEmailInline(admin.StackedInline):
    model = user_models.UserEmail
    readonly_fields = ["email"]
    extra = 0


class UserPhoneNumberInline(admin.StackedInline):
    model = user_models.UserPhoneNumber
    readonly_fields = ["phone_number", "country"]
    extra = 0


class UserDomainInline(admin.StackedInline):
    model = user_models.UserDomain
    readonly_fields = ["domain"]
    extra = 0


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = user_models.AgoraUser
        fields = [
            "email",
        ]

    def clean_password2(self) -> str:
        # Check that the two password entries match
        password1: str | None = self.cleaned_data.get("password1")
        password2: str | None = self.cleaned_data.get("password2")
        if not password1 or not password2:
            raise ValidationError("Password is required")
        if password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit: bool = True) -> user_models.AgoraUser:
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = user_models.AgoraUser
        fields = ["email", "password", "is_active", "is_staff"]


@admin.register(user_models.AgoraUser)
class AgoraUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email", "is_staff"]
    list_filter = ["is_staff"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        # ("Personal info", {"fields": ["date_of_birth"]}),
        ("Permissions", {"fields": ["is_staff"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []
    inlines = [
        UserProfileInline,
        UserSettingsInline,
        IdentityVerificationInline,
    ]


@admin.register(user_models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "stripe_customer_id"]
    search_fields = ["user__email", "stripe_customer_id"]
    readonly_fields = ["stripe_customer_id"]
    inlines = [
        SubscriptionInline,
        PaymentMethodInline,
    ]


@admin.register(user_models.UserContactScope)
class UserContactScopeAdmin(admin.ModelAdmin):
    list_display = [
        "user",
    ]
    search_fields = [
        "user__email",
    ]
    readonly_fields = [
        "user",
    ]
    inlines = [
        UserEmailInline,
        UserPhoneNumberInline,
        UserDomainInline,
    ]
