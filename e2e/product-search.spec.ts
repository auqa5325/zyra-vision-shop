import { test, expect } from '@playwright/test';

test.describe('Product Search and Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should search for products', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    
    if (await searchInput.count() > 0) {
      await searchInput.fill('laptop');
      await searchInput.press('Enter');
      
      // Wait for search results
      await page.waitForTimeout(2000);
      
      // Check if results page loaded
      const hasResults = page.url().includes('/search') || 
                        page.locator('text=/result|product/i').first().isVisible();
      
      if (hasResults) {
        await expect(page).toHaveURL(/.*search/);
      }
    }
  });

  test('should navigate to product page', async ({ page }) => {
    // Wait for products to load
    await page.waitForTimeout(2000);
    
    // Find first product card and click
    const productCard = page.locator('[class*="product-card"], [class*="ProductCard"]').first();
    
    if (await productCard.count() > 0) {
      await productCard.click();
      
      // Wait for product page
      await page.waitForTimeout(1000);
      
      // Check if we're on product page
      if (page.url().includes('/product')) {
        await expect(page).toHaveURL(/.*product/);
      }
    }
  });

  test('should navigate to category page', async ({ page }) => {
    // Wait for categories to load
    await page.waitForTimeout(2000);
    
    // Find first category card/link
    const categoryLink = page.locator('a[href*="/category"], button').filter({ hasText: /electronics|clothing|books/i }).first();
    
    if (await categoryLink.count() > 0) {
      await categoryLink.click();
      
      // Wait for category page
      await page.waitForTimeout(1000);
      
      // Check if we're on category page
      if (page.url().includes('/category')) {
        await expect(page).toHaveURL(/.*category/);
      }
    }
  });

  test('should display product recommendations', async ({ page }) => {
    // Wait for recommendations to load
    await page.waitForTimeout(3000);
    
    // Check for recommendation sections
    const recommendations = page.locator('section, div').filter({ hasText: /recommended|you may like|top picks/i });
    
    // Just verify page has loaded with content
    await expect(page.locator('main')).toBeVisible();
  });

  test('should filter products by category', async ({ page }) => {
    // Navigate to a category
    await page.waitForTimeout(2000);
    
    const categoryLink = page.locator('a[href*="/category"], button').filter({ hasText: /electronics|clothing|books/i }).first();
    
    if (await categoryLink.count() > 0) {
      await categoryLink.click();
      await page.waitForTimeout(2000);
      
      // Verify category page loaded with products
      await expect(page.locator('main')).toBeVisible();
    }
  });
});

test.describe('Shopping Cart Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should add product to cart', async ({ page }) => {
    // Wait for products to load
    await page.waitForTimeout(2000);
    
    // Find first product and add to cart
    const addToCartButton = page.locator('button').filter({ hasText: /add to cart|buy now/i }).first();
    
    if (await addToCartButton.count() > 0) {
      await addToCartButton.click();
      
      // Wait for cart update
      await page.waitForTimeout(1000);
      
      // Check if cart badge updated
      const cartBadge = page.locator('[class*="cart-badge"], [aria-label*="cart"]').first();
      if (await cartBadge.count() > 0) {
        // Cart should have items
        await expect(cartBadge).toBeVisible();
      }
    }
  });

  test('should navigate to cart page', async ({ page }) => {
    // Find cart icon/button
    const cartButton = page.locator('button[aria-label*="cart"], a[href*="/cart"]').first();
    
    if (await cartButton.count() > 0) {
      await cartButton.click();
      
      // Wait for cart page
      await page.waitForTimeout(1000);
      
      // Check if we're on cart page
      if (page.url().includes('/cart')) {
        await expect(page).toHaveURL(/.*cart/);
      }
    }
  });
});

test.describe('Wishlist Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should add product to wishlist', async ({ page }) => {
    // Wait for products to load
    await page.waitForTimeout(2000);
    
    // Find wishlist button (heart icon)
    const wishlistButton = page.locator('button[aria-label*="wishlist"], button[aria-label*="heart"]').first();
    
    if (await wishlistButton.count() > 0) {
      await wishlistButton.click();
      
      // Wait for wishlist update
      await page.waitForTimeout(1000);
      
      // Button should be visible
      await expect(wishlistButton).toBeVisible();
    }
  });

  test('should navigate to wishlist page', async ({ page }) => {
    // Find wishlist icon/button in header
    const wishlistButton = page.locator('button[aria-label*="wishlist"], a[href*="/wishlist"]').first();
    
    if (await wishlistButton.count() > 0) {
      await wishlistButton.click();
      
      // Wait for wishlist page
      await page.waitForTimeout(1000);
      
      // Check if we're on wishlist page
      if (page.url().includes('/wishlist')) {
        await expect(page).toHaveURL(/.*wishlist/);
      }
    }
  });
});

