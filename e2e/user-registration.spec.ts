
import { test, expect } from '@playwright/test';

test('user registration and onboarding', async ({ page }) => {
  // First of all they visit the login page
  await page.goto('/accounts/login/');
  await expect(page).toHaveTitle('Sign In');

  // They see a link to sign up and click it
  await page.click("a:has-text('Sign up')");
  await page.waitForURL('/accounts/signup/');
  await expect(page).toHaveTitle('Signup');

  // They enter their email address and password and submit the form
  const insecurePassword = 'password';
  await page.fill('input[name=email]', 'test@example.com');
  await page.fill('input[name=password1]', insecurePassword);
  await page.fill('input[name=password2]', insecurePassword);
  await page.click("button:has-text('Sign up')");

  // Unfortunately the password is too insecure and they are redirected back to the signup page
  // with some validation errors
  await page.waitForURL('/accounts/signup/');
  await expect(page).toHaveTitle('Signup');
  const errorlist = page.locator('ul.errorlist');
  await expect(errorlist).toBeVisible();
  await expect(errorlist).toContainText('This password is too common.');
  await expect(errorlist).toContainText('This password is too short.');

  // They try again with a more secure password
  const securePassword = "I'm4S3cur3P@ssw0rd!";
  await page.fill('input[name=password1]', securePassword);
  await page.fill('input[name=password2]', securePassword);
  await page.click("button:has-text('Sign up')");
  await page.waitForURL('/accounts/email/sent/');

  // For the purpose of this test, we'll skip the email verification and go straight to the profile page
  await page.goto('/profile/');
  await expect(page).toHaveTitle('Your profile');

  // They refresh the profile page and it works as expected
  await page.reload();
  await expect(page).toHaveTitle('Your profile');

  // When they log out they are redirected to the login page
  await page.click("a:has-text('Sign out')");
  await page.waitForURL('/accounts/logout/');

  await page.click("button:has-text('Sign Out')");
  await page.waitForURL('/accounts/login/');

  // If they're not logged in they can't access the profile page
  // and are redirected to the login page
  await page.goto('/profile/');
  await page.waitForURL('/accounts/login/');

  // They log in and are redirected back to the profile page
  await page.goto('/accounts/login/');
  await page.fill('input[name=email]', 'test@example.com');
  await page.fill('input[name=password]', securePassword);
  await page.click("button:has-text('Sign in')");
  await page.waitForURL('/profile/');
  await expect(page).toHaveTitle('Your profile');
});
