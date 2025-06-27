from django.core.exceptions import ValidationError
from ninja import NinjaAPI

api = NinjaAPI(version="1.0.0")


@api.exception_handler(ValidationError)
def validation_error_handler(request, exc):
    return api.create_response(
        request,
        {"detail": exc.messages},
        status=400,
    )


api.add_router("/user/webhooks/", "user.webhooks.router")
api.add_router("/user/", "user.api.router")
api.add_router("/newsletter/", "agora.newsletter.api.router")
