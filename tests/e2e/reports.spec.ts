import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';
import { env } from './helpers/env';

test.describe('Reports and print-pack', () => {
  test.skip(!env.username || !env.password, 'Credentials required.');

  test('reports index and linked reports behave correctly', async ({ page }) => {
    await login(page);
    await page.goto('/reports/');

    await expect(page.getByRole('heading', { name: /reports & exports/i })).toBeVisible();
    await expect(page.getByText(/missing evidence/i)).toBeVisible();
    await expect(page.getByText(/surveyor print pack/i)).toBeVisible();

    await page.getByRole('link', { name: /view missing/i }).click();
    await expect(page).toHaveURL(/\/reports\/missing-evidence\//);
    await expect(page.getByRole('heading', { name: /missing evidence report/i })).toBeVisible();

    await page.goto('/reports/');
    const packButton = page.getByRole('link', { name: /view print pack/i });
    const disabledPackButton = page.getByRole('button', { name: /no indicators ready yet/i });

    if (await packButton.count()) {
      await packButton.click();
      await expect(page).toHaveURL(/\/reports\/surveyor-pack\//);
      await expect(page.getByRole('heading', { name: /surveyor print pack index/i })).toBeVisible();
    } else {
      await expect(disabledPackButton).toBeVisible();
      await expect(page.getByText(/mark indicators as 'ready for print pack' to enable/i)).toBeVisible();
    }

    const sidebarBox = await page.locator('nav.sidebar').boundingBox();
    const firstCardBox = await page.locator('.card').first().boundingBox();
    expect(sidebarBox).not.toBeNull();
    expect(firstCardBox).not.toBeNull();
    if (sidebarBox && firstCardBox) {
      expect(firstCardBox.x).toBeGreaterThanOrEqual(sidebarBox.x + sidebarBox.width - 1);
    }
  });
});
