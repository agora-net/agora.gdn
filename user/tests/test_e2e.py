import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from playwright.sync_api import Browser, Playwright, sync_playwright


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
        page = self.browser.new_page()
        page.goto(self.get_server_url())
        self.assertEqual(page.title(), "Sign In")
