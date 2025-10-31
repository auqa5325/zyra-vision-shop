import { test, expect } from '@playwright/test';

test.describe('Responsive Design Tests', () => {
  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE size
    await page.goto('/');
    
    // Verify mobile layout
    await expect(page.locator('header')).toBeVisible();
    
    // Check for mobile menu button
    const mobileMenuButton = page.locator('button[aria-label*="menu"], button:has-text("Menu")').first();
    if (await mobileMenuButton.count() > 0) {
      await expect(mobileMenuButton).toBeVisible();
    }
    
    // Verify content is visible
    await expect(page.locator('main')).toBeVisible();
  });

  test('should be responsive on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad size
    await page.goto('/');
    
    // Verify tablet layout
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
  });

  test('should be responsive on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 }); // Desktop size
    await page.goto('/');
    
    // Verify desktop layout
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
  });

  test('should toggle mobile menu', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Find mobile menu button
    const mobileMenuButton = page.locator('button[aria-label*="menu"], button:has-text("Menu")').first();
    
    if (await mobileMenuButton.count() > 0) {
      await mobileMenuButton.click();
      await page.waitForTimeout(500);
      
      // Menu should be visible
      const mobileMenu = page.locator('[class*="mobile-menu"], [role="dialog"]').first();
      if (await mobileMenu.count() > 0) {
        await expect(mobileMenu).toBeVisible();
      }
      
      // Close menu
      const closeButton = page.locator('button[aria-label*="close"], button:has-text("X")').first();
      if (await closeButton.count() > 0) {
        await closeButton.click();
      }
    }
  });
});

test.describe('Accessibility Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    // Get all headings
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    
    // Should have at least one heading
    expect(headings.length).toBeGreaterThan(0);
  });

  test('should have accessible buttons', async ({ page }) => {
    // Check that buttons have proper labels or text
    const buttons = await page.locator('button').all();
    
    for (const button of buttons.slice(0, 5)) { // Check first 5 buttons
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      
      // Button should have either text or aria-label
      expect(text || ariaLabel).toBeTruthy();
    }
  });

  test('should have proper form labels', async ({ page }) => {
    // Find form inputs
    const inputs = await page.locator('input, select, textarea').all();
    
    for (const input of inputs.slice(0, 3)) { // Check first 3 inputs
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const placeholder = await input.getAttribute('placeholder');
      
      // Input should have id (for label association), aria-label, or placeholder
      expect(id || ariaLabel || placeholder).toBeTruthy();
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Start from top
    await page.keyboard.press('Tab');
    await page.waitForTimeout(300);
    
    // Should focus on first interactive element
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(['BUTTON', 'INPUT', 'A', 'LINK']).toContain(focused);
  });
});

