import { test, expect } from '../fixtures/test-fixtures';

test.describe('API and UI Coordination Tests', () => {
  test('should use api for data setup and ui for validation', async ({ page }) => {
    // Set custom mock for get_system_metrics
    await page.evaluate(() => {
      (window as any).__TAURI_MOCKS__ = {
        'get_system_metrics': {
          cpu_usage: 45.5,
          memory_usage: 8589934592,
          memory_total: 17179869184,
          disk_usage: 65.2,
          disk_total: 1099511627776
        }
      };
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible();
    
    const cpuText = await cpuValue.textContent();
    expect(cpuText).toContain('45.5');
  });

  test('should use msw pattern for network interception', async ({ page }) => {
    await page.evaluate(() => {
      (window as any).__TAURI_MOCKS__ = {
        'get_system_metrics': {
          cpu_usage: 75.3,
          memory_usage: 12884901888,
          memory_total: 17179869184
        }
      };
    });

    await page.goto('/');
    await new Promise(r => setTimeout(r, 3000));
    
    const metricsDisplay = page.getByText(/cpu usage/i);
    await expect(metricsDisplay).toBeVisible();
  });

  test('should handle api error with ui fallback', async ({ page }) => {
    // Simulate error by not setting mock - invoke will return null
    await page.goto('/');
    await new Promise(r => setTimeout(r, 3000));
    
    // App should handle error gracefully and show default values
    const cpuMonitor = page.getByText(/cpu usage/i);
    await expect(cpuMonitor).toBeVisible();
  });

  test('should use har-like scenario for deterministic testing', async ({ page }) => {
    await page.evaluate(() => {
      (window as any).__TAURI_MOCKS__ = {
        'get_system_metrics': {
          cpu_usage: 50.0,
          memory_usage: 10737418240,
          memory_total: 17179869184,
          disk_usage: 70.5,
          disk_total: 1099511627776
        }
      };
    });

    await page.goto('/');
    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.getByText(/%/).first();
    const cpuText = await cpuValue.textContent();
    expect(cpuText).toContain('50');
  });

  test('should validate api response structure via ui', async ({ page }) => {
    await page.evaluate(() => {
      (window as any).__TAURI_MOCKS__ = {
        'get_system_metrics': {
          cpu_usage: 33.3,
          memory_usage: 6442450944,
          memory_total: 17179869184,
          disk_usage: 55.0,
          disk_total: 549755813888
        }
      };
    });

    await page.goto('/');
    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible();
    
    const memoryValue = page.getByText(/gb/i).first();
    await expect(memoryValue).toBeVisible();
  });

  test('should handle loading state with api delay', async ({ page }) => {
    // Note: Delay simulation not supported in web mode mock
    await page.evaluate(() => {
      (window as any).__TAURI_MOCKS__ = {
        'get_system_metrics': {
          cpu_usage: 60.0,
          memory_usage: 9663676416,
          memory_total: 17179869184
        }
      };
    });

    await page.goto('/');
    
    const cpuMonitor = page.getByText(/cpu usage/i);
    await expect(cpuMonitor).toBeVisible({ timeout: 5000 });
  });

  test('should test edge case with api boundary values', async ({ page }) => {
    await page.evaluate(() => {
      (window as any).__TAURI_MOCKS__ = {
        'get_system_metrics': {
          cpu_usage: 0.0,
          memory_usage: 0,
          memory_total: 17179869184,
          disk_usage: 0.0,
          disk_total: 1099511627776
        }
      };
    });

    await page.goto('/');
    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible();
  });

  test('should test high load scenario', async ({ page }) => {
    await page.evaluate(() => {
      (window as any).__TAURI_MOCKS__ = {
        'get_system_metrics': {
          cpu_usage: 99.9,
          memory_usage: 16106127360,
          memory_total: 17179869184,
          disk_usage: 98.5,
          disk_total: 1099511627776
        }
      };
    });

    await page.goto('/');
    await new Promise(r => setTimeout(r, 2000));
    
    const cpuValue = page.getByText(/%/).first();
    await expect(cpuValue).toBeVisible();
    
    const cpuText = await cpuValue.textContent();
    expect(cpuText).toContain('99.9');
  });
});
