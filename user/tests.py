from django.test import TestCase


class FullyOnboardedUserRequiredMiddlewareTestCase(TestCase):
    def test_onboarding_middleware(self):
        with self.settings(
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "allauth.account.middleware.AccountMiddleware",
                "user.middleware.FullyOnboardedUserRequiredMiddleware",
            ]
        ):
            response = self.client.get("/")

            self.assertRedirects(response, "/accounts/login/")
