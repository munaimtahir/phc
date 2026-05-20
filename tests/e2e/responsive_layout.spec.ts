import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

const viewports = [
  { width: 1440, height: 900 },
  { width: 1280, height: 800 },
  { width: 1024, height: 768 },
  { width: 768, height: 900 },
  { width: 390, height: 844 },
];

const pages = [
  { path: '/', name: 'Dashboard' },
  { path: '/indicators/', name: 'Indicators List' },
  { path: '/indicators/1/', name: 'Indicator Detail' },
  { path: '/evidence/', name: 'Evidence' },
  { path: '/registers/', name: 'Registers' },
  { path: '/reports/', name: 'Reports' },
];

test.describe('Responsive Layout - Horizontal Overflow', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  for (const viewport of viewports) {
    for (const target of pages) {
      test(`No horizontal scroll on ${target.name} at ${viewport.width}x${viewport.height}`, async ({ page }) => {
        await page.setViewportSize(viewport);
        await page.goto(target.path);

        // Wait for content to settle
        await page.waitForLoadState('networkidle');

        const overflowCheck = await page.evaluate(() => {
          const docWidth = document.documentElement.scrollWidth;
          const bodyWidth = document.body.scrollWidth;
          const winWidth = window.innerWidth;
          
          return {
            docWidth,
            bodyWidth,
            winWidth,
            hasDocOverflow: docWidth > winWidth + 2,
            hasBodyOverflow: bodyWidth > winWidth + 2
          };
        });

        expect(overflowCheck.hasDocOverflow, 
          `Page ${target.path} has horizontal overflow (Document: ${overflowCheck.docWidth}px > Window: ${overflowCheck.winWidth}px)`
        ).toBe(false);

        expect(overflowCheck.hasBodyOverflow, 
          `Page ${target.path} has horizontal overflow (Body: ${overflowCheck.bodyWidth}px > Window: ${overflowCheck.winWidth}px)`
        ).toBe(false);
        
        // Assert main content is visible
        const main = page.locator('main[role="main"]');
        await expect(main).toBeVisible();
      });
    }
  }
});
