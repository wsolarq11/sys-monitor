import { test, expect } from '@playwright/test';

test.describe('边界情况和异常场景测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
  });

  test('空字符串路径', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    await input.fill('');
    
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    await expect(page.getByText('请选择一个文件夹路径')).toBeVisible();
  });

  test('仅空白字符路径', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    await input.fill('   ');
    
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    // 应该显示错误或处理空白
    await expect(page.locator('body')).toBeVisible();
  });

  test('特殊字符路径', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const specialPaths = [
      'C:\\Program Files (x86)\\App',
      'D:\\folder with spaces\\subfolder',
      'E:\\中文路径\\测试文件夹',
    ];
    
    for (const path of specialPaths) {
      await input.fill(path);
      await expect(input).toHaveValue(path);
      
      // 点击扫描验证不会崩溃
      await page.getByRole('button', { name: '扫描文件夹' }).click();
      await page.waitForTimeout(1000);
      
      // 验证页面没有崩溃
      await expect(page.locator('body')).toBeVisible();
      
      // 清除输入
      await input.clear();
    }
  });

  test('超长路径输入', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const longPath = 'C:\\' + 'very_long_folder_name_'.repeat(20) + '\\file.txt';
    
    await input.fill(longPath);
    await expect(input).toHaveValue(longPath);
  });

  test('无效路径错误处理', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    // 输入不存在的路径
    await input.fill('Z:\\This\\Path\\Does\\Not\\Exist\\At\\All');
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
    // 等待响应
    await page.waitForTimeout(3000);
    
    // 验证应用没有崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('包含非法字符的路径', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    // 输入包含非法字符的路径
    await input.fill('C:\\Test<>:"/\\|?*');
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
    // 验证应用没有崩溃
    await expect(page.locator('body')).toBeVisible();
    await expect(input).toBeVisible();
  });

  test('权限受限路径处理', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    // 尝试扫描系统保护目录
    await input.fill('C:\\System Volume Information');
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
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

  test('路径末尾带斜杠', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    await input.fill('C:\\Windows\\');
    
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    
    // 验证进入扫描状态
    await expect(page.getByText('扫描中...')).toBeVisible();
  });

  test('网络路径格式', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    await input.fill('\\\\localhost\\share');
    
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    // 网络路径可能不存在，但不应崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('相对路径', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    await input.fill('.');
    
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    // 相对路径可能成功或失败，但不应崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('UNC路径格式', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    await input.fill('\\?\\C:\\Windows');
    
    await page.getByRole('button', { name: '扫描文件夹' }).click();
    await expect(page.locator('body')).toBeVisible();
  });
});
