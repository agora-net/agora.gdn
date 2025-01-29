import os

import mintotp
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import tag
from django.urls import reverse
from playwright.sync_api import Browser, Playwright, expect, sync_playwright

from user import selectors

from .utils import faker
from .utils import services as test_services


def extract_verification_code(email_body: str) -> str | None:
    # Find the line after the prompt text
    lines = email_body.split("\n")
    for i, line in enumerate(lines):
        if "Your email verification code is listed below" in line:
            # The code is on the next non-empty line
            for potential_code in lines[i + 1 :]:
                if potential_code.strip():
                    return potential_code.strip()
    return None


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

    def get_route_by_name(self, route_name: str) -> str:
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

    def test_user_registration_and_onboarding(self) -> None:
        """
        Jamie is a new user who wants to sign up for the service.
        """
        user_email = faker.fake_email()
        page = self.browser.new_page()
        page.set_default_navigation_timeout(500)

        # First of all they visit the login page
        page.goto(self.get_route_by_name("account_login"))
        self.assertEqual(page.title(), "Sign In")

        # They see a link to sign up and click it
        page.click("a:has-text('Sign up')")
        page.wait_for_url(self.get_route_by_name("account_signup"))
        self.assertEqual(page.title(), "Signup")

        # They enter their email address and password and submit the form
        insecure_password = "password"
        page.fill("input[name=email]", user_email)
        page.fill("input[name=password1]", insecure_password)
        page.fill("input[name=password2]", insecure_password)
        page.click("button:has-text('Sign up')")

        # Unfortunately the password is too insecure and they are redirected back to the signup page
        # with some validation errors
        page.wait_for_url(self.get_route_by_name("account_signup"))
        self.assertEqual(page.title(), "Signup")
        errorlist = page.locator("ul.errorlist")
        self.assertTrue(errorlist.is_visible())
        expect(errorlist).to_contain_text("This password is too common.")
        expect(errorlist).to_contain_text("This password is too short.")

        # They try again with a more secure password
        secure_password = "I'm4S3cur3P@ssw0rd!"
        verification_code = None
        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            page.fill("input[name=password1]", secure_password)
            page.fill("input[name=password2]", secure_password)
            page.click("button:has-text('Sign up')")
            page.wait_for_url(self.get_route_by_name("account_email_verification_sent"))
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            # They successfully receive an email with a verification code
            verification_code = extract_verification_code(str(email.body))

        # The verification code is used to confirm their email
        self.assertIsNotNone(verification_code)
        page.fill("input[name=code]", str(verification_code))
        page.click("button:has-text('Confirm')")

        if self.get_route_by_name("account_reauthenticate") in page.url:
            # Sometimes we have to reauthenticate before we can continue
            page.fill("input[name=password]", secure_password)
            page.click("button:has-text('Confirm')")

        # Next they enter the onboarding flow
        page.wait_for_url(self.get_route_by_name("mfa_activate_totp"))

        # They try to manually get away from the onboarding process but are redirected back
        page.goto(self.get_route_by_name("profile"))
        page.wait_for_url(self.get_route_by_name("mfa_activate_totp"))

        # They have to set up MFA and choose TOTP (Authenticator app).
        totp_secret_input = page.locator("input#authenticator_secret")
        self.assertTrue(totp_secret_input.is_visible())
        totp_secret = totp_secret_input.input_value()
        totp_authenticator_code = mintotp.totp(totp_secret)
        page.fill("input[name=code]", totp_authenticator_code)
        page.click("button:has-text('Activate')")

        # They get shown their recovery codes
        page.wait_for_url(self.get_route_by_name("mfa_view_recovery_codes"))
        recovery_codes = page.locator("textarea#recovery_codes").input_value().split("\n")
        self.assertEqual(len(recovery_codes), 12)

        # After successful setup they progress to the next step
        page.goto(self.get_route_by_name("onboarding_billing"))
        page.wait_for_url(self.get_route_by_name("onboarding_billing"))

        # They try again to get away from the onboarding process but are redirected back
        page.goto(self.get_route_by_name("profile"))
        page.wait_for_url(self.get_route_by_name("onboarding_billing"))

        # They pay for their annual subscription and progress to the next step
        # Just update the database to say they have a valid subscription and go to next step
        user_obj = selectors.user_from_email(email=user_email)
        test_services.create_valid_subscription(user=user_obj)
        page.reload()  # Refresh the page to get the updated subscription status
        page.wait_for_url(self.get_route_by_name("onboarding_identity"))

        # Once again they try to get away from the onboarding process but are redirected back
        page.goto(self.get_route_by_name("profile"))
        page.wait_for_url(self.get_route_by_name("onboarding_identity"))

        # They verify their identity
        # For now we'll manually set it verified in the database.
        test_services.create_verified_identity(user=user_obj)
        page.reload()  # Refresh the page to get the updated identity status
        # Now they are fully onboarded and can access their profile
        page.wait_for_url(self.get_route_by_name("profile"))
        self.assertEqual(page.title(), "Your profile")

        # They refresh the profile page and it works as expected
        page.reload()
        self.assertEqual(page.title(), "Your profile")

        # When they log out they are redirected to the login page
        page.click("a:has-text('Sign out')")
        page.wait_for_url(self.get_route_by_name("account_login"))

        # If they're not logged in they can't access the profile page
        # and are redirected to the login page
        page.goto(self.get_route_by_name("profile"))
        page.wait_for_url(self.get_route_by_name("account_login"))

        # They log in and are redirected back to the profile page
        page.goto(self.get_route_by_name("account_login"))
        page.fill("input[name=email]", user_email)
        page.fill("input[name=password]", secure_password)
        page.click("button:has-text('Sign in')")
        page.wait_for_url(self.get_route_by_name("profile"))
        self.assertEqual(page.title(), "Your profile")
