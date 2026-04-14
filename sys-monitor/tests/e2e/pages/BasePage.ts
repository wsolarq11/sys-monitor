import { Page, Locator } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  readonly navigation: Locator;
  readonly header: Locator;

  constructor(page: Page) {
    this.page = page;
    this.navigation = page.getByRole('navigation');
    this.header = page.getByRole('heading', { name: /sysmonitor/i });
  }

  async isNavigationVisible() {
    await expect(this.navigation).toBeVisible();
    return true;
  }

  async isHeaderVisible() {
    await expect(this.header).toBeVisible();
    return true;
  }

  async waitForLoadState(state: 'load' | 'domcontentloaded' | 'networkidle' = 'networkidle') {
    await this.page.waitForLoadState(state);
  }

  async setViewportSize(width: number, height: number) {
    await this.page.setViewportSize({ width, height });
  }

  async takeScreenshot(name: string, options?: { fullPage?: boolean; mask?: Locator[] }) {
    await expect(this.page).toHaveScreenshot(name, options);
  }
}
