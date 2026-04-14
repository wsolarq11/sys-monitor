import { test, expect } from '@playwright/test';

test.describe('Edge Cases and Performance Testing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
    await page.waitForLoadState('networkidle');
  });

  test('should handle empty folder scanning', async ({ page }) => {
    const emptyFolderPath = 'C:\\empty-folder';
    const mockScanResult = {
      total_size: 0,
      file_count: 0,
      folder_count: 1,
      scan_duration_ms: 100
    };

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(emptyFolderPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockScanResult)
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
    await expect(page.locator('text=总大小: 0 B')).toBeVisible();
    await expect(page.locator('text=文件数: 0')).toBeVisible();
  });

  test('should handle folders with special characters', async ({ page }) => {
    const specialPath = 'C:\\测试文件夹\\中文路径\\特殊字符!@#$%^&*()';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(specialPath);
    
    await expect(pathInput).toHaveValue(specialPath);
    
    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1024,
          file_count: 5,
          folder_count: 1,
          scan_duration_ms: 500
        })
      });
    });

    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle very long folder paths', async ({ page }) => {
    const longPath = 'C:\\' + 'a'.repeat(250) + '\\very-long-folder-name-that-exceeds-normal-limits';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(longPath);
    
    await expect(pathInput).toHaveValue(longPath);
    
    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1024,
          file_count: 3,
          folder_count: 1,
          scan_duration_ms: 300
        })
      });
    });

    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle folders with permission restrictions', async ({ page }) => {
    const restrictedPath = 'C:\\Windows\\System32\\config';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(restrictedPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Access denied: insufficient permissions' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle network drive paths', async ({ page }) => {
    const networkPath = '\\\\server\\share\\folder';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(networkPath);
    
    await expect(pathInput).toHaveValue(networkPath);
    
    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1048576,
          file_count: 50,
          folder_count: 5,
          scan_duration_ms: 2000
        })
      });
    });

    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle folders with symbolic links', async ({ page }) => {
    const symlinkPath = 'C:\\symlink-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(symlinkPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 5120,
          file_count: 8,
          folder_count: 2,
          scan_duration_ms: 800
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle folders with very large files', async ({ page }) => {
    const largeFilesPath = 'C:\\large-files-folder';
    const mockScanResult = {
      total_size: 10737418240, // 10GB
      file_count: 3,
      folder_count: 1,
      scan_duration_ms: 5000
    };

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(largeFilesPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockScanResult)
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
    await expect(page.locator('text=10.00 GB')).toBeVisible();
  });

  test('should handle folders with many small files', async ({ page }) => {
    const manyFilesPath = 'C:\\many-files-folder';
    const mockScanResult = {
      total_size: 1048576, // 1MB
      file_count: 10000,
      folder_count: 10,
      scan_duration_ms: 3000
    };

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(manyFilesPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockScanResult)
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
    await expect(page.locator('text=文件数: 10000')).toBeVisible();
  });

  test('should handle folders with deeply nested structure', async ({ page }) => {
    const deepPath = 'C:\\deeply\\nested\\folder\\structure\\with\\many\\levels';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(deepPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 2048,
          file_count: 15,
          folder_count: 20,
          scan_duration_ms: 1200
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
    await expect(page.locator('text=文件夹数: 20')).toBeVisible();
  });

  test('should handle folders with mixed file types', async ({ page }) => {
    const mixedPath = 'C:\\mixed-file-types';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mixedPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 5242880,
          file_count: 100,
          folder_count: 5,
          scan_duration_ms: 1500
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle folders with Unicode characters', async ({ page }) => {
    const unicodePath = 'C:\\文件夹\\测试目录\\🎉表情符号\\中文测试';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(unicodePath);
    
    await expect(pathInput).toHaveValue(unicodePath);
    
    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 3072,
          file_count: 8,
          folder_count: 4,
          scan_duration_ms: 600
        })
      });
    });

    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle folders with spaces in names', async ({ page }) => {
    const spacedPath = 'C:\\Folder With Spaces\\Another Folder\\File Name.txt';
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(spacedPath);
    
    await expect(pathInput).toHaveValue(spacedPath);
    
    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1024,
          file_count: 5,
          folder_count: 2,
          scan_duration_ms: 400
        })
      });
    });

    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle performance with large scan results', async ({ page }) => {
    const largeScanPath = 'C:\\large-scan-folder';
    const largeScanResult = {
      total_size: 53687091200, // 50GB
      file_count: 50000,
      folder_count: 1000,
      scan_duration_ms: 10000
    };

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(largeScanPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(largeScanResult)
      });
    });

    const startTime = Date.now();
    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible({ timeout: 30000 });
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(10000);
  });

  test('should handle memory usage during large operations', async ({ page }) => {
    const memoryIntensivePath = 'C:\\memory-test-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(memoryIntensivePath)
      });
    });

    await page.route('**/invoke/scan_folder', async route => {
      await page.waitForTimeout(2000);
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1073741824,
          file_count: 1000,
          folder_count: 100,
          scan_duration_ms: 2000
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle concurrent folder scans', async ({ page }) => {
    const testPaths = ['C:\\folder1', 'C:\\folder2', 'C:\\folder3'];
    let scanCount = 0;

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPaths[scanCount % testPaths.length])
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      scanCount++;
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 1024 * scanCount,
          file_count: 10 * scanCount,
          folder_count: 2 * scanCount,
          scan_duration_ms: 500
        })
      });
    });

    for (let i = 0; i < 3; i++) {
      await page.click('button:has-text("浏览...")');
      await page.click('button:has-text("扫描文件夹")');
      await page.waitForTimeout(1000);
    }
    
    await expect(page.locator('text=扫描历史')).toBeVisible();
  });

  test('should handle system resource constraints', async ({ page }) => {
    const resourceConstrainedPath = 'C:\\resource-test-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(resourceConstrainedPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'System resources exhausted' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle network latency during scans', async ({ page }) => {
    const highLatencyPath = 'C:\\latency-test-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(highLatencyPath)
      });
    });

    await page.route('**/invoke/scan_folder', async route => {
      await page.waitForTimeout(5000);
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_size: 2048,
          file_count: 12,
          folder_count: 3,
          scan_duration_ms: 5000
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible({ timeout: 10000 });
  });

  test('should handle file system errors gracefully', async ({ page }) => {
    const errorPath = 'C:\\error-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(errorPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'File system error: device not ready' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle invalid folder paths', async ({ page }) => {
    const invalidPaths = [
      '',
      'invalid-path',
      'C:\\nonexistent\\folder',
      'C:\\*\\invalid',
      'C:\\folder\\..\\..\\etc'
    ];

    for (const invalidPath of invalidPaths) {
      const pathInput = page.locator('input[placeholder*="文件夹路径"]');
      await pathInput.fill(invalidPath);
      
      await page.route('**/invoke/scan_folder', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Invalid folder path' })
        });
      });

      await page.click('button:has-text("扫描文件夹")');
      
      await expect(page.locator('text=扫描失败:')).toBeVisible();
      
      await pathInput.clear();
    }
  });
});