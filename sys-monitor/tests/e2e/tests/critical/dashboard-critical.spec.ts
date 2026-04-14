import { test, expect } from '../fixtures/test-fixtures';
import { mockMetrics } from '../../utils/api-helpers';

test.describe('Dashboard Critical Tests @critical', () => {
  test('should display real-time metrics updates @critical', async ({ dashboardPage }) => {
    const initialCpuValue = await dashboardPage.getCpuUsage();
    
    await dashboardPage.waitForRealTimeUpdate(2000);
    
    const updatedCpuValue = await dashboardPage.getCpuUsage();
    
    expect(initialCpuValue).not.toBe(updatedCpuValue);
  });

  test('should display cpu graph component @critical', async ({ dashboardPage }) => {
    await expect(dashboardPage.cpuGraph).toBeVisible();
  });

  test('should display memory graph component @critical', async ({ dashboardPage }) => {
    await expect(dashboardPage.memoryGraph).toBeVisible();
  });

  test('should handle metrics api errors gracefully @critical', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });

    await page.goto('/');
    await page.waitForTimeout(3000);
    
    const cpuMonitor = page.getByText(/cpu usage/i);
    await expect(cpuMonitor).toBeVisible();
  });

  test('should mock high cpu usage scenario @critical', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 95.2,
          memory_usage: mockMetrics.memory.high.used,
          memory_total: mockMetrics.memory.high.total,
          disk_usage: mockMetrics.disk.high.usage,
          disk_total: mockMetrics.disk.high.total
        })
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);
    
    const cpuValue = page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible();
  });

  test('should maintain navigation visibility @critical', async ({ dashboardPage }) => {
    await expect(dashboardPage.dashboardLink).toBeVisible();
    await expect(dashboardPage.folderAnalysisLink).toBeVisible();
  });
});
