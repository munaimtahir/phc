import { test, expect } from '@playwright/test';
import { assertNoServerTemplateErrors } from './helpers/assertions';
import { login, isDashboardRouteAvailable } from './helpers/auth';
import { env } from './helpers/env';

test.describe('Smoke routes', () => {
  test.skip(!env.username || !env.password, 'Credentials required for authenticated smoke routes.');

  test('core pages load without template/runtime server errors', async ({ page }) => {
    await login(page);

    const routes: { path: string; expectedText: RegExp }[] = [
      { path: '/', expectedText: /dashboard/i },
      { path: '/indicators/', expectedText: /indicators master checklist/i },
      { path: '/evidence/', expectedText: /evidence library/i },
      { path: '/registers/', expectedText: /digital registers/i },
      { path: '/reports/', expectedText: /reports & exports/i },
    ];

    if (await isDashboardRouteAvailable(page)) {
      routes.splice(1, 0, { path: '/dashboard/', expectedText: /dashboard/i });
    }

    for (const route of routes) {
      const response = await page.goto(route.path, { waitUntil: 'domcontentloaded' });
      expect(response, `No response for ${route.path}`).not.toBeNull();
      expect(response!.status(), `${route.path} returned HTTP ${response!.status()}`).toBeLessThan(500);
      await assertNoServerTemplateErrors(page);
      await expect(page.getByText(route.expectedText)).toBeVisible();
    }
  });
});
