from typing import cast

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from user.models import AgoraUser

User = get_user_model()


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "core/profile/self.html"

    def get_object(self, queryset=None) -> AgoraUser:
        return cast(AgoraUser, self.request.user)
