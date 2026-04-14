# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: system-monitoring.spec.ts >> System Monitoring >> should handle system metrics with zero values
- Location: tests\system-monitoring.spec.ts:99:7

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
  3   | test.describe('System Monitoring', () => {
  4   |   test.beforeEach(async ({ page }) => {
> 5   |     await page.goto('/');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/
  6   |     await page.waitForLoadState('networkidle');
  7   |   });
  8   | 
  9   |   test('should display real-time CPU usage updates', async ({ page }) => {
  10  |     const cpuValue = page.locator('text=%').first();
  11  |     
  12  |     const initialValue = await cpuValue.textContent();
  13  |     await page.waitForTimeout(3000);
  14  |     const updatedValue = await cpuValue.textContent();
  15  |     
  16  |     expect(initialValue).not.toBe(updatedValue);
  17  |     
  18  |     const cpuNumber = parseFloat(updatedValue!.replace('%', ''));
  19  |     expect(cpuNumber).toBeGreaterThanOrEqual(0);
  20  |     expect(cpuNumber).toBeLessThanOrEqual(100);
  21  |   });
  22  | 
  23  |   test('should display real-time memory usage updates', async ({ page }) => {
  24  |     const memoryValue = page.locator('text=GB').first();
  25  |     
  26  |     const initialValue = await memoryValue.textContent();
  27  |     await page.waitForTimeout(3000);
  28  |     const updatedValue = await memoryValue.textContent();
  29  |     
  30  |     expect(initialValue).not.toBe(updatedValue);
  31  |     
  32  |     const memoryNumber = parseFloat(updatedValue!.replace('GB', '').trim());
  33  |     expect(memoryNumber).toBeGreaterThanOrEqual(0);
  34  |   });
  35  | 
  36  |   test('should handle CPU usage API errors gracefully', async ({ page }) => {
  37  |     await page.route('**/invoke/get_system_metrics', route => {
  38  |       route.fulfill({
  39  |         status: 500,
  40  |         contentType: 'application/json',
  41  |         body: JSON.stringify({ error: 'Failed to get CPU metrics' })
  42  |       });
  43  |     });
  44  | 
  45  |     await page.waitForTimeout(2000);
  46  |     
  47  |     const cpuMonitor = page.locator('text=CPU Usage');
  48  |     await expect(cpuMonitor).toBeVisible();
  49  |   });
  50  | 
  51  |   test('should handle memory usage API errors gracefully', async ({ page }) => {
  52  |     await page.route('**/invoke/get_system_metrics', route => {
  53  |       route.fulfill({
  54  |         status: 500,
  55  |         contentType: 'application/json',
  56  |         body: JSON.stringify({ error: 'Failed to get memory metrics' })
  57  |       });
  58  |     });
  59  | 
  60  |     await page.waitForTimeout(2000);
  61  |     
  62  |     const memoryMonitor = page.locator('text=Memory Usage');
  63  |     await expect(memoryMonitor).toBeVisible();
  64  |   });
  65  | 
  66  |   test('should display CPU graph with historical data', async ({ page }) => {
  67  |     const cpuGraph = page.locator('text=CPU Usage Over Time');
  68  |     await expect(cpuGraph).toBeVisible();
  69  |     
  70  |     const graphContainer = page.locator('[class*="chart"]').first();
  71  |     await expect(graphContainer).toBeVisible();
  72  |   });
  73  | 
  74  |   test('should display memory graph with historical data', async ({ page }) => {
  75  |     const memoryGraph = page.locator('text=Memory Usage Over Time');
  76  |     await expect(memoryGraph).toBeVisible();
  77  |     
  78  |     const graphContainer = page.locator('[class*="chart"]').nth(1);
  79  |     await expect(graphContainer).toBeVisible();
  80  |   });
  81  | 
  82  |   test('should update graphs with new data points', async ({ page }) => {
  83  |     const cpuGraph = page.locator('text=CPU Usage Over Time');
  84  |     await expect(cpuGraph).toBeVisible();
  85  |     
  86  |     await page.waitForTimeout(5000);
  87  |     
  88  |     await expect(cpuGraph).toBeVisible();
  89  |   });
  90  | 
  91  |   test('should display disk usage information', async ({ page }) => {
  92  |     const diskCard = page.locator('text=Disk Usage');
  93  |     await expect(diskCard).toBeVisible();
  94  |     
  95  |     const diskInfo = page.locator('text=Used').or(page.locator('text=Available'));
  96  |     await expect(diskInfo).toBeVisible();
  97  |   });
  98  | 
  99  |   test('should handle system metrics with zero values', async ({ page }) => {
  100 |     await page.route('**/invoke/get_system_metrics', route => {
  101 |       route.fulfill({
  102 |         status: 200,
  103 |         contentType: 'application/json',
  104 |         body: JSON.stringify({
  105 |           cpu_usage: 0,
```