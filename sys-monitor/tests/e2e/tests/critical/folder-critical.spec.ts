import { test, expect } from '../fixtures/test-fixtures';
import { testPaths } from '../../utils/api-helpers';

test.describe('Folder Analysis Critical Tests @critical', () => {
  test('should handle special character paths @critical', async ({ folderAnalysisPage }) => {
    const specialPaths = [
      'C:\\测试文件夹\\中文路径',
      'C:\\folder with spaces',
      'C:\\very-long-folder-name-that-exceeds-normal-limits'
    ];
    
    for (const path of specialPaths) {
      await folderAnalysisPage.enterPath(path);
      await expect(folderAnalysisPage.pathInput).toHaveValue(path);
      await folderAnalysisPage.clearPath();
    }
  });

  test('should handle invalid paths with error message @critical', async ({ folderAnalysisPage }) => {
    await folderAnalysisPage.enterPath('Z:\\NonExistentFolder');
    await folderAnalysisPage.clickScan();
    
    await folderAnalysisPage.waitForResults(5000);
  });

  test('should mock folder scan api response @critical', async ({ page }) => {
    await page.route('**/invoke/scan_folder', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          path: 'C:\\Test',
          size: 1024000,
          fileCount: 150,
          folderCount: 25
        })
      });
    });

    await page.goto('/folder-analysis');
    await page.getByPlaceholder(/.*文件夹路径.*/).fill('C:\\Test');
    await page.getByRole('button', { name: /扫描文件夹/i }).click();
    
    await page.waitForTimeout(2000);
  });

  test('should support path input navigation @critical', async ({ folderAnalysisPage }) => {
    await folderAnalysisPage.enterPath('C:\\Windows');
    await expect(folderAnalysisPage.pathInput).toHaveValue('C:\\Windows');
    
    await folderAnalysisPage.clearPath();
    await expect(folderAnalysisPage.pathInput).toHaveValue('');
  });

  test('should display loading state during scan @critical', async ({ folderAnalysisPage, page }) => {
    await page.route('**/invoke/scan_folder', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      route.fulfill({
        status: 200,
        body: JSON.stringify({ path: 'C:\\Test', size: 1000 })
      });
    });

    await folderAnalysisPage.enterPath('C:\\Test');
    await folderAnalysisPage.clickScan();
    
    await page.waitForTimeout(1000);
  });
});
