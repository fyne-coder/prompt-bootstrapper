const { test, expect } = require('@playwright/test');

test.describe('Generate10 Page', () => {
  test.beforeEach(async ({ page }) => {
    const context = page.context();
    // Stub JSON response
    await context.route('**/generate10/json', async (route) => {
      // Stub grouped prompts: single category 'Test'
      const grouped = { Test: Array.from({ length: 10 }, (_, i) => `P${i}`) };
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          prompts: grouped,
          logo_url: null,
          palette: ['#123456', '#abcdef'],
        }),
      });
    });
    // Stub PDF response
    await context.route('**/generate10/pdf', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/pdf',
        body: Buffer.from('%PDF-FAKE'),
      });
    });
  });

  test('renders prompt list and downloads PDF', async ({ page }) => {
    await page.goto('/');
    // Generate prompts
    await page.fill('input[type="url"]', 'https://example.com');
    await page.click('button:has-text("Generate")');
    // Check list of prompts
    const items = page.locator('ol li');
    await expect(items).toHaveCount(10);
    for (let i = 0; i < 10; i++) {
      await expect(items.nth(i)).toContainText(`P${i}`);
    }
    // Download PDF
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Download PDF")'),
    ]);
    // Verify suggested filename
    expect(download.suggestedFilename()).toBe('prompts10.pdf');
  });
});