import { test, expect } from '../fixtures/test-fixtures';

test.describe('Folder Analysis Smoke Tests @smoke', () => {
  test('should load folder analysis page @smoke', async ({ folderAnalysisPage }) => {
    await expect(folderAnalysisPage.pathInput).toBeVisible();
    await expect(folderAnalysisPage.scanButton).toBeVisible();
    await expect(folderAnalysisPage.browseButton).toBeVisible();
  });

  test('should accept valid folder path @smoke', async ({ folderAnalysisPage }) => {
    const testPath = 'C:\\Windows';
    await folderAnalysisPage.enterPath(testPath);
    await expect(folderAnalysisPage.pathInput).toHaveValue(testPath);
  });

  test('should show error for empty path @smoke', async ({ folderAnalysisPage }) => {
    await folderAnalysisPage.clickScan();
    await folderAnalysisPage.waitForError(5000);
    await expect(folderAnalysisPage.hasError()).toBeTruthy();
  });

  test('should clear input field @smoke', async ({ folderAnalysisPage }) => {
    await folderAnalysisPage.enterPath('C:\\Test');
    await folderAnalysisPage.clearPath();
    await expect(folderAnalysisPage.pathInput).toHaveValue('');
  });
});
