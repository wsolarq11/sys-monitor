import { test, expect } from '@playwright/test';
import { spawn, ChildProcess } from 'child_process';
import { join } from 'path';

// 应用程序路径
const APP_PATH = join(__dirname, '..', '..', '..', 'src-tauri', 'target', 'release', 'sys-monitor.exe');

// 测试配置
const TEST_TIMEOUT = 60000; // 60秒超时

test.describe('Tauri Application E2E Tests', () => {
  let appProcess: ChildProcess;

  test.beforeAll(async () => {
    console.log('启动 Tauri 应用程序...');
    
    // 启动应用程序
    appProcess = spawn(APP_PATH, [], {
      stdio: 'pipe',
      detached: false
    });

    // 等待应用程序启动
    await new Promise(resolve => setTimeout(resolve, 5000));
  });

  test.afterAll(async () => {
    console.log('关闭 Tauri 应用程序...');
    
    if (appProcess) {
      appProcess.kill();
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  });

  test('应用程序应成功启动', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 等待应用程序窗口出现
    await page.waitForTimeout(3000);
    
    // 检查应用程序标题
    const title = await page.title();
    expect(title).toContain('SysMonitor');
  });

  test('应显示仪表板页面', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 等待页面加载
    await page.waitForTimeout(2000);
    
    // 检查仪表板标题
    const dashboardTitle = page.locator('h1');
    await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
    
    // 检查导航菜单
    const navLinks = page.locator('nav a');
    await expect(navLinks).toHaveCount(2);
    
    // 检查系统监控组件
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible();
    
    const memoryMonitor = page.locator('text=Memory Usage');
    await expect(memoryMonitor).toBeVisible();
  });

  test('应能导航到文件夹分析页面', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 点击文件夹分析链接
    const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
    await folderAnalysisLink.click();
    
    // 等待页面切换
    await page.waitForTimeout(2000);
    
    // 检查文件夹分析页面元素
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await expect(pathInput).toBeVisible();
    
    const browseButton = page.locator('button:has-text("浏览...")');
    await expect(browseButton).toBeVisible();
    
    const scanButton = page.locator('button:has-text("扫描文件夹")');
    await expect(scanButton).toBeVisible();
  });

  test('应能返回仪表板页面', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 点击仪表板链接
    const dashboardLink = page.locator('a[href="/"]');
    await dashboardLink.click();
    
    // 等待页面切换
    await page.waitForTimeout(2000);
    
    // 检查仪表板页面
    const dashboardTitle = page.locator('h1');
    await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  });

  test('应显示实时系统监控数据', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 等待数据加载
    await page.waitForTimeout(3000);
    
    // 检查CPU使用率
    const cpuValue = page.locator('text=%').first();
    await expect(cpuValue).toBeVisible();
    
    const cpuText = await cpuValue.textContent();
    expect(cpuText).toMatch(/\d+\.\d+%/);
    
    // 检查内存使用率
    const memoryValue = page.locator('text=GB').first();
    await expect(memoryValue).toBeVisible();
    
    const memoryText = await memoryValue.textContent();
    expect(memoryText).toMatch(/\d+\.\d+\s*GB/);
  });

  test('应处理文件夹路径输入', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 导航到文件夹分析页面
    const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
    await folderAnalysisLink.click();
    await page.waitForTimeout(2000);
    
    // 测试路径输入
    const testPath = 'C:\\test-folder';
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    
    await pathInput.fill(testPath);
    await expect(pathInput).toHaveValue(testPath);
    
    // 清除输入
    await pathInput.clear();
    await expect(pathInput).toHaveValue('');
  });

  test('应显示错误消息', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 导航到文件夹分析页面
    const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
    await folderAnalysisLink.click();
    await page.waitForTimeout(2000);
    
    // 尝试扫描空路径
    const scanButton = page.locator('button:has-text("扫描文件夹")');
    await scanButton.click();
    
    // 检查错误消息
    const errorMessage = page.locator('[class*="bg-red-50"]');
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test('应用程序应响应窗口调整', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT);
    
    // 设置小窗口尺寸
    await page.setViewportSize({ width: 800, height: 600 });
    await page.waitForTimeout(1000);
    
    // 检查布局适应性
    const dashboardTitle = page.locator('h1');
    await expect(dashboardTitle).toBeVisible();
    
    // 恢复默认尺寸
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(1000);
    
    await expect(dashboardTitle).toBeVisible();
  });

  test('应保持应用程序稳定性', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT * 2);
    
    // 长时间运行测试
    for (let i = 0; i < 5; i++) {
      // 在页面间切换
      const dashboardLink = page.locator('a[href="/"]');
      const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
      
      await dashboardLink.click();
      await page.waitForTimeout(1000);
      
      await folderAnalysisLink.click();
      await page.waitForTimeout(1000);
    }
    
    // 最终检查应用程序状态
    const dashboardTitle = page.locator('h1');
    await expect(dashboardTitle).toBeVisible();
  });
});