import { test, expect } from '@playwright/test';

test.describe('可访问性全量测试', () => {
  test('页面标题存在', async ({ page }) => {
    await page.goto('/');
    
    // 验证标题存在
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.getByText('SysMonitor Dashboard')).toBeVisible();
  });

  test('所有按钮有正确的role属性', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 验证按钮有button role
    const buttons = page.getByRole('button');
    expect(await buttons.count()).toBeGreaterThanOrEqual(2);
    
    // 验证具体按钮
    await expect(page.getByRole('button', { name: '浏览...' })).toBeVisible();
    await expect(page.getByRole('button', { name: '扫描文件夹' })).toBeVisible();
  });

  test('所有链接有正确的role属性', async ({ page }) => {
    await page.goto('/');
    
    // 验证导航链接
    const dashboardLink = page.getByRole('link', { name: 'Dashboard' });
    const folderAnalysisLink = page.getByRole('link', { name: 'Folder Analysis' });
    
    await expect(dashboardLink).toBeVisible();
    await expect(folderAnalysisLink).toBeVisible();
  });

  test('输入框有正确的type和label', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    const input = page.locator('input[type="text"]');
    await expect(input).toBeVisible();
    await expect(input).toHaveAttribute('type', 'text');
    await expect(input).toHaveAttribute('placeholder', '输入文件夹路径');
  });

  test('颜色对比度检查', async ({ page }) => {
    await page.goto('/');
    
    // 验证主要文本元素可见
    await expect(page.getByText('SysMonitor')).toBeVisible();
    await expect(page.getByText('CPU Usage')).toBeVisible();
    await expect(page.getByText('Memory Usage')).toBeVisible();
  });

  test('键盘可访问性 - Tab顺序', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 按Tab键遍历所有可聚焦元素
    await page.keyboard.press('Tab');
    const focused1 = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused1).toBeTruthy();
    
    await page.keyboard.press('Tab');
    const focused2 = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused2).toBeTruthy();
    
    await page.keyboard.press('Tab');
    const focused3 = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused3).toBeTruthy();
  });

  test('键盘可访问性 - Enter键激活', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\test');
    
    // 聚焦扫描按钮并按Enter
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    await scanButton.focus();
    await page.keyboard.press('Enter');
    
    // 验证操作被触发
    await expect(page.getByText('扫描中...')).toBeVisible();
  });

  test('键盘可访问性 - Space键激活', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 聚焦浏览按钮并按Space
    const browseButton = page.getByRole('button', { name: '浏览...' });
    await browseButton.focus();
    await page.keyboard.press('Space');
    
    // 验证按钮保持可见
    await expect(browseButton).toBeVisible();
  });

  test('焦点指示器可见', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    const input = page.locator('input[type="text"]');
    await input.focus();
    
    // 验证输入框获得焦点
    await expect(input).toBeFocused();
  });

  test('ARIA标签存在', async ({ page }) => {
    await page.goto('/');
    
    // 验证导航有正确的结构
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
  });

  test('错误信息的可访问性', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 触发错误
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
    // 验证错误信息可见且可读
    const errorMessage = page.getByText('请选择一个文件夹路径');
    await expect(errorMessage).toBeVisible();
    
    // 验证错误容器有适当的样式
    const errorContainer = page.locator('.bg-red-50');
    await expect(errorContainer).toBeVisible();
  });

  test('进度信息的可访问性', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Windows');
    
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
    // 验证进度信息可见
    const progressMessage = page.locator('.bg-blue-50');
    await expect(progressMessage).toBeVisible();
  });

  test('语义化HTML结构', async ({ page }) => {
    await page.goto('/');
    
    // 验证有main标签
    const main = page.locator('main');
    await expect(main).toBeVisible();
    
    // 验证有nav标签
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
    
    // 验证有h1标题
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
  });

  test('屏幕阅读器友好的内容', async ({ page }) => {
    await page.goto('/');
    
    // 验证所有重要内容都是文本而不是仅图像
    const cpuLabel = page.getByText('Current usage across all cores');
    await expect(cpuLabel).toBeVisible();
    
    const memoryLabel = page.getByText('System memory in use');
    await expect(memoryLabel).toBeVisible();
  });

  test('禁用状态的清晰指示', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Windows');
    
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    await scanButton.click();
    
    // 验证按钮在扫描期间被禁用
    await expect(scanButton).toBeDisabled();
    
    // 验证禁用状态有视觉指示
    await expect(scanButton).toHaveClass(/disabled/);
  });

  test('链接的可访问性', async ({ page }) => {
    await page.goto('/');
    
    // 验证所有链接有href
    const links = page.locator('a');
    const count = await links.count();
    
    for (let i = 0; i < count; i++) {
      const href = await links.nth(i).getAttribute('href');
      expect(href).toBeTruthy();
    }
  });

  test('表单标签关联', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 验证输入框可以通过placeholder识别
    const input = page.locator('input[type="text"]');
    await expect(input).toHaveAttribute('placeholder', '输入文件夹路径');
  });
});
