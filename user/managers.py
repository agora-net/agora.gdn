from typing import Any

from django.contrib.auth.models import BaseUserManager

from . import models as user_models


class AgoraUserManager(BaseUserManager["user_models.AgoraUser"]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "user_models.AgoraUser":
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "user_models.AgoraUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)
