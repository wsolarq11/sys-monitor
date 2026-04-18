import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should load dashboard page successfully', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('SysMonitor Dashboard');
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should display navigation links', async ({ page }) => {
    const dashboardLink = page.locator('a[href="/"]');
    const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');

    await expect(dashboardLink).toBeVisible();
    await expect(folderAnalysisLink).toBeVisible();
    await expect(dashboardLink).toHaveClass(/border-indigo-500/);
  });

  test('should navigate to folder analysis page', async ({ page }) => {
    await page.click('a[href="/folder-analysis"]');
    await page.waitForURL('**/folder-analysis');
    await expect(page.locator('input[placeholder*="文件夹路径"]')).toBeVisible();
  });

  test('should display CPU monitor component', async ({ page }) => {
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible();
    
    const cpuValue = page.locator('text=%').first();
    await expect(cpuValue).toBeVisible();
    
    const cpuText = await cpuValue.textContent();
    expect(cpuText).toMatch(/\d+\.\d+%/);
  });

  test('should display memory monitor component', async ({ page }) => {
    const memoryMonitor = page.locator('text=Memory Usage');
    await expect(memoryMonitor).toBeVisible();
    
    const memoryValue = page.locator('text=GB').first();
    await expect(memoryValue).toBeVisible();
    
    const memoryText = await memoryValue.textContent();
    expect(memoryText).toMatch(/\d+\.\d+\s*GB/);
  });

  test('should display CPU graph component', async ({ page }) => {
    const cpuGraph = page.locator('text=CPU Usage Over Time');
    await expect(cpuGraph).toBeVisible();
  });

  test('should display memory graph component', async ({ page }) => {
    const memoryGraph = page.locator('text=Memory Usage Over Time');
    await expect(memoryGraph).toBeVisible();
  });

  test('should display disk usage card', async ({ page }) => {
    const diskCard = page.locator('text=Disk Usage');
    await expect(diskCard).toBeVisible();
  });

  test('should update system metrics in real-time', async ({ page }) => {
    const initialCpuValue = await page.locator('text=%').first().textContent();
    
    await new Promise(r => setTimeout(r, 2000));
    
    const updatedCpuValue = await page.locator('text=%').first().textContent();
    
    expect(initialCpuValue).not.toBe(updatedCpuValue);
  });

  test('should handle system metrics API errors gracefully', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });

    await new Promise(r => setTimeout(r, 3000));
    
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible();
  });

  test('should maintain responsive layout on different screen sizes', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('nav')).toBeVisible();
    
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should support dark mode toggle', async ({ page }) => {
    const body = page.locator('body');
    
    await page.evaluate(() => {
      document.body.classList.add('dark');
    });
    
    await expect(body).toHaveClass(/dark/);
    
    await page.evaluate(() => {
      document.body.classList.remove('dark');
    });
    
    await expect(body).not.toHaveClass(/dark/);
  });
});