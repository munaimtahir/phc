import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';
import { assertNoServerTemplateErrors } from './helpers/assertions';
import { env } from './helpers/env';

test.describe('Indicators workflow', () => {
  test.skip(!env.username || !env.password, 'Credentials required.');

  test('indicators list and detail flow works', async ({ page }) => {
    await login(page);
    await page.goto('/indicators/');

    await assertNoServerTemplateErrors(page);
    await expect(page.getByRole('heading', { name: /indicators master checklist/i })).toBeVisible();
    await expect(page.locator('input[name="q"]')).toBeVisible();
    await expect(page.locator('select[name="area"]')).toBeVisible();
    await expect(page.locator('table')).toBeVisible();

    const rowCount = await page.locator('table tbody tr').count();
    expect(rowCount).toBeGreaterThan(0);

    const pageText = await page.locator('body').innerText();
    expect(pageText).toContain('IND-001');
    expect(pageText).toContain('IND-118');

    const firstDetailLink = page.locator('a', { hasText: 'IND-001' }).first();
    await firstDetailLink.click();
    await expect(page.getByRole('heading', { name: /indicator: ind-001/i })).toBeVisible();

    await page.goto('/indicators/');
    const statuses = ['Missing', 'Partial', 'Ready', 'Verified'];
    for (const label of statuses) {
      await expect(page.getByText(label)).toBeVisible();
    }
  });
});
