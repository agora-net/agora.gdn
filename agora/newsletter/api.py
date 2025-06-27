from django.http import HttpRequest, HttpResponse
from ninja import Router
from pydantic import BaseModel

from agora.newsletter.services import newsletter_signup

router = Router()


class NewsletterSignupSchema(BaseModel):
    email: str
    location: str


@router.post("/signup")
def newsletter_signup_api(
    request: HttpRequest,
    response: HttpResponse,
    payload: NewsletterSignupSchema,
):
    newsletter_signup(email=payload.email, location=payload.location)
    response.set_cookie("newsletter_signup", "true", max_age=60 * 60 * 24 * 30)
    return {"message": "Thank you for being interested in Agora"}
