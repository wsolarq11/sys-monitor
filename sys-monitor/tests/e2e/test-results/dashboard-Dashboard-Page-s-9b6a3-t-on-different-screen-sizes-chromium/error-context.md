# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard.spec.ts >> Dashboard Page >> should maintain responsive layout on different screen sizes
- Location: tests\dashboard.spec.ts:91:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/
Call log:
  - navigating to "http://localhost:1420/", waiting until "load"

```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('Dashboard Page', () => {
  4   |   test.beforeEach(async ({ page }) => {
> 5   |     await page.goto('/');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/
  6   |     await page.waitForLoadState('networkidle');
  7   |   });
  8   | 
  9   |   test('should load dashboard page successfully', async ({ page }) => {
  10  |     await expect(page.locator('h1')).toContainText('SysMonitor Dashboard');
  11  |     await expect(page.locator('nav')).toBeVisible();
  12  |   });
  13  | 
  14  |   test('should display navigation links', async ({ page }) => {
  15  |     const dashboardLink = page.locator('a[href="/"]');
  16  |     const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  17  | 
  18  |     await expect(dashboardLink).toBeVisible();
  19  |     await expect(folderAnalysisLink).toBeVisible();
  20  |     await expect(dashboardLink).toHaveClass(/border-indigo-500/);
  21  |   });
  22  | 
  23  |   test('should navigate to folder analysis page', async ({ page }) => {
  24  |     await page.click('a[href="/folder-analysis"]');
  25  |     await page.waitForURL('**/folder-analysis');
  26  |     await expect(page.locator('input[placeholder*="文件夹路径"]')).toBeVisible();
  27  |   });
  28  | 
  29  |   test('should display CPU monitor component', async ({ page }) => {
  30  |     const cpuMonitor = page.locator('text=CPU Usage');
  31  |     await expect(cpuMonitor).toBeVisible();
  32  |     
  33  |     const cpuValue = page.locator('text=%').first();
  34  |     await expect(cpuValue).toBeVisible();
  35  |     
  36  |     const cpuText = await cpuValue.textContent();
  37  |     expect(cpuText).toMatch(/\d+\.\d+%/);
  38  |   });
  39  | 
  40  |   test('should display memory monitor component', async ({ page }) => {
  41  |     const memoryMonitor = page.locator('text=Memory Usage');
  42  |     await expect(memoryMonitor).toBeVisible();
  43  |     
  44  |     const memoryValue = page.locator('text=GB').first();
  45  |     await expect(memoryValue).toBeVisible();
  46  |     
  47  |     const memoryText = await memoryValue.textContent();
  48  |     expect(memoryText).toMatch(/\d+\.\d+\s*GB/);
  49  |   });
  50  | 
  51  |   test('should display CPU graph component', async ({ page }) => {
  52  |     const cpuGraph = page.locator('text=CPU Usage Over Time');
  53  |     await expect(cpuGraph).toBeVisible();
  54  |   });
  55  | 
  56  |   test('should display memory graph component', async ({ page }) => {
  57  |     const memoryGraph = page.locator('text=Memory Usage Over Time');
  58  |     await expect(memoryGraph).toBeVisible();
  59  |   });
  60  | 
  61  |   test('should display disk usage card', async ({ page }) => {
  62  |     const diskCard = page.locator('text=Disk Usage');
  63  |     await expect(diskCard).toBeVisible();
  64  |   });
  65  | 
  66  |   test('should update system metrics in real-time', async ({ page }) => {
  67  |     const initialCpuValue = await page.locator('text=%').first().textContent();
  68  |     
  69  |     await page.waitForTimeout(2000);
  70  |     
  71  |     const updatedCpuValue = await page.locator('text=%').first().textContent();
  72  |     
  73  |     expect(initialCpuValue).not.toBe(updatedCpuValue);
  74  |   });
  75  | 
  76  |   test('should handle system metrics API errors gracefully', async ({ page }) => {
  77  |     await page.route('**/invoke/get_system_metrics', route => {
  78  |       route.fulfill({
  79  |         status: 500,
  80  |         contentType: 'application/json',
  81  |         body: JSON.stringify({ error: 'Internal server error' })
  82  |       });
  83  |     });
  84  | 
  85  |     await page.waitForTimeout(3000);
  86  |     
  87  |     const cpuMonitor = page.locator('text=CPU Usage');
  88  |     await expect(cpuMonitor).toBeVisible();
  89  |   });
  90  | 
  91  |   test('should maintain responsive layout on different screen sizes', async ({ page }) => {
  92  |     await page.setViewportSize({ width: 375, height: 667 });
  93  |     
  94  |     await expect(page.locator('h1')).toBeVisible();
  95  |     await expect(page.locator('nav')).toBeVisible();
  96  |     
  97  |     await page.setViewportSize({ width: 1920, height: 1080 });
  98  |     
  99  |     await expect(page.locator('h1')).toBeVisible();
  100 |     await expect(page.locator('nav')).toBeVisible();
  101 |   });
  102 | 
  103 |   test('should support dark mode toggle', async ({ page }) => {
  104 |     const body = page.locator('body');
  105 |     
```