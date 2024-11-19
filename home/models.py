from django.db import models
from model_utils.models import TimeStampedModel
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


# -----------------------------------------
# Regular Models
# -----------------------------------------
class WaitingListSignup(TimeStampedModel):
    email = models.EmailField(unique=True, max_length=255)

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
    background_color = models.CharField(
        max_length=255, blank=True, help_text="Background color for the waiting page"
    )
    signup_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Sign Up image",
    )

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel("tag"),
        FieldPanel("waiting_title"),
        FieldPanel("description"),
        FieldPanel("show_signup"),
        FieldPanel("background_color"),
        FieldPanel("signup_image"),
    ]
