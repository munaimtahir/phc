import { test, expect } from '@playwright/test';
import { env } from './helpers/env';

test.describe('Authentication flow', () => {
  test('login page opens', async ({ page }) => {
    await page.goto('/accounts/login/');
    await expect(page.getByRole('heading', { name: /please sign in/i })).toBeVisible();
    await expect(page.locator('#id_username')).toBeVisible();
    await expect(page.locator('#id_password')).toBeVisible();
  });

  test('valid login works and dashboard remains accessible', async ({ page }) => {
    test.skip(!env.username || !env.password, 'Credentials required.');

    await page.goto('/accounts/login/');
    await page.fill('#id_username', env.username);
    await page.fill('#id_password', env.password);
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

    await page.goto('/indicators/');
    await expect(page).not.toHaveURL(/\/accounts\/login\//);
    await expect(page.getByRole('heading', { name: /indicators master checklist/i })).toBeVisible();
  });

  test('logout works when available', async ({ page }) => {
    test.skip(!env.username || !env.password, 'Credentials required.');

    await page.goto('/accounts/login/');
    await page.fill('#id_username', env.username);
    await page.fill('#id_password', env.password);
    await page.getByRole('button', { name: /sign in/i }).click();

    await page.getByRole('button', { name: /sign out/i }).click();
    await expect(page).toHaveURL(/\/accounts\/login\//);
    await expect(page.getByRole('heading', { name: /please sign in/i })).toBeVisible();
  });
});
