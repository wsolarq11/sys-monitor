import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  
  fullyParallel: process.env.CI ? false : true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  timeout: process.env.CI ? 60000 : 120000,
  expect: {
    timeout: process.env.CI ? 5000 : 10000
  },
  
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit-results.xml' }],
    ...(process.env.CI ? [['github'] as const] : [])
  ],
  
  use: {
    baseURL: 'http://localhost:1420',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1920, height: 1080 },
    actionTimeout: 10000,
    navigationTimeout: 30000
  },
  
  projects: [
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/
    },
    
    {
      name: 'smoke',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/smoke/**/*.spec.ts',
      grep: /@smoke/,
      timeout: 30000
    },
    
    {
      name: 'critical',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/critical/**/*.spec.ts',
      grep: /@critical/,
      timeout: 60000,
      dependencies: ['setup']
    },
    
    {
      name: 'regression',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/regression/**/*.spec.ts',
      grep: /@regression/,
      timeout: 120000,
      dependencies: ['setup']
    },
    
    {
      name: 'e2e-chromium',
      use: { ...devices['Desktop Chrome'] },
      testIgnore: ['**/smoke/**', '**/critical/**', '**/regression/**']
    }
  ],
  
  webServer: {
    command: process.env.CI ? 'pnpm dev' : 'pnpm dev',
    url: 'http://localhost:1420',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
    stdout: 'pipe',
    stderr: 'pipe'
  },
  
  outputDir: 'test-results/output',
  preserveOutput: process.env.CI ? 'failures-only' : 'always',
  
  metadata: {
    environment: process.env.CI ? 'ci' : 'local',
    timestamp: new Date().toISOString()
  }
});