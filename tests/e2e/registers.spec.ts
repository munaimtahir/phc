import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';
import { env } from './helpers/env';

test.describe('Registers workflow', () => {
  test.skip(!env.username || !env.password, 'Credentials required.');

  test('register list read-only checks', async ({ page }) => {
    await login(page);
    await page.goto('/registers/');

    await expect(page.getByRole('heading', { name: /digital registers/i })).toBeVisible();
    const cards = page.locator('.card:has(a:has-text("View Log"))');
    await expect(cards.first()).toBeVisible();

    const cardCount = await cards.count();
    expect(cardCount).toBeGreaterThanOrEqual(14);

    await expect(page.getByRole('link', { name: /view log/i }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: /add entry/i }).first()).toBeVisible();

    const sidebarBox = await page.locator('nav.sidebar').boundingBox();
    const firstCardBox = await cards.first().boundingBox();
    expect(sidebarBox).not.toBeNull();
    expect(firstCardBox).not.toBeNull();
    if (sidebarBox && firstCardBox) {
      expect(firstCardBox.x).toBeGreaterThanOrEqual(sidebarBox.x + sidebarBox.width - 1);
    }
  });

  test('add register entry when mutation enabled', async ({ page }) => {
    test.skip(!env.allowMutation, 'Mutation disabled: set PLAYWRIGHT_ALLOW_MUTATION=true to run write tests.');

    await login(page);
    await page.goto('/registers/');

    await page.getByRole('link', { name: /add entry/i }).first().click();
    await expect(page.getByRole('heading', { name: /add entry:/i })).toBeVisible();

    const today = new Date().toISOString().slice(0, 10);
    await page.locator('input[name="entry_date"]').fill(today);

    const firstField = page.locator('input[name^="field_"]').first();
    if (await firstField.count()) {
      await firstField.fill(`E2E value ${Date.now()}`);
    }
    await page.locator('textarea[name="remarks"]').fill(`Playwright mutation test ${Date.now()}`);

    await page.getByRole('button', { name: /save entry/i }).click();
    await expect(page).toHaveURL(/\/registers\/\d+\/$/);
    await expect(page.locator('table')).toBeVisible();
    await expect(page.getByText('Playwright mutation test')).toBeVisible();
  });
});
