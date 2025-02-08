from ninja import NinjaAPI

api = NinjaAPI()

api.add_router("/user/webhooks/", "user.webhooks.router")
api.add_router("/user/", "user.api.router")
