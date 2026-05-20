import { expect, Locator, Page } from '@playwright/test';

export async function assertNoServerTemplateErrors(page: Page): Promise<void> {
  await expect(page.locator('body')).not.toContainText('TemplateSyntaxError');
  await expect(page.locator('body')).not.toContainText('Invalid block tag');
  await expect(page.locator('body')).not.toContainText('Server Error (500)');
  await expect(page.locator('body')).not.toContainText('Traceback');
}

export async function assertNoHorizontalOverlap(sidebar: Locator, main: Locator): Promise<void> {
  const sidebarBox = await sidebar.boundingBox();
  const mainBox = await main.boundingBox();

  expect(sidebarBox).not.toBeNull();
  expect(mainBox).not.toBeNull();

  if (!sidebarBox || !mainBox) return;

  expect(mainBox.x).toBeGreaterThanOrEqual(sidebarBox.x + sidebarBox.width - 1);
}

export async function assertHeadingVisible(page: Page, headingPattern: RegExp): Promise<void> {
  await expect(page.getByRole('heading', { name: headingPattern })).toBeVisible();
}
