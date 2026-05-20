import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';
import { env } from './helpers/env';

test.describe('Evidence workflow', () => {
  test.skip(!env.username || !env.password, 'Credentials required.');

  test('evidence read-only view loads expected controls', async ({ page }) => {
    await login(page);
    await page.goto('/evidence/');

    await expect(page.getByRole('heading', { name: /evidence library/i })).toBeVisible();
    await expect(page.locator('input[name="q"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /search/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /clear/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /add evidence/i })).toBeVisible();
    await expect(page.locator('table')).toBeVisible();

    const bodyText = await page.locator('body').innerText();
    if (bodyText.includes('No evidence uploaded yet.')) {
      await expect(page.getByText(/No evidence uploaded yet\./i)).toBeVisible();
    } else {
      await expect(page.locator('table thead')).toContainText('Evidence Title');
      await expect(page.locator('table thead')).toContainText('Linked Indicators');
    }
  });

  test('create evidence through admin when mutation enabled', async ({ page }) => {
    test.skip(!env.allowMutation, 'Mutation disabled: set PLAYWRIGHT_ALLOW_MUTATION=true to run write tests.');

    await login(page);

    await page.goto('/admin/evidence/evidenceitem/add/');
    await expect(page.getByRole('heading', { name: /add evidence item/i })).toBeVisible();

    const testTitle = `PW E2E Evidence ${Date.now()}`;
    await page.locator('#id_title').fill(testTitle);
    await page.locator('#id_evidence_type').selectOption({ label: 'Other' });
    await page.locator('#id_external_url').fill('https://example.com/e2e-evidence');

    await page.locator('#id_linked_indicators_from').selectOption({ label: /IND-001/ });
    await page.getByRole('link', { name: 'Add' }).first().click();

    await page.getByRole('button', { name: /save/i }).click();
    await expect(page.locator('.messagelist, .success')).toContainText(/was added successfully/i);

    await page.goto('/evidence/');
    await page.fill('input[name="q"]', testTitle);
    await page.getByRole('button', { name: /search/i }).click();

    await expect(page.getByText(testTitle)).toBeVisible();
    await expect(page.getByText('IND-001')).toBeVisible();
  });
});
