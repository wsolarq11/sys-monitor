import { defineConfig, devices } from '@playwright/test';
import path from 'path';

/**
 * 针对打包后应用程序的Playwright配置
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report-prod' }],
    ['list']
  ],
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  timeout: 120000,
  
  // 使用Tauri应用程序作为webServer
  webServer: {
    command: 'cd "d:\\Users\\Administrator\\Desktop\\PowerShell_Script_Repository\\FolderSizeMonitor\\sys-monitor\\src-tauri\\target\\release" && start /B sys-monitor.exe',
    url: 'http://localhost:1420',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
  },
});
