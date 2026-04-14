import { test, expect } from '../fixtures/test-fixtures';

test.describe('Dashboard Smoke Tests @smoke', () => {
  test('should load dashboard page successfully @smoke', async ({ dashboardPage }) => {
    await expect(dashboardPage.page.getByRole('heading', { name: /sysmonitor dashboard/i })).toBeVisible();
    await expect(dashboardPage.page.getByRole('navigation')).toBeVisible();
  });

  test('should display cpu monitor component @smoke', async ({ dashboardPage }) => {
    await expect(dashboardPage.cpuMonitor).toBeVisible();
    
    const cpuValue = dashboardPage.page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible();
  });

  test('should display memory monitor component @smoke', async ({ dashboardPage }) => {
    await expect(dashboardPage.memoryMonitor).toBeVisible();
    
    const memoryValue = dashboardPage.page.getByText(/gb/i).first();
    await expect(memoryValue).toBeVisible();
  });

  test('should navigate to folder analysis page @smoke', async ({ dashboardPage }) => {
    await dashboardPage.navigateToFolderAnalysis();
    await expect(dashboardPage.page).toHaveURL(/.*folder-analysis/);
  });

  test('should display disk usage card @smoke', async ({ dashboardPage }) => {
    await expect(dashboardPage.diskUsageCard).toBeVisible();
  });
});
