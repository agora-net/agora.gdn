from django.db import models
from model_utils.models import TimeStampedModel


class NewsletterSubscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.email
