import { test, expect } from '@playwright/test';

test.describe('Folder Analysis Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
    await page.waitForLoadState('networkidle');
  });

  test('should load folder analysis page successfully', async ({ page }) => {
    await expect(page.locator('input[placeholder*="文件夹路径"]')).toBeVisible();
    await expect(page.locator('button:has-text("浏览...")')).toBeVisible();
    await expect(page.locator('button:has-text("扫描文件夹")')).toBeVisible();
  });

  test('should allow manual path input', async ({ page }) => {
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    
    await pathInput.fill('C:\\test-folder');
    await expect(pathInput).toHaveValue('C:\\test-folder');
    
    await pathInput.clear();
    await expect(pathInput).toHaveValue('');
  });

  test('should handle folder selection dialog cancellation', async ({ page }) => {
    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'No folder selected' })
      });
    });

    await page.click('button:has-text("浏览...")');
    
    await page.waitForTimeout(1000);
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await expect(pathInput).toHaveValue('');
  });

  test('should handle successful folder selection', async ({ page }) => {
    const testPath = 'C:\\test-folder';
    
    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    await page.click('button:has-text("浏览...")');
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await expect(pathInput).toHaveValue(testPath);
  });

  test('should validate empty path before scanning', async ({ page }) => {
    await page.click('button:has-text("扫描文件夹")');
    
    const errorMessage = page.locator('text=请选择一个文件夹路径');
    await expect(errorMessage).toBeVisible();
  });

  test('should handle successful folder scan', async ({ page }) => {
    const testPath = 'C:\\test-folder';
    const mockScanResult = {
      total_size: 1024,
      file_count: 10,
      folder_count: 2,
      scan_duration_ms: 500
    };

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockScanResult)
      });
    });

    await page.route('**/invoke/get_folder_scans', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ scans: [] })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
    await expect(page.locator('text=总大小:')).toBeVisible();
    await expect(page.locator('text=文件数:')).toBeVisible();
    await expect(page.locator('text=文件夹数:')).toBeVisible();
    await expect(page.locator('text=扫描耗时:')).toBeVisible();
  });

  test('should handle folder scan errors', async ({ page }) => {
    const testPath = 'C:\\invalid-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Folder does not exist' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should display scan progress during scanning', async ({ page }) => {
    const testPath = 'C:\\test-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    let scanStarted = false;
    await page.route('**/invoke/scan_folder', async route => {
      if (!scanStarted) {
        scanStarted = true;
        await page.waitForTimeout(1000);
      }
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1024,
          file_count: 10,
          folder_count: 2,
          scan_duration_ms: 500
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=正在扫描文件夹...')).toBeVisible();
  });

  test('should display scan history', async ({ page }) => {
    const mockScans = [
      {
        id: 1,
        path: 'C:\\test-folder',
        scan_timestamp: Date.now() / 1000,
        total_size: 1024,
        file_count: 10,
        folder_count: 2
      }
    ];

    await page.route('**/invoke/get_folder_scans', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ scans: mockScans })
      });
    });

    await page.reload();
    
    await expect(page.locator('text=扫描历史')).toBeVisible();
    await expect(page.locator('text=C:\\test-folder')).toBeVisible();
  });

  test('should handle empty scan history', async ({ page }) => {
    await page.route('**/invoke/get_folder_scans', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ scans: [] })
      });
    });

    await page.reload();
    
    const scanHistory = page.locator('text=扫描历史');
    await expect(scanHistory).not.toBeVisible();
  });

  test('should handle special characters in folder paths', async ({ page }) => {
    const specialPath = 'C:\\测试文件夹\\中文路径\\特殊字符!@#$%';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(specialPath);
    await expect(pathInput).toHaveValue(specialPath);
  });

  test('should handle very long folder paths', async ({ page }) => {
    const longPath = 'C:\\' + 'a'.repeat(200) + '\\very-long-folder-name';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(longPath);
    await expect(pathInput).toHaveValue(longPath);
  });

  test('should clear error message when path is entered', async ({ page }) => {
    await page.click('button:has-text("扫描文件夹")');
    
    const errorMessage = page.locator('text=请选择一个文件夹路径');
    await expect(errorMessage).toBeVisible();
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill('C:\\test-folder');
    
    await expect(errorMessage).not.toBeVisible();
  });

  test('should disable scan button during scanning', async ({ page }) => {
    const testPath = 'C:\\test-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    let scanResolve: () => void;
    const scanPromise = new Promise<void>(resolve => {
      scanResolve = resolve;
    });

    await page.route('**/invoke/scan_folder', async route => {
      await scanPromise;
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1024,
          file_count: 10,
          folder_count: 2,
          scan_duration_ms: 500
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    const scanButton = page.locator('button:has-text("扫描中...")');
    await expect(scanButton).toBeDisabled();
    
    scanResolve();
  });

  test('should handle network connectivity issues', async ({ page }) => {
    await page.route('**/invoke/*', route => {
      route.abort('failed');
    });

    await page.click('button:has-text("浏览...")');
    
    await page.waitForTimeout(1000);
    
    const errorMessage = page.locator('[class*="bg-red-50"]');
    await expect(errorMessage).toBeVisible();
  });

  test('should maintain state after page refresh', async ({ page }) => {
    const testPath = 'C:\\test-folder';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(testPath);
    
    await page.reload();
    
    await expect(pathInput).toHaveValue('');
  });
});