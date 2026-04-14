import { Page, Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  
  // 导航元素
  readonly dashboardLink: Locator;
  readonly folderAnalysisLink: Locator;
  
  // 系统监控组件
  readonly cpuMonitor: Locator;
  readonly memoryMonitor: Locator;
  readonly diskUsageCard: Locator;
  
  // 图表组件
  readonly cpuGraph: Locator;
  readonly memoryGraph: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // 使用 getByRole 优先策略
    this.dashboardLink = page.getByRole('link', { name: /dashboard/i });
    this.folderAnalysisLink = page.getByRole('link', { name: /folder analysis/i });
    
    // 系统监控组件 - 使用 heading 和 text 组合
    this.cpuMonitor = page.getByText(/cpu usage/i).first();
    this.memoryMonitor = page.getByText(/memory usage/i).first();
    this.diskUsageCard = page.getByText(/disk usage/i).first();
    
    // 图表组件 - 使用 heading
    this.cpuGraph = page.getByRole('heading', { name: /cpu usage over time/i });
    this.memoryGraph = page.getByRole('heading', { name: /memory usage over time/i });
  }

  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async isLoaded() {
    await expect(this.page.getByRole('heading', { name: /sysmonitor dashboard/i })).toBeVisible();
    return true;
  }

  async navigateToFolderAnalysis() {
    await this.folderAnalysisLink.click();
    await this.page.waitForURL(/.*folder-analysis/);
  }

  async getCpuUsage() {
    const cpuText = await this.page.getByText(/%/).first().textContent();
    return cpuText?.match(/\d+\.\d+%/)?.[0] || null;
  }

  async getMemoryUsage() {
    const memoryText = await this.page.getByText(/gb/i).first().textContent();
    return memoryText?.match(/\d+\.\d+\s*gb/i)?.[0] || null;
  }

  async waitForRealTimeUpdate(timeout = 5000) {
    await this.page.waitForTimeout(timeout);
  }
}
