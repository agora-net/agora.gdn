from django.test import TestCase


class FullyOnboardedUserRequiredMiddlewareTestCase(TestCase):
    def test_without_onboarding_middleware_works_as_expected(self) -> None:
        with self.modify_settings(
            MIDDLEWARE={"remove": "user.middleware.FullyOnboardedUserRequiredMiddleware"}
        ):
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)

    def test_onboarding_middleware(self) -> None:
        response = self.client.get("/")
        self.assertRedirects(response, "/accounts/login/")
