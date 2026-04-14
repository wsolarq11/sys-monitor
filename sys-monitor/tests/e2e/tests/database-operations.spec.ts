import { test, expect } from '@playwright/test';

test.describe('Database Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
    await page.waitForLoadState('networkidle');
  });

  test('should get database path successfully', async ({ page }) => {
    await page.route('**/invoke/get_db_path', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify('C:\\test\\sysmonitor.db')
      });
    });

    await page.reload();
    
    await page.waitForTimeout(1000);
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await expect(pathInput).toBeVisible();
  });

  test('should handle database path errors', async ({ page }) => {
    await page.route('**/invoke/get_db_path', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Failed to get database path' })
      });
    });

    await page.reload();
    
    await page.waitForTimeout(1000);
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await expect(pathInput).toBeVisible();
  });

  test('should create folder scan record', async ({ page }) => {
    const testPath = 'C:\\test-folder';
    const mockScanResult = {
      id: 123,
      path: testPath,
      scan_timestamp: Date.now() / 1000,
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
        body: JSON.stringify({ scans: [mockScanResult] })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
    await expect(page.locator('text=扫描历史')).toBeVisible();
    await expect(page.locator('text=C:\\test-folder')).toBeVisible();
  });

  test('should retrieve folder scan history', async ({ page }) => {
    const mockScans = [
      {
        id: 1,
        path: 'C:\\folder1',
        scan_timestamp: Date.now() / 1000,
        total_size: 1024,
        file_count: 5,
        folder_count: 1
      },
      {
        id: 2,
        path: 'C:\\folder2',
        scan_timestamp: (Date.now() / 1000) - 3600,
        total_size: 2048,
        file_count: 8,
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
    await expect(page.locator('text=C:\\folder1')).toBeVisible();
    await expect(page.locator('text=C:\\folder2')).toBeVisible();
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

  test('should handle database connection errors', async ({ page }) => {
    const testPath = 'C:\\test-folder';

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
        body: JSON.stringify({ error: 'Database connection failed' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle database timeout errors', async ({ page }) => {
    const testPath = 'C:\\test-folder';

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    await page.route('**/invoke/scan_folder', async route => {
      await page.waitForTimeout(10000);
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
    
    await expect(page.locator('text=扫描中...')).toBeVisible();
  });

  test('should handle concurrent database operations', async ({ page }) => {
    const testPath = 'C:\\test-folder';
    let operationCount = 0;

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    await page.route('**/invoke/scan_folder', async route => {
      operationCount++;
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: operationCount,
          path: testPath,
          scan_timestamp: Date.now() / 1000,
          total_size: 1024 * operationCount,
          file_count: 10 * operationCount,
          folder_count: 2 * operationCount,
          scan_duration_ms: 500
        })
      });
    });

    await page.route('**/invoke/get_folder_scans', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
          scans: Array.from({ length: operationCount }, (_, i) => ({
            id: i + 1,
            path: testPath,
            scan_timestamp: Date.now() / 1000,
            total_size: 1024 * (i + 1),
            file_count: 10 * (i + 1),
            folder_count: 2 * (i + 1)
          }))
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    
    for (let i = 0; i < 3; i++) {
      await page.click('button:has-text("扫描文件夹")');
      await page.waitForTimeout(1000);
    }
    
    await expect(page.locator('text=扫描历史')).toBeVisible();
  });

  test('should handle database file permission errors', async ({ page }) => {
    const testPath = 'C:\\test-folder';

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
        body: JSON.stringify({ error: 'Permission denied: cannot write to database file' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle database corruption errors', async ({ page }) => {
    await page.route('**/invoke/get_folder_scans', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Database file is corrupted' })
      });
    });

    await page.reload();
    
    await page.waitForTimeout(1000);
    
    const scanHistory = page.locator('text=扫描历史');
    await expect(scanHistory).not.toBeVisible();
  });

  test('should handle database schema version mismatches', async ({ page }) => {
    const testPath = 'C:\\test-folder';

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
        body: JSON.stringify({ error: 'Database schema version mismatch' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle database disk space errors', async ({ page }) => {
    const testPath = 'C:\\test-folder';

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
        body: JSON.stringify({ error: 'Disk full: cannot write to database' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle database transaction conflicts', async ({ page }) => {
    const testPath = 'C:\\test-folder';
    let attemptCount = 0;

    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    await page.route('**/invoke/scan_folder', route => {
      attemptCount++;
      
      if (attemptCount <= 2) {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Transaction conflict, please retry' })
        });
      } else {
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
      }
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
  });

  test('should handle database connection pool exhaustion', async ({ page }) => {
    const testPath = 'C:\\test-folder';

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
        body: JSON.stringify({ error: 'Database connection pool exhausted' })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible();
  });

  test('should handle database query optimization', async ({ page }) => {
    const mockScans = Array.from({ length: 100 }, (_, i) => ({
      id: i + 1,
      path: `C:\\folder${i + 1}`,
      scan_timestamp: (Date.now() / 1000) - (i * 3600),
      total_size: 1024 * (i + 1),
      file_count: 10 * (i + 1),
      folder_count: 2 * (i + 1)
    }));

    await page.route('**/invoke/get_folder_scans', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ scans: mockScans.slice(0, 10) })
      });
    });

    await page.reload();
    
    await expect(page.locator('text=扫描历史')).toBeVisible();
    
    const scanItems = page.locator('[class*="bg-gray-50"]');
    await expect(scanItems).toHaveCount(10);
  });

  test('should handle database index corruption', async ({ page }) => {
    await page.route('**/invoke/get_folder_scans', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Database index corrupted' })
      });
    });

    await page.reload();
    
    await page.waitForTimeout(1000);
    
    const scanHistory = page.locator('text=扫描历史');
    await expect(scanHistory).not.toBeVisible();
  });

  test('should handle database vacuum operations', async ({ page }) => {
    const testPath = 'C:\\test-folder';

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
        body: JSON.stringify({
          total_size: 1024,
          file_count: 10,
          folder_count: 2,
          scan_duration_ms: 1500
        })
      });
    });

    await page.click('button:has-text("浏览...")');
    await page.click('button:has-text("扫描文件夹")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible();
    await expect(page.locator('text=扫描耗时: 1500ms')).toBeVisible();
  });
});