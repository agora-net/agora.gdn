from django.contrib import admin

from .models import NewsletterSubscription


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin[NewsletterSubscription]):
    list_display = ("email", "location", "created", "modified")
    search_fields = ("email", "location")
