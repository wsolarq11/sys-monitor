import { test, expect } from '@playwright/test';
import { setupCommonMocks, simulateErrorScenario } from '../utils/tauriMock';

test.describe('Folder Analysis Page - Fixed with Tauri Mock', () => {
  test.beforeEach(async ({ page }) => {
    // 注入Tauri API Mock
    await setupCommonMocks(page, 'folder-analysis');
    await page.goto('/folder-analysis');
    await page.waitForLoadState('networkidle');
  });

  test('should load folder analysis page successfully', async ({ page }) => {
    await expect(page.locator('input[placeholder*=\"文件夹路径\"]')).toBeVisible();
    await expect(page.locator('button:has-text(\"浏览...\")')).toBeVisible();
    await expect(page.locator('button:has-text(\"扫描文件夹\")')).toBeVisible();
  });

  test('should allow manual path input', async ({ page }) => {
    const pathInput = page.locator('input[placeholder*=\"文件夹路径\"]');
    
    await pathInput.fill('C:\\\\test-folder');
    await expect(pathInput).toHaveValue('C:\\\\test-folder');
    
    await pathInput.clear();
    await expect(pathInput).toHaveValue('');
  });

  test('should handle successful folder selection and scan', async ({ page }) => {
    const testPath = 'C:\\\\test-folder';
    
    // Mock select_folder返回
    await page.route('**/invoke/select_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testPath)
      });
    });

    await page.click('button:has-text(\"浏览...\")');
    
    const pathInput = page.locator('input[placeholder*=\"文件夹路径\"]');
    await expect(pathInput).toHaveValue(testPath);
  });

  test('should validate empty path before scanning', async ({ page }) => {
    await page.click('button:has-text(\"扫描文件夹\")');
    
    const errorMessage = page.locator('text=请选择一个文件夹路径');
    await expect(errorMessage).toBeVisible();
  });

  test('should handle successful folder scan', async ({ page }) => {
    const testPath = 'C:\\\\test-folder';

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
          total_size: 1048576,
          file_count: 100,
          folder_count: 10,
          scan_duration_ms: 1500
        })
      });
    });

    await page.click('button:has-text(\"浏览...\")');
    await page.click('button:has-text(\"扫描文件夹\")');
    
    await expect(page.locator('text=扫描完成')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=总大小:')).toBeVisible();
    await expect(page.locator('text=文件数:')).toBeVisible();
    await expect(page.locator('text=文件夹数:')).toBeVisible();
  });

  test('should handle folder scan errors', async ({ page }) => {
    const testPath = 'C:\\\\invalid-folder';

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

    await page.click('button:has-text(\"浏览...\")');
    await page.click('button:has-text(\"扫描文件夹\")');
    
    await expect(page.locator('text=扫描失败:')).toBeVisible({ timeout: 10000 });
  });

  test('should display scan history', async ({ page }) => {
    const mockScans = [
      {
        id: 1,
        path: 'C:\\\\test-folder',
        scan_timestamp: Math.floor(Date.now() / 1000),
        total_size: 1048576,
        file_count: 100,
        folder_count: 10
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
    await expect(page.locator('text=C:\\\\test-folder')).toBeVisible();
  });

  test('should handle special characters in folder paths', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  
    const specialPath = 'C:\\测试文件夹\\中文路径\\特殊字符!@#$%';
      
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill(specialPath);
    await expect(pathInput).toHaveValue(specialPath);
  });

  test('should clear error message when path is entered', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  
    await page.click('button:has-text("扫描文件夹")');
      
    const errorMessage = page.locator('text=请选择一个文件夹路径');
    await expect(errorMessage).toBeVisible();
      
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await pathInput.fill('C:\\test-folder');
      
    await expect(errorMessage).not.toBeVisible();
  });
});
