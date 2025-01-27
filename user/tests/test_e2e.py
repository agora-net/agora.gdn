from django.test import LiveServerTestCase, tag
from playwright.sync_api import Browser, Playwright, sync_playwright


@tag("e2e")
class UserRegistrationTestCase(LiveServerTestCase):
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
        super().setUpClass()
        playwright = sync_playwright().start()
        browser = playwright.firefox.launch()
        cls.playwright = playwright
        cls.browser = browser

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def test_user_registration(self) -> None:
        page = self.browser.new_page()
        page.goto(self.get_server_url())
        self.assertEqual(page.title(), "Sign In")
