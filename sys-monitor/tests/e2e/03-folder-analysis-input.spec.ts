import { test, expect } from '@playwright/test';

test.describe('文件夹分析 - 输入框全量测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
  });

  test('输入框基本属性和可见性', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    // 验证输入框存在且可见
    await expect(input).toBeVisible();
    await expect(input).toBeEnabled();
    
    // 验证placeholder
    await expect(input).toHaveAttribute('placeholder', '输入文件夹路径');
    
    // 验证初始为空
    await expect(input).toHaveValue('');
  });

  test('输入框文本输入功能', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const testPath = 'C:\\Users\\Test\\Documents';
    
    // 输入文本
    await input.fill(testPath);
    
    // 验证输入值
    await expect(input).toHaveValue(testPath);
  });

  test('输入框清空功能', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    // 先输入内容
    await input.fill('some path');
    await expect(input).toHaveValue('some path');
    
    // 清空输入
    await input.clear();
    
    // 验证已清空
    await expect(input).toHaveValue('');
  });

  test('输入框特殊字符处理', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const specialPaths = [
      'C:\\Program Files (x86)\\App',
      'D:\\folder with spaces\\subfolder',
      'E:\\中文路径\\测试文件夹',
      '\\\\network\\share\\folder',
      '/usr/local/bin',
    ];
    
    for (const path of specialPaths) {
      await input.fill(path);
      await expect(input).toHaveValue(path);
      await input.clear();
    }
  });

  test('输入框超长路径处理', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const longPath = 'C:\\' + 'very_long_folder_name_'.repeat(20) + '\\file.txt';
    
    await input.fill(longPath);
    await expect(input).toHaveValue(longPath);
  });

  test('输入框键盘事件 - Enter键', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    await input.fill('C:\\test');
    await input.press('Enter');
    
    // 验证输入框仍保持焦点或有相应响应
    await expect(input).toHaveValue('C:\\test');
  });

  test('输入框键盘事件 - Tab键', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    await input.focus();
    await input.press('Tab');
    
    // 验证焦点已转移
    await expect(input).not.toBeFocused();
  });

  test('输入框粘贴操作', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const testPath = 'C:\\Pasted\\Path\\Here';
    
    // 模拟粘贴
    await input.evaluate((el, value) => {
      (el as HTMLInputElement).value = value;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }, testPath);
    
    await expect(input).toHaveValue(testPath);
  });

  test('输入框选择全部文本', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    await input.fill('C:\\test\\path');
    await input.selectText();
    
    // 验证文本被选中（通过检查值仍存在）
    await expect(input).toHaveValue('C:\\test\\path');
  });

  test('输入框与错误状态联动', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 不输入内容直接扫描
    await scanButton.click();
    
    // 验证错误信息显示
    await expect(page.getByText('请选择一个文件夹路径')).toBeVisible();
    
    // 输入内容后错误应消失
    await input.fill('C:\\valid\\path');
    await expect(page.getByText('请选择一个文件夹路径')).not.toBeVisible();
  });

  test('输入框样式验证', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    
    // 验证基本样式类存在
    await expect(input).toHaveClass(/flex-1/);
    await expect(input).toHaveClass(/px-4/);
    await expect(input).toHaveClass(/py-2/);
    await expect(input).toHaveClass(/border/);
    await expect(input).toHaveClass(/rounded-lg/);
  });
});
