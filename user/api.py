from ninja import Router, Schema
from ninja.security import django_auth

from user.models import AgoraUser
from utils.typing.request import HttpRequest

from . import selectors

router = Router(auth=django_auth)


class UserVerificationStatusResponse(Schema):
    status: selectors.UserVerificationStatus


@router.get(
    "/identity/verification/",
    response={200: UserVerificationStatusResponse},
    url_name="verification_status",
)
def check_users_verification_status(request: HttpRequest):
    user = request.user
    if user.is_anonymous or not user.is_authenticated:
        return 403

    agora_user: AgoraUser = user  # type: ignore

    verification_status = selectors.user_identity_verification_status(user=agora_user)

    return 200, {"status": verification_status}
