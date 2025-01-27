from django.test import LiveServerTestCase, tag


@tag("e2e")
class UserRegistrationTestCase(LiveServerTestCase):
    def test_user_registration(self) -> None:
        raise NotImplementedError
