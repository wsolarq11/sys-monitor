/**
 * Tauri API Mock 工具
 * 用于在 Playwright E2E 测试中模拟 Tauri invoke 调用
 */

import { Page } from '@playwright/test';

/**
 * Tauri 命令Mock配置接口
 */
export interface TauriCommandMock {
  command: string;
  response?: any;
  error?: string;
  delay?: number; // 模拟延迟(ms)
}

/**
 * 为页面注入Tauri API Mock
 */
export async function injectTauriMock(page: Page, mocks: TauriCommandMock[] = []) {
  await page.addInitScript(() => {
    // 创建全局 Tauri 对象
    window.__TAURI__ = {
      invoke: async (command: string, args?: any) => {
        // 这里会在测试时通过route拦截来模拟
        return new Promise((resolve, reject) => {
          // 默认实现，实际会被route拦截覆盖
          resolve(null);
        });
      },
      event: {
        listen: async (event: string, handler: any) => {
          return () => {}; // 返回取消监听函数
        },
        emit: async (event: string, payload?: any) => {},
      },
      dialog: {
        open: async (options?: any) => null,
        save: async (options?: any) => null,
      },
      fs: {
        readTextFile: async (path: string) => '',
        writeTextFile: async (path: string, contents: string) => {},
      },
    };
  });

  // 为每个mock命令设置路由拦截
  for (const mock of mocks) {
    await page.route(**/invoke/, async route => {
      if (mock.delay) {
        await page.waitForTimeout(mock.delay);
      }

      if (mock.error) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: mock.error })
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mock.response ?? null)
        });
      }
    });
  }
}

/**
 * 默认的文件夹分析相关Mock配置
 */
export const folderAnalysisMocks: TauriCommandMock[] = [
  {
    command: 'select_folder',
    response: 'C:\\\\test-folder'
  },
  {
    command: 'scan_folder',
    response: {
      total_size: 1048576,
      file_count: 100,
      folder_count: 10,
      scan_duration_ms: 1500
    }
  },
  {
    command: 'get_folder_scans',
    response: {
      scans: [
        {
          id: 1,
          path: 'C:\\\\test-folder',
          scan_timestamp: Math.floor(Date.now() / 1000),
          total_size: 1048576,
          file_count: 100,
          folder_count: 10
        }
      ]
    }
  },
  {
    command: 'get_folder_items',
    response: {
      items: [
        { name: 'file1.txt', size: 1024, type: 'file' },
        { name: 'folder1', size: 2048, type: 'folder' }
      ]
    }
  },
  {
    command: 'get_file_type_stats',
    response: {
      stats: [
        { extension: '.txt', count: 50, total_size: 51200 },
        { extension: '.jpg', count: 30, total_size: 524288 }
      ]
    }
  },
  {
    command: 'delete_folder_scan',
    response: { success: true }
  },
  {
    command: 'add_watched_folder',
    response: { id: 1, path: 'C:\\\\test-folder', is_active: true }
  },
  {
    command: 'list_watched_folders',
    response: {
      folders: [
        { id: 1, path: 'C:\\\\test-folder', is_active: true }
      ]
    }
  }
];

/**
 * 系统监控相关Mock配置
 */
export const systemMonitorMocks: TauriCommandMock[] = [
  {
    command: 'get_system_metrics',
    response: {
      cpu_usage: 45.5,
      memory_usage: 62.3,
      disk_usage: 75.8,
      network_usage: 12.5
    }
  },
  {
    command: 'get_cpu_info',
    response: {
      model: 'Intel Core i7',
      cores: 8,
      threads: 16,
      frequency: 2.8
    }
  },
  {
    command: 'get_memory_info',
    response: {
      total: 16777216,
      used: 10485760,
      free: 6291456,
      usage_percent: 62.5
    }
  },
  {
    command: 'get_disk_info',
    response: {
      disks: [
        {
          name: 'C:',
          total: 536870912000,
          used: 407374182400,
          free: 129496729600,
          usage_percent: 75.9
        }
      ]
    }
  },
  {
    command: 'get_network_info',
    response: {
      interfaces: [
        {
          name: 'Ethernet',
          bytes_sent: 1048576,
          bytes_recv: 2097152,
          packets_sent: 1000,
          packets_recv: 2000
        }
      ]
    }
  },
  {
    command: 'get_db_path',
    response: 'C:\\\\Users\\\\Test\\\\AppData\\\\Local\\\\sysmonitor\\\\data.db'
  }
];

/**
 * 错误场景Mock配置
 */
export const errorScenarioMocks: Record<string, TauriCommandMock[]> = {
  folderNotFound: [
    {
      command: 'scan_folder',
      error: '文件夹不存在: C:\\\\invalid-path'
    }
  ],
  
  permissionDenied: [
    {
      command: 'scan_folder',
      error: '权限不足，无法访问该文件夹'
    }
  ],
  
  databaseError: [
    {
      command: 'get_folder_scans',
      error: '数据库连接失败'
    }
  ],
  
  networkTimeout: [
    {
      command: 'get_system_metrics',
      error: '请求超时',
      delay: 5000
    }
  ]
};

/**
 * 快速设置常用Mock组合
 */
export async function setupCommonMocks(
  page: Page,
  scenario: 'folder-analysis' | 'system-monitor' | 'full-app' = 'full-app'
) {
  let mocks: TauriCommandMock[] = [];

  switch (scenario) {
    case 'folder-analysis':
      mocks = folderAnalysisMocks;
      break;
    case 'system-monitor':
      mocks = systemMonitorMocks;
      break;
    case 'full-app':
      mocks = [...folderAnalysisMocks, ...systemMonitorMocks];
      break;
  }

  await injectTauriMock(page, mocks);
}

/**
 * 模拟特定错误场景
 */
export async function simulateErrorScenario(
  page: Page,
  scenario: keyof typeof errorScenarioMocks
) {
  const mocks = errorScenarioMocks[scenario];
  await injectTauriMock(page, mocks);
}
