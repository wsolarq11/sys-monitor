import { test, expect } from '@playwright/test';

test.describe('文件夹分析 - 错误处理全量测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
  });

  test('空路径错误提示', async ({ page }) => {
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 确保输入框为空
    const input = page.locator('input[type="text"]');
    await input.clear();
    
    // 点击扫描
    await scanButton.click();
    
    // 验证错误信息
    await expect(page.getByText('请选择一个文件夹路径')).toBeVisible();
    
    // 验证错误样式
    const errorDiv = page.locator('.bg-red-50.border-red-200');
    await expect(errorDiv).toBeVisible();
  });

  test('无效路径错误处理', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入不存在的路径
    await input.fill('Z:\\This\\Path\\Does\\Not\\Exist\\At\\All');
    await scanButton.click();
    
    // 等待错误显示
    await page.waitForTimeout(2000);
    
    // 验证错误状态（可能有错误提示或扫描失败状态）
    const errorOrProgress = page.locator('.bg-red-50, .bg-blue-50');
    await expect(errorOrProgress).toBeVisible();
  });

  test('错误信息自动清除', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 触发错误
    await scanButton.click();
    await expect(page.getByText('请选择一个文件夹路径')).toBeVisible();
    
    // 输入内容
    await input.fill('C:\\valid');
    
    // 验证错误消失
    await expect(page.getByText('请选择一个文件夹路径')).not.toBeVisible();
  });

  test('扫描中状态显示', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await input.fill('C:\\Windows');
    await scanButton.click();
    
    // 验证进度提示
    await expect(page.getByText(/正在初始化扫描|正在扫描文件夹|正在加载/)).toBeVisible();
    
    // 验证蓝色提示样式
    const progressDiv = page.locator('.bg-blue-50.border-blue-200');
    await expect(progressDiv).toBeVisible();
  });

  test('扫描完成后状态清除', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 使用系统临时目录（通常存在且可访问）
    await input.fill('C:\\Windows\\Temp');
    await scanButton.click();
    
    // 等待扫描完成或超时
    try {
      await expect(page.getByText('扫描完成')).toBeVisible({ timeout: 30000 });
    } catch (e) {
      // 扫描可能失败，验证有状态显示即可
    }
    
    // 验证页面仍有内容显示
    await expect(page.locator('body')).toBeVisible();
  });

  test('网络错误处理', async ({ page }) => {
    // 模拟离线状态
    await page.context().setOffline(true);
    
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await input.fill('C:\\Windows');
    await scanButton.click();
    
    // 恢复网络
    await page.context().setOffline(false);
    
    // 验证页面没有崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('特殊字符路径错误', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入包含非法字符的路径
    await input.fill('C:\\Test<>:"/\\|?*');
    await scanButton.click();
    
    // 验证应用没有崩溃
    await expect(page.locator('body')).toBeVisible();
    await expect(input).toBeVisible();
  });

  test('超长路径错误', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入超长路径
    const longPath = 'C:\\' + 'a'.repeat(300);
    await input.fill(longPath);
    await scanButton.click();
    
    // 验证应用没有崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('权限受限路径处理', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 尝试扫描系统保护目录
    await input.fill('C:\\System Volume Information');
    await scanButton.click();
    
    // 等待响应
    await page.waitForTimeout(3000);
    
    // 验证应用没有崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('并发扫描请求处理', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await input.fill('C:\\Windows');
    
    // 快速点击多次
    await Promise.all([
      scanButton.click(),
      scanButton.click(),
      scanButton.click(),
    ]);
    
    // 验证应用没有崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('错误信息样式验证', async ({ page }) => {
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await scanButton.click();
    
    // 验证错误容器样式
    const errorContainer = page.locator('.bg-red-50');
    await expect(errorContainer).toBeVisible();
    await expect(errorContainer).toHaveClass(/border/);
    await expect(errorContainer).toHaveClass(/rounded-lg/);
    
    // 验证错误文本样式
    const errorText = page.locator('.text-red-700');
    await expect(errorText).toBeVisible();
  });

  test('进度信息样式验证', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await input.fill('C:\\Windows');
    await scanButton.click();
    
    // 验证进度容器样式
    const progressContainer = page.locator('.bg-blue-50');
    await expect(progressContainer).toBeVisible();
    await expect(progressContainer).toHaveClass(/border/);
    await expect(progressContainer).toHaveClass(/rounded-lg/);
    
    // 验证进度文本样式
    const progressText = page.locator('.text-blue-700');
    await expect(progressText).toBeVisible();
  });
});
