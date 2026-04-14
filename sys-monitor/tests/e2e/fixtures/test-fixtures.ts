import { test as base, Page } from '@playwright/test';
import { DashboardPage, FolderAnalysisPage, BasePage } from '../pages';

export type Fixtures = {
  dashboardPage: DashboardPage;
  folderAnalysisPage: FolderAnalysisPage;
  basePage: BasePage;
  authenticatedPage: Page;
};

export const test = base.extend<Fixtures>({
  dashboardPage: async ({ page }, use) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    await use(dashboardPage);
  },

  folderAnalysisPage: async ({ page }, use) => {
    const folderAnalysisPage = new FolderAnalysisPage(page);
    await folderAnalysisPage.goto();
    await use(folderAnalysisPage);
  },

  basePage: async ({ page }, use) => {
    const basePage = new BasePage(page);
    await use(basePage);
  },

  authenticatedPage: async ({ page }, use) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await use(page);
  }
});

export { expect } from '@playwright/test';
