from django.http import HttpRequest
from ninja import NinjaAPI

api = NinjaAPI()


@api.post("/stripe")
def stripe_webhook(request: HttpRequest):
    pass
