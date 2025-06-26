import { test, expect } from '@playwright/test';
import { faker } from '@faker-js/faker';
import fs from 'fs/promises';

const mailDir = "mail";

const getLatestEmail = async (emailDir: string): Promise<string> => {
  const files = await fs.readdir(emailDir);
  const latestFile = files.filter((file) => file.endsWith('.log')).sort().pop();
  const email = await fs.readFile(`${emailDir}/${latestFile}`, 'utf8');
  return email;
};

const extractVerificationCode = (emailBody: string): string | null => {
  // Find the line after the prompt text
  const lines = emailBody.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.includes("Your email verification code is listed below")) {
      // The code is on the next non-empty line
      for (let j = i + 1; j < lines.length; j++) {
        const potentialCode = lines[j];
        if (potentialCode.trim()) {
          return potentialCode.trim();
        }
      }
    }
  }
  return null;
};

test('user registration and onboarding', async ({ page }) => {
  const email = faker.internet.email({ provider: 'example.com' });

  // First of all they visit the login page
  await page.goto('/accounts/login/');
  await expect(page).toHaveTitle('Sign In');

  // They see a link to sign up and click it
  await page.click("a:has-text('Sign up')");
  await page.waitForURL('/accounts/signup/');
  await expect(page).toHaveTitle('Signup');

  // They enter their email address and password and submit the form
  const insecurePassword = 'password';
  await page.fill('input[name=email]', email);
  await page.fill('input[name=password1]', insecurePassword);
  await page.fill('input[name=password2]', insecurePassword);
  await page.click("button:has-text('Sign up')");

  // Unfortunately the password is too insecure and they are redirected back to the signup page
  // with some validation errors
  await page.waitForURL('/accounts/signup/');
  await expect(page).toHaveTitle('Signup');
  const signupErrorlist = page.locator('ul.errorlist');
  await expect(signupErrorlist).toBeVisible();
  await expect(signupErrorlist).toContainText('This password is too common.');
  await expect(signupErrorlist).toContainText('This password is too short.');

  // They try again with a more secure password
  const securePassword = "I'm4S3cur3P@ssw0rd!";
  await page.fill('input[name=password1]', securePassword);
  await page.fill('input[name=password2]', securePassword);
  await page.click("button:has-text('Sign up')");
  await page.waitForURL('/accounts/confirm-email/');

  // They enter an incorrect verification code
  const incorrectVerificationCode = '1234567890';
  await page.getByRole('textbox', { name: 'Code' }).fill(incorrectVerificationCode);
  await page.click("button:has-text('Confirm')");

  // They see an error message
  const confirmEmailErrorlist = page.locator('ul.errorlist');
  await expect(confirmEmailErrorlist).toBeVisible();
  await expect(confirmEmailErrorlist).toContainText('Incorrect code');

  // They try again with the correct verification code
  const latestEmail = await getLatestEmail(mailDir);
  const verificationCode = extractVerificationCode(latestEmail);
  if (!verificationCode) {
    throw new Error('No verification code found');
  }
  await page.getByRole('textbox', { name: 'Code' }).fill(verificationCode);
  await page.click("button:has-text('Confirm')");

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
  await page.waitForURL((u) => u.pathname.startsWith('/accounts/login/'));

  // They log in and are redirected back to the profile page
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Password Forgot your password?' }).fill(securePassword);
  await page.click("button:has-text('Sign in')");
  await page.waitForURL((u) => u.pathname.startsWith('/profile/'));
  await expect(page).toHaveTitle('Your profile');
});
