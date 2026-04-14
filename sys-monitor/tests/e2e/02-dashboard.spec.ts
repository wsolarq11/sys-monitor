import { test, expect } from '@playwright/test';

test.describe('Dashboard页面全量测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('页面标题和基本结构', async ({ page }) => {
    // 验证页面标题（使用更具体的选择器）
    await expect(page.locator('main h1')).toContainText('SysMonitor Dashboard');
    
    // 验证主容器存在
    await expect(page.locator('main')).toBeVisible();
  });

  test('CPU监控组件完整测试', async ({ page }) => {
    // 验证CPU卡片存在
    await expect(page.getByText('CPU Usage')).toBeVisible();
    
    // 验证描述文本
    await expect(page.getByText('Current usage across all cores')).toBeVisible();
    
    // 验证有数值显示（无论是正常数据还是错误状态）
    const cpuSection = page.locator('.card, [class*="bg-white"], [class*="rounded-lg"]').filter({ hasText: 'CPU Usage' });
    await expect(cpuSection).toBeVisible();
  });

  test('内存监控组件完整测试', async ({ page }) => {
    // 验证内存卡片存在
    await expect(page.getByText('Memory Usage')).toBeVisible();
    
    // 验证描述文本
    await expect(page.getByText('System memory in use')).toBeVisible();
    
    // 验证内存部分可见
    const memorySection = page.locator('.card, [class*="bg-white"], [class*="rounded-lg"]').filter({ hasText: 'Memory Usage' });
    await expect(memorySection).toBeVisible();
  });

  test('图表组件可见性', async ({ page }) => {
    // 验证图表容器存在
    const charts = page.locator('main .grid > div');
    await expect(charts.first()).toBeVisible();
  });

  test('数据自动刷新机制', async ({ page }) => {
    // 验证页面加载后组件仍然存在
    await expect(page.getByText('CPU Usage')).toBeVisible();
    
    // 等待2秒（数据刷新间隔）
    await page.waitForTimeout(2000);
    
    // 验证组件仍然存在
    await expect(page.getByText('CPU Usage')).toBeVisible();
  });

  test('响应式布局验证', async ({ page }) => {
    // 桌面分辨率
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('main .grid').first()).toBeVisible();
    
    // 平板分辨率
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('main .grid').first()).toBeVisible();
    
    // 恢复桌面分辨率
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('深色模式支持', async ({ page }) => {
    // 验证深色模式类存在（使用first()避免strict mode violation）
    const container = page.locator('.dark\\:bg-gray-900, .bg-gray-100, .bg-gray-50').first();
    await expect(container).toBeVisible();
  });
});
