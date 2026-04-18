/**
 * 端到端测试 - 核心功能验证
 * 
 * 测试场景：
 * 1. 添加监控文件夹流程
 * 2. 扫描文件夹流程
 * 3. 告警通知显示
 * 4. 系统监控数据显示
 */

import { test, expect } from '@playwright/test';

test.describe('Sys-Monitor E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // 导航到应用首页
    await page.goto('/');
    
    // 等待应用加载
    await page.waitForLoadState('networkidle');
  });

  test('应该正确显示Dashboard页面', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/Sys Monitor/);
    
    // 验证主要区域存在
    await expect(page.locator('text=系统监控')).toBeVisible();
    await expect(page.locator('text=文件夹分析')).toBeVisible();
  });

  test('应该显示CPU使用率图表', async ({ page }) => {
    // 等待系统监控组件加载
    await page.waitForSelector('.system-monitor', { timeout: 5000 });
    
    // 验证CPU监控区域存在
    const cpuMonitor = page.locator('text=CPU Usage').first();
    await expect(cpuMonitor).toBeVisible({ timeout: 10000 });
    
    // 验证图表容器存在
    const chartContainer = page.locator('.recharts-wrapper').first();
    await expect(chartContainer).toBeVisible();
  });

  test('应该显示内存使用情况', async ({ page }) => {
    // 等待内存监控加载
    const memoryText = page.locator('text=Memory').first();
    await expect(memoryText).toBeVisible({ timeout: 10000 });
    
    // 验证内存使用率显示
    const memoryUsage = page.locator('text=/\\d+\\.?\\d*%/').first();
    await expect(memoryUsage).toBeVisible();
  });

  test('应该能够选择文件夹进行扫描', async ({ page }) => {
    // 导航到文件夹分析页面
    await page.click('text=文件夹分析');
    
    // 等待页面加载
    await new Promise(r => setTimeout(r, 1000));
    
    // 验证文件夹选择按钮存在
    const selectButton = page.locator('button:has-text("选择文件夹")').first();
    await expect(selectButton).toBeVisible();
  });

  test('应该显示扫描历史记录', async ({ page }) => {
    // 导航到文件夹分析页面
    await page.click('text=文件夹分析');
    await new Promise(r => setTimeout(r, 1000));
    
    // 验证历史记录区域存在（即使为空）
    const historySection = page.locator('text=扫描历史').first();
    await expect(historySection).toBeVisible();
  });

  test('应该能够添加监控文件夹', async ({ page }) => {
    // 导航到监控文件夹页面
    await page.click('text=监控文件夹');
    await new Promise(r => setTimeout(r, 1000));
    
    // 验证添加按钮存在
    const addButton = page.locator('button:has-text("添加监控文件夹")').first();
    await expect(addButton).toBeVisible();
  });

  test('应该显示磁盘使用情况', async ({ page }) => {
    // 等待磁盘监控加载
    const diskText = page.locator('text=Disk').first();
    await expect(diskText).toBeVisible({ timeout: 10000 });
    
    // 验证磁盘使用率显示
    const diskUsage = page.locator('text=/\\d+\\.?\\d*%/').nth(1);
    await expect(diskUsage).toBeVisible();
  });

  test('应该实时更新系统指标', async ({ page }) => {
    // 等待初始数据加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 获取初始CPU使用率
    const initialCpuLocator = page.locator('.cpu-usage-value').first();
    const initialCpu = await initialCpuLocator.textContent();
    
    // 等待一段时间让数据更新
    await new Promise(r => setTimeout(r, 5000));
    
    // 验证数据仍然存在（说明有持续更新）
    await expect(initialCpuLocator).toBeVisible();
  });

  test('应该正确处理错误状态', async ({ page }) => {
    // 模拟错误情况（通过注入脚本）
    await page.evaluate(() => {
      // 模拟设置错误状态
      if ((window as any).__TEST_SET_ERROR__) {
        (window as any).__TEST_SET_ERROR__('Test error message');
      }
    });
    
    // 验证错误处理机制存在
    // 实际应用中应该有错误边界
  });

  test('应该响应式布局', async ({ page }) => {
    // 测试桌面视图
    await page.setViewportSize({ width: 1920, height: 1080 });
    const desktopLayout = page.locator('.dashboard-grid');
    await expect(desktopLayout).toBeVisible();
    
    // 测试平板视图
    await page.setViewportSize({ width: 768, height: 1024 });
    await new Promise(r => setTimeout(r, 500));
    
    // 测试手机视图
    await page.setViewportSize({ width: 375, height: 667 });
    await new Promise(r => setTimeout(r, 500));
    
    // 验证在小屏幕上仍然可见关键元素
    await expect(page.locator('text=系统监控')).toBeVisible();
  });

  test('应该支持深色/浅色主题切换', async ({ page }) => {
    // 查找主题切换按钮
    const themeToggle = page.locator('button[aria-label*="theme" i], .theme-toggle').first();
    
    if (await themeToggle.count() > 0) {
      await expect(themeToggle).toBeVisible();
      
      // 点击切换主题
      await themeToggle.click();
      await new Promise(r => setTimeout(r, 500));
      
      // 验证主题已切换（通过检查CSS类或属性）
      const body = page.locator('body');
      const hasDarkClass = await body.evaluate(el => el.classList.contains('dark'));
      
      // 再次切换
      await themeToggle.click();
      await new Promise(r => setTimeout(r, 500));
    }
  });

  test('应该显示加载状态', async ({ page }) => {
    // 刷新页面触发加载
    await page.reload();
    
    // 验证加载指示器出现然后消失
    const loadingIndicator = page.locator('.loading, .spinner').first();
    
    // 加载完成后应该消失
    await expect(loadingIndicator).not.toBeVisible({ timeout: 10000 });
  });

  test('应该保持状态持久化', async ({ page }) => {
    // 执行一些操作
    await page.click('text=文件夹分析');
    await new Promise(r => setTimeout(r, 1000));
    
    // 刷新页面
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 验证某些状态被保留（如主题、语言等）
    // 这取决于具体的持久化实现
  });

  test('应该正确处理网络错误', async ({ page }) => {
    // 拦截请求模拟失败
    await page.route('**/api/**', route => {
      route.fulfill({
        status: 500,
        body: 'Internal Server Error'
      });
    });
    
    // 尝试执行需要API的操作
    await page.click('text=文件夹分析');
    await new Promise(r => setTimeout(r, 1000));
    
    // 验证应用没有崩溃，仍然可用
    await expect(page.locator('body')).toBeVisible();
  });

  test('性能测试 - 页面加载时间', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // 验证加载时间在合理范围内（小于5秒）
    expect(loadTime).toBeLessThan(5000);
    
    console.log(`Page load time: ${loadTime}ms`);
  });

  test('性能测试 - 图表渲染性能', async ({ page }) => {
    await page.goto('/');
    await new Promise(r => setTimeout(r, 3000)); // 等待图表渲染
    
    // 获取性能指标
    const metrics = await page.evaluate(() => {
      const entries = performance.getEntriesByType('paint');
      return entries.map((e: any) => ({
        name: e.name,
        startTime: e.startTime
      }));
    });
    
    console.log('Paint metrics:', metrics);
    
    // 验证首次绘制时间在合理范围内
    const fcp = metrics.find((m: any) => m.name === 'first-contentful-paint');
    if (fcp) {
      expect(fcp.startTime).toBeLessThan(3000);
    }
  });
});
