from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from agora.newsletter.services import newsletter_signup

router = Router()


class NewsletterSignupSchema(BaseModel):
    email: str
    location: str


@router.post("/signup")
def newsletter_signup_api(request: HttpRequest, payload: NewsletterSignupSchema):
    newsletter_signup(email=payload.email, location=payload.location)
    return {"message": "Thank you for being interested in Agora"}
