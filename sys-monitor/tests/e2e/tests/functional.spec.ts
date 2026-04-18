import { test, expect } from '@playwright/test';

// 功能测试 - 模拟实际用户操作
test.describe('SysMonitor Functional Tests', () => {
  
  // 模拟应用程序启动和基本功能
  test('应用程序基本功能测试', async ({ page }) => {
    // 模拟访问应用程序
    await page.goto('http://localhost:1420');
    
    // 检查应用程序标题
    const title = await page.title();
    expect(title).toContain('SysMonitor');
    
    // 等待React应用加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 检查导航菜单
    const navLinks = page.locator('nav a');
    await expect(navLinks).toHaveCount(2);
    
    // 检查仪表板组件
    const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
    await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
    
    // 检查系统监控组件
    const cpuMonitor = page.locator('text=CPU Usage');
    await expect(cpuMonitor).toBeVisible();
    
    const memoryMonitor = page.locator('text=Memory Usage');
    await expect(memoryMonitor).toBeVisible();
  });

  test('导航功能测试', async ({ page }) => {
    await page.goto('http://localhost:1420');
    
    // 等待React应用加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 测试导航到文件夹分析页面
    const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
    await folderAnalysisLink.click();
    
    // 等待页面切换
    await new Promise(r => setTimeout(r, 2000));
    
    // 检查文件夹分析页面
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await expect(pathInput).toBeVisible();
    
    // 测试返回仪表板
    const dashboardLink = page.locator('a[href="/"]');
    await dashboardLink.click();
    
    // 等待页面切换
    await new Promise(r => setTimeout(r, 2000));
    
    const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
    await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  });

  test('文件夹分析功能测试', async ({ page }) => {
    await page.goto('http://localhost:1420/folder-analysis');
    
    // 测试路径输入
    const testPath = 'C:\\test-folder';
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    
    await pathInput.fill(testPath);
    await expect(pathInput).toHaveValue(testPath);
    
    // 测试清除输入
    await pathInput.clear();
    await expect(pathInput).toHaveValue('');
    
    // 测试错误处理
    const scanButton = page.locator('button:has-text("扫描文件夹")');
    await scanButton.click();
    
    // 检查错误消息
    const errorMessage = page.locator('[class*="bg-red-50"]');
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test('系统监控数据测试', async ({ page }) => {
    await page.goto('http://localhost:1420');
    
    // 等待React应用加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 模拟系统监控数据
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cpu_usage: 45.5,
          memory_usage: 8589934592, // 8GB
          memory_total: 17179869184, // 16GB
          disk_usage: 65.2,
          disk_total: 1099511627776 // 1TB
        })
      });
    });
    
    // 等待数据加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 检查CPU使用率显示
    const cpuValue = page.locator('text=%').first();
    await expect(cpuValue).toBeVisible();
    
    // 检查内存使用率显示
    const memoryValue = page.locator('text=GB').first();
    await expect(memoryValue).toBeVisible();
  });

  test('响应式设计测试', async ({ page }) => {
    await page.goto('http://localhost:1420');
    
    // 等待React应用加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 测试不同屏幕尺寸
    await page.setViewportSize({ width: 375, height: 667 }); // 移动端
    await new Promise(r => setTimeout(r, 1000));
    
    const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
    await expect(dashboardTitle).toBeVisible();
    
    await page.setViewportSize({ width: 1920, height: 1080 }); // 桌面端
    await new Promise(r => setTimeout(r, 1000));
    
    await expect(dashboardTitle).toBeVisible();
  });

  test('API错误处理测试', async ({ page }) => {
    await page.goto('http://localhost:1420');
    
    // 等待React应用加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 模拟API错误
    await page.route('**/invoke/get_system_metrics', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    // 等待错误处理
    await new Promise(r => setTimeout(r, 3000));
    
    // 检查应用程序是否仍然正常运行
    const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
    await expect(dashboardTitle).toBeVisible();
  });

  test('文件夹扫描功能模拟测试', async ({ page }) => {
    await page.goto('http://localhost:1420/folder-analysis');
    
    // 等待React应用加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 测试基本的UI交互，不模拟具体的Tauri API调用
    // 因为Tauri API调用需要实际的桌面应用程序环境
    
    // 验证页面基本元素
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    await expect(pathInput).toBeVisible();
    
    const browseButton = page.locator('button:has-text("浏览")');
    await expect(browseButton).toBeVisible();
    
    const scanButton = page.locator('button:has-text("扫描文件夹")');
    await expect(scanButton).toBeVisible();
    
    // 测试输入框交互
    const testPath = 'C:\\test-folder';
    await pathInput.fill(testPath);
    await expect(pathInput).toHaveValue(testPath);
    
    // 测试按钮点击（不期望实际扫描成功，因为需要Tauri环境）
    await scanButton.click();
    
    // 等待可能的UI状态变化
    await new Promise(r => setTimeout(r, 2000));
    
    // 验证应用程序没有崩溃，仍然可以正常交互
    await expect(pathInput).toBeVisible();
    await expect(scanButton).toBeVisible();
    
    // 测试导航回仪表板
    const dashboardLink = page.locator('a[href="/"]');
    await dashboardLink.click();
    await new Promise(r => setTimeout(r, 2000));
    
    // 验证成功导航到仪表板
    const dashboardTitle = page.locator('h1').nth(1);
    await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  });

  test('长时间运行稳定性测试', async ({ page }) => {
    await page.goto('http://localhost:1420');
    
    // 模拟长时间运行
    for (let i = 0; i < 10; i++) {
      // 切换页面
      const dashboardLink = page.locator('a[href="/"]');
      const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
      
      await dashboardLink.click();
      await new Promise(r => setTimeout(r, 500));
      
      await folderAnalysisLink.click();
      await new Promise(r => setTimeout(r, 500));
    }
    
    // 最终状态检查
    const dashboardTitle = page.locator('h1');
    await expect(dashboardTitle).toBeVisible();
  });

  test('边界条件测试', async ({ page }) => {
    await page.goto('http://localhost:1420/folder-analysis');
    
    // 测试特殊字符路径
    const specialPaths = [
      'C:\\测试文件夹\\中文路径',
      'C:\\folder with spaces',
      'C:\\very-long-folder-name-that-exceeds-normal-limits'
    ];
    
    const pathInput = page.locator('input[placeholder*="文件夹路径"]');
    
    for (const path of specialPaths) {
      await pathInput.fill(path);
      await expect(pathInput).toHaveValue(path);
      await pathInput.clear();
    }
    
    // 测试空路径错误
    const scanButton = page.locator('button:has-text("扫描文件夹")');
    await scanButton.click();
    
    const errorMessage = page.locator('[class*="bg-red-50"]');
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test('性能测试', async ({ page }) => {
    await page.goto('http://localhost:1420');
    
    const startTime = Date.now();
    
    // 执行一系列操作
    for (let i = 0; i < 5; i++) {
      const dashboardLink = page.locator('a[href="/"]');
      const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
      
      await dashboardLink.click();
      await new Promise(r => setTimeout(r, 200));
      
      await folderAnalysisLink.click();
      await new Promise(r => setTimeout(r, 200));
    }
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // 性能要求：操作应在合理时间内完成
    expect(duration).toBeLessThan(10000); // 10秒内完成
    
    // 最终状态验证
    const dashboardTitle = page.locator('h1');
    await expect(dashboardTitle).toBeVisible();
  });
});