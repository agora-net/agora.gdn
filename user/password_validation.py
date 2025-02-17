from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MaximumLengthValidator:
    def __init__(self, max_length: int = 64):
        self.max_length = max_length

    def validate(self, password: str, user: AbstractUser | None = None) -> None:
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password must contain no more than %(max_length)d characters."),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self) -> str:
        return _(f"Your password must be shorter than {self.max_length} characters.")
