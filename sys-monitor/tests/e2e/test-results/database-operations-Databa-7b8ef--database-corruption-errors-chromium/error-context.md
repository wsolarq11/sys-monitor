# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: database-operations.spec.ts >> Database Operations >> should handle database corruption errors
- Location: tests\database-operations.spec.ts:275:7

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
  3   | test.describe('Database Operations', () => {
  4   |   test.beforeEach(async ({ page }) => {
> 5   |     await page.goto('/folder-analysis');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/folder-analysis
  6   |     await page.waitForLoadState('networkidle');
  7   |   });
  8   | 
  9   |   test('should get database path successfully', async ({ page }) => {
  10  |     await page.route('**/invoke/get_db_path', route => {
  11  |       route.fulfill({
  12  |         status: 200,
  13  |         contentType: 'application/json',
  14  |         body: JSON.stringify('C:\\test\\sysmonitor.db')
  15  |       });
  16  |     });
  17  | 
  18  |     await page.reload();
  19  |     
  20  |     await page.waitForTimeout(1000);
  21  |     
  22  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  23  |     await expect(pathInput).toBeVisible();
  24  |   });
  25  | 
  26  |   test('should handle database path errors', async ({ page }) => {
  27  |     await page.route('**/invoke/get_db_path', route => {
  28  |       route.fulfill({
  29  |         status: 500,
  30  |         contentType: 'application/json',
  31  |         body: JSON.stringify({ error: 'Failed to get database path' })
  32  |       });
  33  |     });
  34  | 
  35  |     await page.reload();
  36  |     
  37  |     await page.waitForTimeout(1000);
  38  |     
  39  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  40  |     await expect(pathInput).toBeVisible();
  41  |   });
  42  | 
  43  |   test('should create folder scan record', async ({ page }) => {
  44  |     const testPath = 'C:\\test-folder';
  45  |     const mockScanResult = {
  46  |       id: 123,
  47  |       path: testPath,
  48  |       scan_timestamp: Date.now() / 1000,
  49  |       total_size: 1024,
  50  |       file_count: 10,
  51  |       folder_count: 2,
  52  |       scan_duration_ms: 500
  53  |     };
  54  | 
  55  |     await page.route('**/invoke/select_folder', route => {
  56  |       route.fulfill({
  57  |         status: 200,
  58  |         contentType: 'application/json',
  59  |         body: JSON.stringify(testPath)
  60  |       });
  61  |     });
  62  | 
  63  |     await page.route('**/invoke/scan_folder', route => {
  64  |       route.fulfill({
  65  |         status: 200,
  66  |         contentType: 'application/json',
  67  |         body: JSON.stringify(mockScanResult)
  68  |       });
  69  |     });
  70  | 
  71  |     await page.route('**/invoke/get_folder_scans', route => {
  72  |       route.fulfill({
  73  |         status: 200,
  74  |         contentType: 'application/json',
  75  |         body: JSON.stringify({ scans: [mockScanResult] })
  76  |       });
  77  |     });
  78  | 
  79  |     await page.click('button:has-text("浏览...")');
  80  |     await page.click('button:has-text("扫描文件夹")');
  81  |     
  82  |     await expect(page.locator('text=扫描完成')).toBeVisible();
  83  |     await expect(page.locator('text=扫描历史')).toBeVisible();
  84  |     await expect(page.locator('text=C:\\test-folder')).toBeVisible();
  85  |   });
  86  | 
  87  |   test('should retrieve folder scan history', async ({ page }) => {
  88  |     const mockScans = [
  89  |       {
  90  |         id: 1,
  91  |         path: 'C:\\folder1',
  92  |         scan_timestamp: Date.now() / 1000,
  93  |         total_size: 1024,
  94  |         file_count: 5,
  95  |         folder_count: 1
  96  |       },
  97  |       {
  98  |         id: 2,
  99  |         path: 'C:\\folder2',
  100 |         scan_timestamp: (Date.now() / 1000) - 3600,
  101 |         total_size: 2048,
  102 |         file_count: 8,
  103 |         folder_count: 2
  104 |       }
  105 |     ];
```