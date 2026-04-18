import { test, expect } from '../fixtures/test-fixtures';

// Skip visual regression tests in CI as snapshots are not committed
test.describe.skip('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await new Promise(r => setTimeout(r, 2000));
  });

  test('dashboard baseline visual regression', async ({ page }) => {
    await expect(page).toHaveScreenshot('dashboard-baseline.png', {
      fullPage: false,
      maxDiffPixels: 100,
      mask: [
        page.locator('[data-dynamic]'),
        page.locator('[class*="animate-"]')
      ]
    });
  });

  test('dashboard cpu monitor visual regression', async ({ page }) => {
    const cpuMonitor = page.getByText(/cpu usage/i).first();
    await expect(cpuMonitor).toBeVisible();
    
    await expect(page).toHaveScreenshot('dashboard-cpu-monitor.png', {
      mask: [
        page.locator('text=%'),
        page.locator('[data-dynamic]')
      ],
      maskColor: '#00FF00'
    });
  });

  test('dashboard memory monitor visual regression', async ({ page }) => {
    const memoryMonitor = page.getByText(/memory usage/i).first();
    await expect(memoryMonitor).toBeVisible();
    
    await expect(page).toHaveScreenshot('dashboard-memory-monitor.png', {
      mask: [
        page.locator('text=GB'),
        page.locator('[data-dynamic]')
      ],
      maskColor: '#00FF00'
    });
  });

  test('folder analysis page visual regression', async ({ page }) => {
    await page.goto('/folder-analysis');
    await page.waitForLoadState('networkidle');
    await new Promise(r => setTimeout(r, 2000));
    
    await expect(page).toHaveScreenshot('folder-analysis-baseline.png', {
      fullPage: true,
      maxDiffPixels: 150
    });
  });

  test('folder analysis input visual regression', async ({ page }) => {
    await page.goto('/folder-analysis');
    await page.waitForLoadState('networkidle');
    
    const pathInput = page.getByPlaceholder(/.*文件夹路径.*/);
    await expect(pathInput).toBeVisible();
    
    await expect(page).toHaveScreenshot('folder-analysis-input.png', {
      mask: [
        page.locator('input'),
        page.locator('[data-dynamic]')
      ]
    });
  });

  test('mobile viewport visual regression', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await new Promise(r => setTimeout(r, 1000));
    
    await expect(page).toHaveScreenshot('dashboard-mobile.png', {
      fullPage: true,
      maxDiffPixels: 200
    });
  });

  test('tablet viewport visual regression', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await new Promise(r => setTimeout(r, 1000));
    
    await expect(page).toHaveScreenshot('dashboard-tablet.png', {
      fullPage: true,
      maxDiffPixels: 150
    });
  });

  test('dark mode visual regression', async ({ page }) => {
    await page.evaluate(() => {
      document.body.classList.add('dark');
    });
    await new Promise(r => setTimeout(r, 1000));
    
    await expect(page).toHaveScreenshot('dashboard-dark-mode.png', {
      fullPage: false,
      maxDiffPixels: 300
    });
  });
});
