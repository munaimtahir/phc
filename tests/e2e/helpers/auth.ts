import { Page, expect } from '@playwright/test';
import { env } from './env';

export async function login(page: Page): Promise<void> {
  if (!env.username || !env.password) {
    throw new Error('PLAYWRIGHT_USERNAME and PLAYWRIGHT_PASSWORD are required for authenticated tests.');
  }

  await page.goto('/accounts/login/');
  await expect(page.getByRole('heading', { name: /please sign in/i })).toBeVisible();

  await page.fill('#id_username', env.username);
  await page.fill('#id_password', env.password);
  await page.getByRole('button', { name: /sign in/i }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
}

export async function isDashboardRouteAvailable(page: Page): Promise<boolean> {
  const response = await page.request.get('/dashboard/', { failOnStatusCode: false });
  return response.status() !== 404;
}
