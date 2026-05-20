import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';
import { assertHeadingVisible, assertNoHorizontalOverlap } from './helpers/assertions';
import { env } from './helpers/env';

const viewports = [
  { width: 1366, height: 768 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
];

const pages = [
  { path: '/', heading: /dashboard/i },
  { path: '/indicators/', heading: /indicators master checklist/i },
  { path: '/evidence/', heading: /evidence library/i },
  { path: '/registers/', heading: /digital registers/i },
  { path: '/reports/', heading: /reports & exports/i },
];

test.describe('Global layout', () => {
  test.skip(!env.username || !env.password, 'Credentials required for protected pages.');

  for (const viewport of viewports) {
    test(`no sidebar/content overlap at ${viewport.width}x${viewport.height}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await login(page);

      for (const target of pages) {
        await page.goto(target.path);
        await assertHeadingVisible(page, target.heading);

        const sidebar = page.locator('nav.sidebar');
        const main = page.locator('main[role="main"]');
        await expect(sidebar).toBeVisible();
        await expect(main).toBeVisible();
        await assertNoHorizontalOverlap(sidebar, main);

        const firstCardOrTable = page.locator('.card, table').first();
        await expect(firstCardOrTable).toBeVisible();
        const box = await firstCardOrTable.boundingBox();
        expect(box).not.toBeNull();
        if (box) {
          expect(box.x + box.width).toBeLessThanOrEqual(viewport.width + 1);
          expect(box.y + box.height).toBeGreaterThan(0);
        }
      }
    });
  }
});
