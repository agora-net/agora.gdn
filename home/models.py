from cuid2 import Cuid
from django.db import models
from django.template.response import TemplateResponse
from model_utils.models import TimeStampedModel
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


# -----------------------------------------
# Regular Models
# -----------------------------------------
class WaitingListSignup(TimeStampedModel):
    email = models.EmailField(unique=True, max_length=255)
    referral_code = models.CharField(max_length=10, default=Cuid(length=10).generate, unique=True)
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

    # Overwrite some core methods

    def route(self, request, path_components):
        if request.method == "POST":
            from .views import join_waiting_list

            return join_waiting_list(request)
        return super().route(request, path_components)

    def serve(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        # Allow passing additional context to serve method
        context.update(kwargs.get("context", {}))

        return TemplateResponse(
            request,
            self.get_template(request, *args, **kwargs),
            context,
        )

    # Add some additional context

    def get_context(self, request):
        from .forms import WaitingListSignupForm

        context = super().get_context(request)
        initial_data = {"referred_by_code": request.GET.get("ref")}
        context["form"] = WaitingListSignupForm(data=initial_data)
        return context
