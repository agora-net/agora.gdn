from ninja import NinjaAPI

api = NinjaAPI(version="1.0.0")

api.add_router("/user/webhooks/", "user.webhooks.router")
api.add_router("/user/", "user.api.router")
