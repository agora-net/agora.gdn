from typing import cast

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, RedirectView

from user.models import AgoraUser

User = get_user_model()


class ProfileRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs) -> str:
        return self.request.user.get_absolute_url()


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "core/profile/self.html"

    def get_object(self, queryset=None) -> AgoraUser:
        # Access URL parameters from self.kwargs
        handle = self.kwargs.get("handle")
        user_id = self.kwargs.get("id")

        profile = None

        if handle is not None:
            profile = get_object_or_404(AgoraUser, handle=handle)
        elif user_id is not None:
            profile = get_object_or_404(AgoraUser, id=user_id)

        assert profile is not None

        # Check permissions
        if profile.id == self.request.user.id:
            # User can view their own profile
            pass
        elif (
            profile.visibility == AgoraUser.Visibility.HIDDEN
            and not self.request.user.has_perm("user.view_hidden_profile", profile)
        ) or (
            profile.visibility == AgoraUser.Visibility.PRIVATE
            and not self.request.user.has_perm("user.view_private_profile", profile)
        ):
            raise PermissionDenied

        return cast(AgoraUser, profile)
