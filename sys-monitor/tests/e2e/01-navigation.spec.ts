import { test, expect } from '@playwright/test';

test.describe('导航功能全量测试', () => {
  test('首页导航链接可见性', async ({ page }) => {
    await page.goto('/');
    
    // 验证导航栏存在
    await expect(page.locator('nav')).toBeVisible();
    
    // 验证Logo/标题（使用更具体的选择器）
    await expect(page.locator('nav').getByText('SysMonitor')).toBeVisible();
    
    // 验证导航链接
    await expect(page.getByRole('link', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Folder Analysis' })).toBeVisible();
  });

  test('Dashboard链接点击跳转', async ({ page }) => {
    await page.goto('/folder-analysis');
    
    // 点击Dashboard链接
    await page.getByRole('link', { name: 'Dashboard' }).click();
    
    // 验证URL变化
    await expect(page).toHaveURL(/\/$/);
    
    // 验证页面内容
    await expect(page.getByText('SysMonitor Dashboard')).toBeVisible();
  });

  test('Folder Analysis链接点击跳转', async ({ page }) => {
    await page.goto('/');
    
    // 点击Folder Analysis链接
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    
    // 验证URL变化
    await expect(page).toHaveURL(/\/folder-analysis$/);
    
    // 验证页面内容
    await expect(page.locator('input[type="text"]')).toBeVisible();
  });

  test('导航链接href属性验证', async ({ page }) => {
    await page.goto('/');
    
    // 验证链接href
    await expect(page.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('href', '/');
    await expect(page.getByRole('link', { name: 'Folder Analysis' })).toHaveAttribute('href', '/folder-analysis');
  });

  test('快速导航切换', async ({ page }) => {
    await page.goto('/');
    
    // 快速切换多次
    for (let i = 0; i < 5; i++) {
      await page.getByRole('link', { name: 'Folder Analysis' }).click();
      await expect(page).toHaveURL(/\/folder-analysis$/);
      
      await page.getByRole('link', { name: 'Dashboard' }).click();
      await expect(page).toHaveURL(/\/$/);
    }
  });

  test('浏览器前进后退导航', async ({ page }) => {
    await page.goto('/');
    
    // 导航到Folder Analysis
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    await expect(page).toHaveURL(/\/folder-analysis$/);
    
    // 点击后退
    await page.goBack();
    await expect(page).toHaveURL(/\/$/);
    
    // 点击前进
    await page.goForward();
    await expect(page).toHaveURL(/\/folder-analysis$/);
  });
});
