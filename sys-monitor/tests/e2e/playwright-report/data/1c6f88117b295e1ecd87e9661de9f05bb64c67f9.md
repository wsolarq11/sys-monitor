# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: folder-analysis.spec.ts >> Folder Analysis Page >> should handle very long folder paths
- Location: tests\folder-analysis.spec.ts:219:7

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
  3   | test.describe('Folder Analysis Page', () => {
  4   |   test.beforeEach(async ({ page }) => {
> 5   |     await page.goto('/folder-analysis');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/folder-analysis
  6   |     await page.waitForLoadState('networkidle');
  7   |   });
  8   | 
  9   |   test('should load folder analysis page successfully', async ({ page }) => {
  10  |     await expect(page.locator('input[placeholder*="文件夹路径"]')).toBeVisible();
  11  |     await expect(page.locator('button:has-text("浏览...")')).toBeVisible();
  12  |     await expect(page.locator('button:has-text("扫描文件夹")')).toBeVisible();
  13  |   });
  14  | 
  15  |   test('should allow manual path input', async ({ page }) => {
  16  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  17  |     
  18  |     await pathInput.fill('C:\\test-folder');
  19  |     await expect(pathInput).toHaveValue('C:\\test-folder');
  20  |     
  21  |     await pathInput.clear();
  22  |     await expect(pathInput).toHaveValue('');
  23  |   });
  24  | 
  25  |   test('should handle folder selection dialog cancellation', async ({ page }) => {
  26  |     await page.route('**/invoke/select_folder', route => {
  27  |       route.fulfill({
  28  |         status: 200,
  29  |         contentType: 'application/json',
  30  |         body: JSON.stringify({ error: 'No folder selected' })
  31  |       });
  32  |     });
  33  | 
  34  |     await page.click('button:has-text("浏览...")');
  35  |     
  36  |     await page.waitForTimeout(1000);
  37  |     
  38  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  39  |     await expect(pathInput).toHaveValue('');
  40  |   });
  41  | 
  42  |   test('should handle successful folder selection', async ({ page }) => {
  43  |     const testPath = 'C:\\test-folder';
  44  |     
  45  |     await page.route('**/invoke/select_folder', route => {
  46  |       route.fulfill({
  47  |         status: 200,
  48  |         contentType: 'application/json',
  49  |         body: JSON.stringify(testPath)
  50  |       });
  51  |     });
  52  | 
  53  |     await page.click('button:has-text("浏览...")');
  54  |     
  55  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  56  |     await expect(pathInput).toHaveValue(testPath);
  57  |   });
  58  | 
  59  |   test('should validate empty path before scanning', async ({ page }) => {
  60  |     await page.click('button:has-text("扫描文件夹")');
  61  |     
  62  |     const errorMessage = page.locator('text=请选择一个文件夹路径');
  63  |     await expect(errorMessage).toBeVisible();
  64  |   });
  65  | 
  66  |   test('should handle successful folder scan', async ({ page }) => {
  67  |     const testPath = 'C:\\test-folder';
  68  |     const mockScanResult = {
  69  |       total_size: 1024,
  70  |       file_count: 10,
  71  |       folder_count: 2,
  72  |       scan_duration_ms: 500
  73  |     };
  74  | 
  75  |     await page.route('**/invoke/select_folder', route => {
  76  |       route.fulfill({
  77  |         status: 200,
  78  |         contentType: 'application/json',
  79  |         body: JSON.stringify(testPath)
  80  |       });
  81  |     });
  82  | 
  83  |     await page.route('**/invoke/scan_folder', route => {
  84  |       route.fulfill({
  85  |         status: 200,
  86  |         contentType: 'application/json',
  87  |         body: JSON.stringify(mockScanResult)
  88  |       });
  89  |     });
  90  | 
  91  |     await page.route('**/invoke/get_folder_scans', route => {
  92  |       route.fulfill({
  93  |         status: 200,
  94  |         contentType: 'application/json',
  95  |         body: JSON.stringify({ scans: [] })
  96  |       });
  97  |     });
  98  | 
  99  |     await page.click('button:has-text("浏览...")');
  100 |     await page.click('button:has-text("扫描文件夹")');
  101 |     
  102 |     await expect(page.locator('text=扫描完成')).toBeVisible();
  103 |     await expect(page.locator('text=总大小:')).toBeVisible();
  104 |     await expect(page.locator('text=文件数:')).toBeVisible();
  105 |     await expect(page.locator('text=文件夹数:')).toBeVisible();
```