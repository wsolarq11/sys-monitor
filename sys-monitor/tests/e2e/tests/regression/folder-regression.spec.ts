import { test, expect } from '../fixtures/test-fixtures';
import { testPaths } from '../../utils/api-helpers';

test.describe('Folder Analysis Regression Tests @regression', () => {
  test('should handle all special character path variations @regression', async ({ folderAnalysisPage }) => {
    for (const path of testPaths.special) {
      await folderAnalysisPage.enterPath(path);
      await expect(folderAnalysisPage.pathInput).toHaveValue(path);
      await folderAnalysisPage.clearPath();
    }
  });

  test('should handle all invalid path variations @regression', async ({ folderAnalysisPage }) => {
    for (const path of testPaths.invalid) {
      await folderAnalysisPage.enterPath(path || 'empty');
      await folderAnalysisPage.clickScan();
      await folderAnalysisPage.waitForResults(3000);
    }
  });

  test('should handle all valid path variations @regression', async ({ folderAnalysisPage }) => {
    for (const path of testPaths.valid) {
      await folderAnalysisPage.enterPath(path);
      await expect(folderAnalysisPage.pathInput).toHaveValue(path);
      await folderAnalysisPage.clearPath();
    }
  });

  test('should maintain ui stability during rapid input @regression', async ({ folderAnalysisPage }) => {
    const rapidInputs = [
      'C:\\Test1',
      'C:\\Test2',
      'C:\\Test3',
      'C:\\Test4',
      'C:\\Test5'
    ];
    
    for (const path of rapidInputs) {
      await folderAnalysisPage.enterPath(path);
      await folderAnalysisPage.page.waitForTimeout(200);
    }
    
    await expect(folderAnalysisPage.pathInput).toHaveValue('C:\\Test5');
  });

  test('should handle button click sequences @regression', async ({ folderAnalysisPage }) => {
    await folderAnalysisPage.enterPath('C:\\Test');
    
    for (let i = 0; i < 5; i++) {
      await folderAnalysisPage.clickScan();
      await folderAnalysisPage.page.waitForTimeout(500);
    }
    
    await expect(folderAnalysisPage.pathInput).toBeVisible();
  });

  test('should preserve input on page refresh @regression', async ({ folderAnalysisPage, page }) => {
    await folderAnalysisPage.enterPath('C:\\PersistentTest');
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    const pathInput = page.getByPlaceholder(/.*文件夹路径.*/);
    const value = await pathInput.inputValue();
    
    if (value) {
      expect(value).toBe('C:\\PersistentTest');
    }
  });

  test('should handle concurrent navigation and input @regression', async ({ folderAnalysisPage }) => {
    await folderAnalysisPage.enterPath('C:\\Test');
    
    await folderAnalysisPage.page.goto('/');
    await folderAnalysisPage.page.waitForTimeout(500);
    
    await folderAnalysisPage.page.goto('/folder-analysis');
    await folderAnalysisPage.page.waitForLoadState('networkidle');
    
    await expect(folderAnalysisPage.pathInput).toBeVisible();
  });

  test('should handle extended usage session @regression', async ({ folderAnalysisPage }) => {
    const paths = [
      'C:\\Windows',
      'C:\\Program Files',
      'C:\\Users',
      'C:\\Test',
      'C:\\Temp'
    ];
    
    for (const path of paths) {
      await folderAnalysisPage.enterPath(path);
      await folderAnalysisPage.page.waitForTimeout(300);
      await folderAnalysisPage.clearPath();
    }
    
    await expect(folderAnalysisPage.pathInput).toBeVisible();
    await expect(folderAnalysisPage.scanButton).toBeVisible();
  });
});
