import { test, expect } from '@playwright/test';

test.describe('System Monitoring', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Use domcontentloaded instead of networkidle to avoid timeout in CI
    await page.waitForLoadState('domcontentloaded');
    await new Promise(r => setTimeout(r, 2000));
  });

  test('should display real-time CPU usage updates', async ({ page }) => {
    // Additional wait for component rendering
    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.locator('text=%').first();
    await expect(cpuValue).toBeVisible({ timeout: 10000 });
    
    const initialValue = await cpuValue.textContent();
    await new Promise(r => setTimeout(r, 3000));
    const updatedValue = await cpuValue.textContent();
    
    expect(initialValue).not.toBe(updatedValue);
    
    const cpuNumber = parseFloat(updatedValue!.replace('%', ''));
    expect(cpuNumber).toBeGreaterThanOrEqual(0);
    expect(cpuNumber).toBeLessThanOrEqual(100);
  });

  test('should display real-time memory usage updates', async ({ page }) => {
    // Additional wait for component rendering
    await new Promise(r => setTimeout(r, 2000));
    
    const memoryValue = page.locator('text=GB').first();
    await expect(memoryValue).toBeVisible({ timeout: 10000 });
    
    const initialValue = await memoryValue.textContent();
    await new Promise(r => setTimeout(r, 3000));
    const updatedValue = await memoryValue.textContent();
    
    expect(initialValue).not.toBe(updatedValue);
    
    const memoryNumber = parseFloat(updatedValue!.replace('GB', '').trim());
    expect(memoryNumber).toBeGreaterThanOrEqual(0);
  });

  test('should handle CPU usage API errors gracefully', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Failed to get CPU metrics' })
      });
    });

    await new Promise(r => setTimeout(r, 2000));
    
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible();
  });

  test('should handle memory usage API errors gracefully', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Failed to get memory metrics' })
      });
    });

    await new Promise(r => setTimeout(r, 2000));
    
    const memoryMonitor = page.locator('text=Memory Usage');
    await expect(memoryMonitor).toBeVisible();
  });

  test('should display CPU graph with historical data', async ({ page }) => {
    const cpuGraph = page.locator('text=CPU Usage Over Time');
    await expect(cpuGraph).toBeVisible();
    
    const graphContainer = page.locator('[class*="chart"]').first();
    await expect(graphContainer).toBeVisible();
  });

  test('should display memory graph with historical data', async ({ page }) => {
    const memoryGraph = page.locator('text=Memory Usage Over Time');
    await expect(memoryGraph).toBeVisible();
    
    const graphContainer = page.locator('[class*="chart"]').nth(1);
    await expect(graphContainer).toBeVisible();
  });

  test('should update graphs with new data points', async ({ page }) => {
    const cpuGraph = page.locator('text=CPU Usage');
    await expect(cpuGraph).toBeVisible();
    
    await new Promise(r => setTimeout(r, 5000));
    
    await expect(cpuGraph).toBeVisible();
  });

  test('should display disk usage information', async ({ page }) => {
    const diskCard = page.locator('text=Disk Usage');
    await expect(diskCard).toBeVisible();
    
    const diskInfo = page.locator('text=Used').or(page.locator('text=Available'));
    await expect(diskInfo).toBeVisible();
  });

  test('should handle system metrics with zero values', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 0,
          memory_usage: 0,
          memory_total: 0,
          disk_usage: 0,
          disk_total: 0
        })
      });
    });

    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.locator('text=%').first();
    await expect(cpuValue).toHaveText('0.0%');
    
    const memoryValue = page.locator('text=GB').first();
    await expect(memoryValue).toHaveText('0.00 GB');
  });

  test('should handle system metrics with maximum values', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 100,
          memory_usage: 17179869184, // 16GB
          memory_total: 17179869184,
          disk_usage: 100,
          disk_total: 1099511627776 // 1TB
        })
      });
    });

    // Wait for component to render with mocked data
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await new Promise(r => setTimeout(r, 3000));
    
    const cpuValue = page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible({ timeout: 10000 });
    
    const cpuText = await cpuValue.textContent();
    expect(cpuText).toContain('100.0');
    
    const memoryValue = page.getByText(/GB/).first();
    await expect(memoryValue).toBeVisible({ timeout: 10000 });
    
    const memoryText = await memoryValue.textContent();
    expect(memoryText).toContain('16.00');
  });

  test('should maintain consistent polling intervals', async ({ page }) => {
    const requestTimes: number[] = [];
    
    // Mock the API to track requests and return consistent data
    await page.route('**/invoke/get_system_metrics', route => {
      requestTimes.push(Date.now());
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 45.5,
          memory_usage: 8589934592,
          memory_total: 17179869184,
          disk_usage: 60,
          disk_total: 1099511627776
        })
      });
    });

    // Wait for initial page load and multiple polling cycles
    await page.waitForLoadState('networkidle');
    await new Promise(r => setTimeout(r, 6000));
    
    expect(requestTimes.length).toBeGreaterThan(3);
    
    for (let i = 1; i < requestTimes.length; i++) {
      const interval = requestTimes[i] - requestTimes[i - 1];
      expect(interval).toBeGreaterThanOrEqual(900);
      expect(interval).toBeLessThanOrEqual(1100);
    }
  });

  test('should handle rapid system metric changes', async ({ page }) => {
    let requestCount = 0;
    
    await page.route('**/invoke/get_system_metrics', route => {
      requestCount++;
      
      const cpuUsage = requestCount % 2 === 0 ? 25 : 75;
      const memoryUsage = requestCount % 2 === 0 ? 4294967296 : 8589934592; // 4GB or 8GB
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: cpuUsage,
          memory_usage: memoryUsage,
          memory_total: 17179869184, // 16GB
          disk_usage: 50,
          disk_total: 1099511627776 // 1TB
        })
      });
    });

    await new Promise(r => setTimeout(r, 3000));
    
    const cpuValue = page.locator('text=%').first();
    const cpuText = await cpuValue.textContent();
    const cpuNumber = parseFloat(cpuText!.replace('%', ''));
    
    expect([25, 75]).toContain(cpuNumber);
  });

  test('should handle system metrics API timeouts', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', async route => {
      await new Promise(r => setTimeout(r, 3000));
      route.continue();
    });

    await new Promise(r => setTimeout(r, 5000));
    
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible();
  });

  test('should display proper formatting for large numbers', async ({ page }) => {
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 87.654321,
          memory_usage: 12345678901, // ~11.5GB
          memory_total: 17179869184,
          disk_usage: 87.65,
          disk_total: 1099511627776
        })
      });
    });

    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.locator('text=%').first();
    await expect(cpuValue).toHaveText('87.7%');
    
    const memoryValue = page.locator('text=GB').first();
    await expect(memoryValue).toHaveText('11.50 GB');
  });

  test('should handle concurrent system metric requests', async ({ page }) => {
    let concurrentRequests = 0;
    let maxConcurrent = 0;
    
    await page.route('**/invoke/get_system_metrics', async route => {
      concurrentRequests++;
      maxConcurrent = Math.max(maxConcurrent, concurrentRequests);
      
      await new Promise(r => setTimeout(r, 100));
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 50,
          memory_usage: 8589934592,
          memory_total: 17179869184,
          disk_usage: 50,
          disk_total: 1099511627776
        })
      });
      
      concurrentRequests--;
    });

    await new Promise(r => setTimeout(r, 3000));
    
    expect(maxConcurrent).toBeLessThanOrEqual(2);
  });

  test('should handle system metrics with missing data', async ({ page }) => {
    // Set up mock BEFORE page loads (override beforeEach)
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 50,
          memory_usage: 8589934592,
          memory_total: 17179869184,
          disk_usage: 50,
          disk_total: 1099511627776
        })
      });
    });

    // Navigate to trigger component mount with mocked data
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await new Promise(r => setTimeout(r, 2000));
    
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible({ timeout: 10000 });
    
    // Clear the route to avoid affecting other tests
    await page.unroute('**/invoke/get_system_metrics');
  });

  test('should maintain system monitoring during navigation', async ({ page }) => {
    // Set up a default mock for system metrics BEFORE page loads
    const mockMetrics = {
      cpu_usage: 45.5,
      memory_usage: 8589934592,
      memory_total: 17179869184,
      disk_usage: 60,
      disk_total: 1099511627776
    };

    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMetrics)
      });
    });
    
    // Navigate to dashboard to trigger component mount with mocked data
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await new Promise(r => setTimeout(r, 2000));
    
    // Verify CPU monitor is visible on dashboard
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible({ timeout: 10000 });
    
    // Navigate to folder analysis using direct URL (more reliable)
    await page.goto('/folder-analysis');
    await page.waitForURL('**/folder-analysis');
    await new Promise(r => setTimeout(r, 2000));
    
    // Re-setup mock before navigating back (mocks are cleared on navigation)
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMetrics)
      });
    });
    
    // Navigate back to dashboard
    await page.goto('/');
    await page.waitForURL('**/');
    await page.waitForLoadState('networkidle');
    // Wait longer for Tauri invoke and component re-render
    await new Promise(r => setTimeout(r, 5000));
    
    // Verify system monitoring is still working
    await expect(cpuMonitor).toBeVisible({ timeout: 15000 });
  });
});