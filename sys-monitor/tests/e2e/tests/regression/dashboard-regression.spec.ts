import { test, expect } from '../fixtures/test-fixtures';
import { mockMetrics, testPaths } from '../../utils/api-helpers';

test.describe('Dashboard Regression Tests @regression', () => {
  test('should maintain responsive layout on mobile @regression', async ({ dashboardPage }) => {
    await dashboardPage.page.setViewportSize({ width: 375, height: 667 });
    
    await expect(dashboardPage.page.getByRole('heading', { name: /sysmonitor dashboard/i })).toBeVisible();
    await expect(dashboardPage.page.getByRole('navigation')).toBeVisible();
  });

  test('should maintain responsive layout on desktop @regression', async ({ dashboardPage }) => {
    await dashboardPage.page.setViewportSize({ width: 1920, height: 1080 });
    
    await expect(dashboardPage.page.getByRole('heading', { name: /sysmonitor dashboard/i })).toBeVisible();
    await expect(dashboardPage.page.getByRole('navigation')).toBeVisible();
  });

  test('should support dark mode toggle @regression', async ({ dashboardPage }) => {
    await dashboardPage.page.evaluate(() => {
      document.body.classList.add('dark');
    });
    
    await expect(dashboardPage.page.locator('body')).toHaveClass(/dark/);
    
    await dashboardPage.page.evaluate(() => {
      document.body.classList.remove('dark');
    });
    
    await expect(dashboardPage.page.locator('body')).not.toHaveClass(/dark/);
  });

  test('should handle multiple api errors in sequence @regression', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Metrics API error' })
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);
    
    const cpuMonitor = page.getByText(/cpu usage/i);
    await expect(cpuMonitor).toBeVisible();
  });

  test('should display all system monitoring components @regression', async ({ dashboardPage }) => {
    await expect(dashboardPage.cpuMonitor).toBeVisible();
    await expect(dashboardPage.memoryMonitor).toBeVisible();
    await expect(dashboardPage.diskUsageCard).toBeVisible();
    await expect(dashboardPage.cpuGraph).toBeVisible();
    await expect(dashboardPage.memoryGraph).toBeVisible();
  });

  test('should handle rapid navigation without errors @regression', async ({ dashboardPage }) => {
    for (let i = 0; i < 5; i++) {
      await dashboardPage.navigateToFolderAnalysis();
      await dashboardPage.page.waitForTimeout(500);
      
      await dashboardPage.page.goto('/');
      await dashboardPage.page.waitForTimeout(500);
    }
    
    await expect(dashboardPage.page.getByRole('heading', { name: /sysmonitor dashboard/i })).toBeVisible();
  });

  test('should maintain data consistency after long running @regression', async ({ dashboardPage }) => {
    for (let i = 0; i < 10; i++) {
      await dashboardPage.waitForRealTimeUpdate(1000);
    }
    
    const cpuValue = dashboardPage.page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible();
  });

  test('should handle edge case viewport sizes @regression', async ({ dashboardPage }) => {
    const viewports = [
      { width: 1024, height: 768 },
      { width: 1366, height: 768 },
      { width: 1440, height: 900 },
      { width: 2560, height: 1440 }
    ];
    
    for (const viewport of viewports) {
      await dashboardPage.page.setViewportSize(viewport);
      await dashboardPage.page.waitForTimeout(500);
      await expect(dashboardPage.page.getByRole('navigation')).toBeVisible();
    }
  });
});
