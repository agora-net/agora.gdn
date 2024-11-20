from cuid2 import Cuid
from django.db import models
from model_utils.models import TimeStampedModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page


# -----------------------------------------
# Regular Models
# -----------------------------------------
class WaitingListSignup(TimeStampedModel):
    email = models.EmailField(unique=True, max_length=255)
    referral_code = models.CharField(
        max_length=10,
        default=Cuid(length=10).generate,
        unique=True,
        editable=False,
    )
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        help_text="The person who referred this user",
    )

    def __str__(self) -> str:
        return self.email


# -----------------------------------------
# Pages
# -----------------------------------------
class WaitingPage(Page):
    # Database fields

    tag = models.CharField(max_length=255, blank=True, help_text="Text for a tag above the title")
    waiting_title = models.CharField(max_length=255, help_text="Title for the waiting page")
    description = models.TextField(blank=True, help_text="Description for the waiting page")
    show_signup = models.BooleanField(default=True, help_text="Show the signup form or not")
    signup_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Sign Up image",
    )
    features = StreamField(
        [
            (
                "feature_list",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("icon", blocks.CharBlock()),
                            ("title", blocks.CharBlock()),
                            ("description", blocks.TextBlock()),
                        ]
                    )
                ),
            )
        ]
    )

    # Content for successful sign up to waiting list. Will have referral code injected
    success_content = StreamField(
        [
            (
                "title",
                blocks.CharBlock(
                    max_length=255,
                    blank=True,
                    help_text="Title upon successful sign up to waiting list",
                ),
            ),
            ("body", blocks.RichTextBlock(blank=True, help_text="Body upon successful sign up")),
            (
                "referral_code",
                blocks.BooleanBlock(default=True, help_text="Show referral code here"),
            ),
            (
                "incentive_list",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("icon", blocks.CharBlock()),
                            ("title", blocks.CharBlock()),
                            ("description", blocks.TextBlock()),
                        ]
                    )
                ),
            ),
        ]
    )

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel("tag"),
        FieldPanel("waiting_title"),
        FieldPanel("description"),
        FieldPanel("show_signup"),
        FieldPanel("signup_image"),
        FieldPanel("features"),
        FieldPanel("success_content"),
    ]

    # Overwrite some core methods

    def serve(self, request, *args, **kwargs):
        """Handle the POST request to join the waiting list with our custom view"""
        if request.method == "POST" and not kwargs.get("additional_context"):
            from .views import join_waiting_list

            return join_waiting_list(request)
        return super().serve(request, *args, **kwargs)

    # Add some additional context

    def get_context(self, request, additional_context=None, *args, **kwargs):
        from .forms import WaitingListSignupForm

        context = super().get_context(request, *args, **kwargs)
        initial_data = {"referred_by_code": request.GET.get("ref")}
        context["form"] = WaitingListSignupForm(data=initial_data)
        context["referral_code"] = request.session.get("referral_code")

        if additional_context:
            context.update(additional_context)

        return context
