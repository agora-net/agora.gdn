from django.test import TestCase


class FullyOnboardedUserRequiredMiddlewareTestCase(TestCase):
    def test_onboarding_middleware(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/accounts/login/")
