# Register the newsletter sign ups with the admin site

from django.contrib import admin

from .models import WaitingListSignup


@admin.register(WaitingListSignup)
class WaitingListSignupAdmin(admin.ModelAdmin):
    list_display = ("email", "created", "referral_code", "referred_by")
    search_fields = ("email",)
    list_filter = ("created", "referred_by")
