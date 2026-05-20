import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

test.describe('Evidence Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('can create evidence from indicator detail page', async ({ page }) => {
    // Go to indicators list
    await page.goto('/indicators/');
    
    // Click on the first indicator
    await page.click('table tbody tr:first-child a.fw-bold');
    
    // Capture indicator info
    const indicatorNo = await page.locator('h1.h2').innerText();
    
    // Click Add New Evidence
    await page.click('text=+ Add New Evidence');
    
    // Verify we are on the form and indicator context is present
    await expect(page).toHaveURL(/\/evidence\/add\/\?indicator=\d+/);
    await expect(page.locator('h1.h2')).toContainText('Add Evidence for Indicator');
    
    // Fill the form
    await page.fill('input[name="title"]', 'New Automated Evidence');
    await page.selectOption('select[name="evidence_type"]', 'SOP / Policy');
    await page.fill('textarea[name="description"]', 'This was created by Playwright');
    
    // Save
    await page.click('button[type="submit"]');
    
    // Should be redirected back to indicator detail
    await expect(page).toHaveURL(/\/indicators\/\d+\//);
    
    // Verify newly added evidence is in the list
    await expect(page.locator('.card:has-text("Linked Evidence Items")')).toContainText('New Automated Evidence');
  });

  test('can link existing evidence from library', async ({ page }) => {
    // First create a standalone evidence item
    await page.goto('/evidence/add/');
    await page.fill('input[name="title"]', 'Standalone Evidence');
    await page.selectOption('select[name="evidence_type"]', 'Other');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/evidence/');

    // Go to an indicator detail page
    await page.goto('/indicators/');
    await page.click('table tbody tr:nth-child(2) a.fw-bold');
    const indicatorUrl = page.url();

    // Click Browse Library to Link Existing
    await page.click('text=Browse Library to Link Existing');
    await expect(page).toHaveURL(/\/evidence\/\?link_to=\d+/);

    // Click Link to Indicator for our evidence
    await page.click('tr:has-text("Standalone Evidence") .btn-success:has-text("Link to Indicator")');

    // Should be redirected back to indicator detail
    await expect(page).toHaveURL(indicatorUrl);

    // Verify linked
    await expect(page.locator('.card:has-text("Linked Evidence Items")')).toContainText('Standalone Evidence');
  });
});
