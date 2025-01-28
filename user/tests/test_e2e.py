import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
from playwright.sync_api import Browser, Playwright, expect, sync_playwright

from .utils import faker


@tag("e2e")
class UserRegistrationTestCase(StaticLiveServerTestCase):
    playwright: Playwright
    browser: Browser

    def get_server_url(self) -> str:
        """Helper method to get the live server URL.

        In future we could use this to read an environment variable
        so we can run the tests against a different (i.e. live) server.
        """
        return self.live_server_url

    def get_route(self, route_name: str) -> str:
        return self.get_server_url() + reverse(route_name)

    @classmethod
    def setUpClass(cls) -> None:
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = ""
        cls.browser.close()
        cls.playwright.stop()

    def test_user_registration(self) -> None:
        """
        Jamie is a new user who wants to sign up for the service.
        """
        user_email = faker.fake_email()
        page = self.browser.new_page()

        # First of all they visit the login page
        page.goto(self.get_route("account_login"))
        self.assertEqual(page.title(), "Sign In")

        # They see a link to sign up and click it
        page.click("a:has-text('Sign up')")
        page.wait_for_url(self.get_route("account_signup"))
        self.assertEqual(page.title(), "Signup")

        # They enter their email address and password and submit the form
        insecure_password = "password"
        page.fill("input[name=email]", user_email)
        page.fill("input[name=password1]", insecure_password)
        page.fill("input[name=password2]", insecure_password)
        page.click("button:has-text('Sign up')")

        # Unfortunately the password is too insecure and they are redirected back to the signup page
        # with some validation errors
        page.wait_for_url(self.get_route("account_signup"))
        self.assertEqual(page.title(), "Signup")
        errorlist = page.locator("ul.errorlist")
        self.assertTrue(errorlist.is_visible())
        expect(errorlist).to_contain_text("This password is too common.")
        expect(errorlist).to_contain_text("This password is too short.")
