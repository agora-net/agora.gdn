from typing import Any

import readtime
import readtime.result
from django.db import models
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

import utils.models


# -----------------------------------------
# Regular Models
# -----------------------------------------
class WaitingListSignup(TimeStampedModel):
    email = models.EmailField(unique=True, max_length=255)
    referral_code = models.CharField(
        max_length=10,
        default=utils.models.cuid2_generator,
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
class WaitingPage(Page, models.Model):  # type: ignore[django-manager-missing]
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

    def serve(self, request: HttpRequest, *args: Any, **kwargs: Any) -> TemplateResponse:
        """Handle the POST request to join the waiting list with our custom view"""
        if request.method == "POST" and not kwargs.get("additional_context"):
            from .views import join_waiting_list

            return join_waiting_list(request)
        return super().serve(request, *args, **kwargs)

    # Add some additional context

    def get_context(
        self,
        request: HttpRequest,
        additional_context: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        from .forms import WaitingListSignupForm

        context = super().get_context(request, *args, **kwargs)
        initial_data = {"referred_by_code": request.GET.get("ref")}
        context["form"] = WaitingListSignupForm(initial=initial_data)
        context["referral_code"] = request.session.get("referral_code")

        if additional_context:
            context.update(additional_context)

        return context


class BlogPageTag(TaggedItemBase):
    """https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging"""

    content_object = ParentalKey(
        "home.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class BlogPage(Page, models.Model):  # type: ignore[django-manager-missing]
    """A blog page, written to attract and engage readers

    Inspiration: https://www.qualcomm.com/news/releases/2024/12/qualcomm-appoints-yasumasa-nakayama-as-vice-president-and-presid
    """

    class CategoryChoices(models.TextChoices):
        NEWS = "news", _("News")
        PRESS_RELEASE = "press_release", _("Press Release")
        BLOG = "blog", _("Blog")
        ARTICLE = "article", _("Article")
        CASE_STUDY = "case_study", _("Case Study")
        WHITE_PAPER = "white_paper", _("White Paper")
        WEBINAR = "webinar", _("Webinar")
        PODCAST = "podcast", _("Podcast")
        VIDEO = "video", _("Video")
        INFOGRAPHIC = "infographic", _("Infographic")
        REPORT = "report", _("Report")
        RESEARCH = "research", _("Research")
        INTERVIEW = "interview", _("Interview")
        EVENT = "event", _("Event")
        AWARD = "award", _("Award")
        JOB_POSTING = "job_posting", _("Job Posting")

    category = models.CharField(
        choices=CategoryChoices.choices,
        max_length=255,
        blank=True,
        help_text="Text for a category above the title",
    )
    location = models.CharField(max_length=255, blank=True, help_text="Location of the release")
    content = StreamField(
        [
            ("body", blocks.RichTextBlock(blank=True, help_text="Blog body")),
        ]
    )

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        FieldPanel("location"),
        FieldPanel("content"),
        FieldPanel("tags"),
    ]

    parent_page_types = ["home.BlogIndexPage"]
    page_description = "A blog page, written to attract and engage readers"

    def read_time(self) -> readtime.result.Result:
        """Calculates how long (roughly) it will take to read the blog post"""
        words_per_minute = 235
        content = ""
        for block in self.content:
            content += block.get_prep_value()["value"]

        return readtime.of_text(content, words_per_minute)


class BlogIndexPage(Page):
    """Lists all the blog pages"""

    subpage_types = ["home.BlogPage"]

    def get_context(self, request: HttpRequest, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return the updated context
        context["blog_entries"] = BlogPage.objects.child_of(self).live()
        return context
