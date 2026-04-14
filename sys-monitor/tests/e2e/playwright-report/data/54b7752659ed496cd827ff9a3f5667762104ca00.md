# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: edge-cases.spec.ts >> Edge Cases and Performance Testing >> should handle folders with permission restrictions
- Location: tests\edge-cases.spec.ts:94:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/folder-analysis
Call log:
  - navigating to "http://localhost:1420/folder-analysis", waiting until "load"

```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('Edge Cases and Performance Testing', () => {
  4   |   test.beforeEach(async ({ page }) => {
> 5   |     await page.goto('/folder-analysis');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/folder-analysis
  6   |     await page.waitForLoadState('networkidle');
  7   |   });
  8   | 
  9   |   test('should handle empty folder scanning', async ({ page }) => {
  10  |     const emptyFolderPath = 'C:\\empty-folder';
  11  |     const mockScanResult = {
  12  |       total_size: 0,
  13  |       file_count: 0,
  14  |       folder_count: 1,
  15  |       scan_duration_ms: 100
  16  |     };
  17  | 
  18  |     await page.route('**/invoke/select_folder', route => {
  19  |       route.fulfill({
  20  |         status: 200,
  21  |         contentType: 'application/json',
  22  |         body: JSON.stringify(emptyFolderPath)
  23  |       });
  24  |     });
  25  | 
  26  |     await page.route('**/invoke/scan_folder', route => {
  27  |       route.fulfill({
  28  |         status: 200,
  29  |         contentType: 'application/json',
  30  |         body: JSON.stringify(mockScanResult)
  31  |       });
  32  |     });
  33  | 
  34  |     await page.click('button:has-text("浏览...")');
  35  |     await page.click('button:has-text("扫描文件夹")');
  36  |     
  37  |     await expect(page.locator('text=扫描完成')).toBeVisible();
  38  |     await expect(page.locator('text=总大小: 0 B')).toBeVisible();
  39  |     await expect(page.locator('text=文件数: 0')).toBeVisible();
  40  |   });
  41  | 
  42  |   test('should handle folders with special characters', async ({ page }) => {
  43  |     const specialPath = 'C:\\测试文件夹\\中文路径\\特殊字符!@#$%^&*()';
  44  |     
  45  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  46  |     await pathInput.fill(specialPath);
  47  |     
  48  |     await expect(pathInput).toHaveValue(specialPath);
  49  |     
  50  |     await page.route('**/invoke/scan_folder', route => {
  51  |       route.fulfill({
  52  |         status: 200,
  53  |         contentType: 'application/json',
  54  |         body: JSON.stringify({
  55  |           total_size: 1024,
  56  |           file_count: 5,
  57  |           folder_count: 1,
  58  |           scan_duration_ms: 500
  59  |         })
  60  |       });
  61  |     });
  62  | 
  63  |     await page.click('button:has-text("扫描文件夹")');
  64  |     
  65  |     await expect(page.locator('text=扫描完成')).toBeVisible();
  66  |   });
  67  | 
  68  |   test('should handle very long folder paths', async ({ page }) => {
  69  |     const longPath = 'C:\\' + 'a'.repeat(250) + '\\very-long-folder-name-that-exceeds-normal-limits';
  70  |     
  71  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  72  |     await pathInput.fill(longPath);
  73  |     
  74  |     await expect(pathInput).toHaveValue(longPath);
  75  |     
  76  |     await page.route('**/invoke/scan_folder', route => {
  77  |       route.fulfill({
  78  |         status: 200,
  79  |         contentType: 'application/json',
  80  |         body: JSON.stringify({
  81  |           total_size: 1024,
  82  |           file_count: 3,
  83  |           folder_count: 1,
  84  |           scan_duration_ms: 300
  85  |         })
  86  |       });
  87  |     });
  88  | 
  89  |     await page.click('button:has-text("扫描文件夹")');
  90  |     
  91  |     await expect(page.locator('text=扫描完成')).toBeVisible();
  92  |   });
  93  | 
  94  |   test('should handle folders with permission restrictions', async ({ page }) => {
  95  |     const restrictedPath = 'C:\\Windows\\System32\\config';
  96  | 
  97  |     await page.route('**/invoke/select_folder', route => {
  98  |       route.fulfill({
  99  |         status: 200,
  100 |         contentType: 'application/json',
  101 |         body: JSON.stringify(restrictedPath)
  102 |       });
  103 |     });
  104 | 
  105 |     await page.route('**/invoke/scan_folder', route => {
```