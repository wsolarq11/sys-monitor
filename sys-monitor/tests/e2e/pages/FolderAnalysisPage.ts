import { Page, Locator } from '@playwright/test';

export class FolderAnalysisPage {
  readonly page: Page;
  
  // 输入元素
  readonly pathInput: Locator;
  readonly scanButton: Locator;
  readonly browseButton: Locator;
  
  // 结果展示
  readonly resultsContainer: Locator;
  readonly errorMessage: Locator;
  readonly loadingIndicator: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // 使用 getByRole 和 getByPlaceholder 优先策略
    this.pathInput = page.getByPlaceholder(/.*文件夹路径.*/);
    this.scanButton = page.getByRole('button', { name: /扫描文件夹/i });
    this.browseButton = page.getByRole('button', { name: /浏览/i });
    
    // 结果展示
    this.resultsContainer = page.getByTestId('folder-results');
    this.errorMessage = page.getByText(/error|错误|invalid/i);
    this.loadingIndicator = page.getByText(/scanning|loading|扫描中/i);
  }

  async goto() {
    await this.page.goto('/folder-analysis');
    await this.page.waitForLoadState('networkidle');
  }

  async isLoaded() {
    await expect(this.pathInput).toBeVisible();
    return true;
  }

  async enterPath(path: string) {
    await this.pathInput.fill(path);
  }

  async clearPath() {
    await this.pathInput.clear();
  }

  async getPathValue() {
    return await this.pathInput.inputValue();
  }

  async clickScan() {
    await this.scanButton.click();
  }

  async clickBrowse() {
    await this.browseButton.click();
  }

  async waitForResults(timeout = 10000) {
    await this.page.waitForTimeout(timeout);
  }

  async hasError() {
    return await this.errorMessage.isVisible();
  }

  async isLoading() {
    return await this.loadingIndicator.isVisible();
  }

  async waitForError(timeout = 5000) {
    await expect(this.errorMessage).toBeVisible({ timeout });
  }
}
