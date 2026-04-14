import { defineConfig, devices } from '@playwright/test';

// Tauri应用程序专用配置
export default defineConfig({
  testDir: './tests',
  fullyParallel: false, // Tauri应用需要顺序测试
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1, // 单线程运行，避免应用程序冲突
  timeout: 60000, // 60秒超时
  
  reporter: [
    ['html'],
    ['json', { outputFile: 'tauri-test-results.json' }],
    ['junit', { outputFile: 'tauri-junit-results.xml' }]
  ],
  
  use: {
    baseURL: 'http://localhost:1420',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1200, height: 800 } // 匹配应用程序窗口尺寸
  },
  
  projects: [
    {
      name: 'tauri-functional',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/functional.spec.ts'
    }
  ],
  
  // 自定义web服务器配置，用于模拟Tauri应用环境
  webServer: {
    command: 'echo "Tauri应用程序测试模式 - 请手动启动应用程序"',
    url: 'http://localhost:1420',
    reuseExistingServer: true,
    timeout: 10000
  }
});