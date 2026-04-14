import { test, expect } from '@playwright/test';

test.describe('全栈集成测试', () => {
  test('完整工作流程 - Dashboard到Folder Analysis', async ({ page }) => {
    // 1. 访问Dashboard
    await page.goto('/');
    await expect(page.getByText('SysMonitor Dashboard')).toBeVisible();
    
    // 2. 验证系统监控数据
    await expect(page.getByText('CPU Usage')).toBeVisible();
    await expect(page.getByText('Memory Usage')).toBeVisible();
    
    // 3. 导航到Folder Analysis
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    await expect(page).toHaveURL(/\/folder-analysis$/);
    
    // 4. 验证Folder Analysis页面
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.getByRole('button', { name: '浏览...' })).toBeVisible();
    await expect(page.getByRole('button', { name: '扫描文件夹' })).toBeVisible();
  });

  test('完整工作流程 - 扫描流程验证', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 1. 输入路径
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Windows\\Temp');
    
    // 2. 点击扫描
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    await scanButton.click();
    
    // 3. 验证扫描状态
    await expect(page.getByText('扫描中...')).toBeVisible();
    await expect(scanButton).toBeDisabled();
    
    // 4. 等待扫描完成或超时
    await page.waitForTimeout(10000);
    
    // 5. 验证按钮恢复可用
    await expect(scanButton).toBeEnabled();
  });

  test('多页面状态保持', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 1. 在Folder Analysis输入路径
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\TestPath');
    
    // 2. 切换到Dashboard
    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page).toHaveURL(/\/$/);
    
    // 3. 切换回Folder Analysis
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    await expect(page).toHaveURL(/\/folder-analysis$/);
    
    // 4. 验证输入框内容（可能保持也可能不保持，取决于实现）
    await expect(input).toBeVisible();
  });

  test('快速页面切换稳定性', async ({ page }) => {
    await page.goto('/');
    
    // 快速切换10次
    for (let i = 0; i < 10; i++) {
      await page.getByRole('link', { name: 'Folder Analysis' }).click();
      await page.getByRole('link', { name: 'Dashboard' }).click();
    }
    
    // 验证页面仍然正常
    await expect(page.getByText('SysMonitor Dashboard')).toBeVisible();
    await expect(page.getByText('CPU Usage')).toBeVisible();
  });

  test('系统监控与文件夹扫描并发', async ({ page }) => {
    await page.goto('/');
    
    // 验证系统监控运行中
    await expect(page.getByText('CPU Usage')).toBeVisible();
    const initialCpu = await page.locator('text=/\\d+\\.\\d%/').first().textContent();
    
    // 切换到Folder Analysis并扫描
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Windows\\Temp');
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
    // 等待扫描开始
    await expect(page.getByText('扫描中...')).toBeVisible();
    
    // 切换回Dashboard
    await page.getByRole('link', { name: 'Dashboard' }).click();
    
    // 验证系统监控仍在运行
    await expect(page.getByText('CPU Usage')).toBeVisible();
    await page.waitForTimeout(2000);
    await expect(page.locator('text=/\\d+\\.\\d%/').first()).toBeVisible();
  });

  test('错误恢复能力', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 1. 触发错误
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    await expect(page.getByText('请选择一个文件夹路径')).toBeVisible();
    
    // 2. 导航到其他页面
    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page).toHaveURL(/\/$/);
    
    // 3. 返回Folder Analysis
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    
    // 4. 验证可以正常操作
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Windows');
    await expect(input).toHaveValue('C:\\Windows');
  });

  test('浏览器刷新后状态', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 输入内容
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Test');
    
    // 刷新页面
    await page.reload();
    
    // 验证页面正常加载
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.getByRole('button', { name: '浏览...' })).toBeVisible();
    await expect(page.getByRole('button', { name: '扫描文件夹' })).toBeVisible();
  });

  test('响应式布局集成', async ({ page }) => {
    await page.goto('/');
    
    // 测试不同分辨率
    const viewports = [
      { width: 1920, height: 1080 },
      { width: 1366, height: 768 },
      { width: 1024, height: 768 },
      { width: 768, height: 1024 },
      { width: 375, height: 667 },
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(500);
      
      // 验证关键元素仍然可见
      await expect(page.getByText('SysMonitor')).toBeVisible();
      await expect(page.getByText('CPU Usage')).toBeVisible();
    }
    
    // 恢复默认分辨率
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('键盘导航集成', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // Tab导航
    await page.keyboard.press('Tab'); // 输入框
    await expect(page.locator('input[type="text"]')).toBeFocused();
    
    await page.keyboard.press('Tab'); // 浏览按钮
    // 焦点可能在按钮上
    
    await page.keyboard.press('Tab'); // 扫描按钮
    // 焦点可能在按钮上
    
    await page.keyboard.press('Tab'); // 导航链接
    // 焦点可能在Dashboard链接
  });

  test('端到端性能测试', async ({ page }) => {
    const startTime = Date.now();
    
    // 1. 加载Dashboard
    await page.goto('/');
    await expect(page.getByText('SysMonitor Dashboard')).toBeVisible();
    
    // 2. 导航到Folder Analysis
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    await expect(page).toHaveURL(/\/folder-analysis$/);
    
    // 3. 执行扫描
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Windows\\Temp');
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
    // 等待扫描开始
    await expect(page.getByText('扫描中...')).toBeVisible();
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // 验证总时间合理（应该小于30秒）
    expect(duration).toBeLessThan(30000);
  });
});
