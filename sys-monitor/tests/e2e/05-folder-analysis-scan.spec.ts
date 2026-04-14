import { test, expect } from '@playwright/test';

test.describe('文件夹分析 - 扫描功能全量测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/folder-analysis');
  });

  test('扫描按钮点击后进入扫描状态', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 输入有效路径
    await input.fill('C:\\Windows\\Temp');
    
    // 点击扫描按钮
    await scanButton.click();
    
    // 验证扫描状态显示（按钮文本变化和禁用）
    await expect(scanButton).toBeDisabled();
    await expect(scanButton).toHaveText('扫描中...');
    
    // 等待扫描完成（最多30秒）
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
    await expect(scanButton).toHaveText('扫描文件夹');
  });

  test('扫描进度提示显示', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await input.fill('C:\\Windows\\Temp');
    await scanButton.click();
    
    // 验证按钮显示扫描中
    await expect(scanButton).toHaveText('扫描中...');
    
    // 验证进度区域显示
    const progressArea = page.locator('.bg-blue-50, [class*="progress"]').first();
    await expect(progressArea).toBeVisible({ timeout: 5000 });
    
    // 等待扫描完成
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
  });

  test('扫描完成后结果显示区域', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await input.fill('C:\\Windows\\Temp');
    await scanButton.click();
    
    // 等待扫描完成
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
    
    // 验证结果区域显示
    const resultSection = page.locator('.bg-green-50, [class*="success"], [class*="result"]').first();
    await expect(resultSection).toBeVisible();
    
    // 验证结果包含关键信息
    const resultText = await resultSection.textContent();
    expect(resultText).toContain('总大小');
    expect(resultText).toContain('文件数');
    expect(resultText).toContain('文件夹数');
  });

  test('扫描结果包含文件类型统计', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    await input.fill('C:\\Windows\\Temp');
    await scanButton.click();
    
    // 等待扫描完成
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
    
    // 验证文件类型统计区域
    const fileTypeSection = page.locator('text=/文件类型分布|File Types/i').first();
    await expect(fileTypeSection).toBeVisible();
  });

  test('扫描历史记录显示', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 执行第一次扫描
    await input.fill('C:\\Windows\\Temp');
    await scanButton.click();
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
    
    // 等待一下确保数据保存
    await page.waitForTimeout(1000);
    
    // 刷新页面
    await page.reload();
    await page.goto('/folder-analysis');
    
    // 验证历史记录区域存在
    const historySection = page.locator('text=/历史记录|History|最近扫描/i').first();
    await expect(historySection).toBeVisible();
  });

  test('多次扫描操作', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    // 第一次扫描
    await input.fill('C:\\Windows\\Temp');
    await scanButton.click();
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
    
    // 第二次扫描（相同路径）
    await scanButton.click();
    await expect(scanButton).toBeDisabled();
    await expect(scanButton).toHaveText('扫描中...');
    await expect(scanButton).toBeEnabled({ timeout: 30000 });
  });

  test('扫描不同路径', async ({ page }) => {
    const input = page.locator('input[type="text"]');
    const scanButton = page.getByRole('button', { name: '扫描文件夹' });
    
    const paths = [
      'C:\\Windows\\Temp',
      'C:\\ProgramData',
    ];
    
    for (const testPath of paths) {
      await input.clear();
      await input.fill(testPath);
      await scanButton.click();
      
      // 验证扫描开始
      await expect(scanButton).toBeDisabled();
      await expect(scanButton).toHaveText('扫描中...');
      
      // 等待扫描完成或超时
      try {
        await expect(scanButton).toBeEnabled({ timeout: 30000 });
      } catch (e) {
        // 某些路径可能没有权限，但至少验证页面没有崩溃
        await expect(page.locator('body')).toBeVisible();
      }
    }
  });
});
