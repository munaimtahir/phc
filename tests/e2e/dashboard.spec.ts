import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';
import { env } from './helpers/env';

test.describe('Dashboard', () => {
  test.skip(!env.username || !env.password, 'Credentials required.');

  test('dashboard cards and expected sections are visible', async ({ page }) => {
    await login(page);

    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /indicator status/i })).toBeVisible();
    await expect(page.getByText(/118\s+Total/i)).toBeVisible();
    await expect(page.getByText(/verified/i)).toBeVisible();
    await expect(page.getByText(/ready/i)).toBeVisible();
    await expect(page.getByText(/partial/i)).toBeVisible();
    await expect(page.getByText(/missing/i)).toBeVisible();
    await expect(page.getByRole('heading', { name: /quick stats/i })).toBeVisible();
    await expect(page.getByText(/recent updates/i)).toBeVisible();

    await expect(page.locator('table tbody tr').first()).toBeVisible();

    const sidebarBox = await page.locator('nav.sidebar').boundingBox();
    const firstMainCardBox = await page.locator('main .card').first().boundingBox();
    expect(sidebarBox).not.toBeNull();
    expect(firstMainCardBox).not.toBeNull();
    if (sidebarBox && firstMainCardBox) {
      expect(firstMainCardBox.x).toBeGreaterThanOrEqual(sidebarBox.x + sidebarBox.width - 1);
    }
  });
});
