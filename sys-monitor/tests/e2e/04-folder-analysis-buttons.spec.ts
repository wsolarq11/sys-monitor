import { test, expect } from '@playwright/test';

test.describe('文件夹分析 - 按钮全量测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
  });

  test('浏览按钮基本属性和可见性', async ({ page }) => {
    const browseButton = page.getByRole('button', { name: '浏览...' });
    
    await expect(browseButton).toBeVisible();
    await expect(browseButton).toBeEnabled();
    await expect(browseButton).toHaveText('浏览...');
  });

  test('扫描按钮基本属性和可见性', async ({ page }) => {
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await expect(scanButton).toBeVisible();
    await expect(scanButton).toBeEnabled();
    await expect(scanButton).toHaveText('扫描文件夹');
  });

  test('浏览按钮样式验证', async ({ page }) => {
    const browseButton = page.getByRole('button', { name: '浏览...' });
    
    await expect(browseButton).toHaveClass(/bg-blue-600/);
    await expect(browseButton).toHaveClass(/text-white/);
    await expect(browseButton).toHaveClass(/rounded-lg/);
    await expect(browseButton).toHaveClass(/hover:bg-blue-700/);
  });

  test('扫描按钮样式验证', async ({ page }) => {
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await expect(scanButton).toHaveClass(/bg-indigo-600/);
    await expect(scanButton).toHaveClass(/text-white/);
    await expect(scanButton).toHaveClass(/rounded-lg/);
    await expect(scanButton).toHaveClass(/disabled:bg-gray-400/);
  });

  test('浏览按钮悬停效果', async ({ page }) => {
    const browseButton = page.getByRole('button', { name: '浏览...' });
    
    await browseButton.hover();
    await expect(browseButton).toBeVisible();
  });

  test('扫描按钮悬停效果', async ({ page }) => {
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await scanButton.hover();
    await expect(scanButton).toBeVisible();
  });

  test('浏览按钮点击触发文件对话框', async ({ page }) => {
    const browseButton = page.getByRole('button', { name: '浏览...' });
    
    // 点击浏览按钮
    await browseButton.click();
    
    // 由于文件对话框是系统级别的，我们验证按钮点击不会导致错误
    await expect(browseButton).toBeVisible();
  });

  test('扫描按钮无路径时显示错误', async ({ page }) => {
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 确保输入框为空
    const input = page.locator('input[type="text"]');
    await input.clear();
    
    // 点击扫描按钮
    await scanButton.click();
    
    // 验证错误信息显示
    await expect(page.getByText('请选择一个文件夹路径')).toBeVisible();
  });

  test('扫描按钮有路径时进入扫描状态', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入有效路径
    await input.fill('C:\\Windows\\Temp');
    
    // 点击扫描按钮
    await scanButton.click();
    
    // 验证按钮进入禁用状态且文本变为"扫描中..."
    await expect(scanButton).toBeDisabled();
    await expect(scanButton).toHaveText('扫描中...');
    
    // 等待扫描完成
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
    await expect(scanButton).toHaveText('扫描文件夹');
  });

  test('扫描按钮禁用状态样式', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入路径并点击扫描
    await input.fill('C:\\Windows\\Temp');
    await scanButton.click();
    
    // 验证禁用状态有视觉指示
    await expect(scanButton).toBeDisabled();
    await expect(scanButton).toHaveClass(/disabled:bg-gray-400/);
    
    // 等待扫描完成
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
  });

  test('按钮键盘导航', async ({ page }) => {
    const browseButton = page.getByRole('button', { name: '浏览...' });
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    const input = page.locator('input[type="text"]');
    
    // 聚焦输入框
    await input.focus();
    
    // 按Tab键导航到浏览按钮
    await page.keyboard.press('Tab');
    await expect(browseButton).toBeFocused();
    
    // 再按Tab导航到扫描按钮
    await page.keyboard.press('Tab');
    await expect(scanButton).toBeFocused();
  });

  test('按钮回车键激活', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入路径
    await input.fill('C:\\Windows\\Temp');
    
    // 聚焦扫描按钮并按回车
    await scanButton.focus();
    await page.keyboard.press('Enter');
    
    // 验证扫描开始（按钮文本变化且禁用）
    await expect(scanButton).toBeDisabled();
    await expect(scanButton).toHaveText('扫描中...');
    
    // 等待扫描完成
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
  });

  test('快速连续点击扫描按钮', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入路径
    await input.fill('C:\\Windows\\Temp');
    
    // 快速连续点击
    await scanButton.click();
    await scanButton.click();
    await scanButton.click();
    
    // 验证只触发一次扫描（按钮被禁用）
    await expect(scanButton).toBeDisabled();
    await expect(scanButton).toHaveText('扫描中...');
    
    // 等待扫描完成
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
  });
});
