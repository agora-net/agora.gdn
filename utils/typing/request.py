from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest as DjangoHttpRequest

from user.models import AgoraUser


class HttpRequest(DjangoHttpRequest):
    """Custom HttpRequest class that includes the proper user attribute for typing purposes."""

    user: AnonymousUser | AgoraUser  # type: ignore [assignment]
