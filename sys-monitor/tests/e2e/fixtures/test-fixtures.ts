import { test as base, Page } from '@playwright/test';
import { DashboardPage, FolderAnalysisPage, BasePage } from '../pages';
import { injectTauriMock } from '../utils/tauriMock';

export type Fixtures = {
  dashboardPage: DashboardPage;
  folderAnalysisPage: FolderAnalysisPage;
  basePage: BasePage;
  authenticatedPage: Page;
};

export const test = base.extend<Fixtures>({
  page: async ({ page }, use) => {
    // Automatically inject Tauri mock for all tests
    await injectTauriMock(page);
    
    // Inject mock appState for web mode (must be after injectTauriMock)
    await page.addInitScript(() => {
      if (!(window as any).appState) {
        (window as any).appState = {
          isRunning: true,
          version: '1.0.0',
          monitoringEnabled: true,
          environment: 'web'
        };
      }
    });
    
    await use(page);
  },
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
