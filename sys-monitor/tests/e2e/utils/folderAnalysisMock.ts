/**
 * FolderAnalysis 模块 E2E 测试 - Tauri Mock 配置
 * 
 * 为 Playwright E2E 测试提供 Tauri API Mock
 */

import { test as base } from '@playwright/test';

/**
 * 注入 Tauri Mock 到页面
 */
export async function injectFolderAnalysisMock(page: any) {
  await page.addInitScript(() => {
    // 模拟 Tauri 环境
    (window as any).__TAURI_INTERNALS__ = {
      invoke: async (cmd: string, args?: any) => {
        console.log(`[Tauri Mock] ${cmd}`, args);

        switch (cmd) {
          // ==================== 数据库路径 ====================
          case 'get_db_path':
            return 'data.db';

          // ==================== 文件夹选择 ====================
          case 'select_folder':
            // 模拟用户选择文件夹(使用Unix路径以兼容浏览器环境)
            return '/test-folder';

          // ==================== 文件夹扫描 ====================
          case 'scan_folder':
            // 模拟扫描结果
            return {
              total_size: 1048576, // 1MB
              file_count: 100,
              folder_count: 10,
              scan_duration_ms: 523,
            };

          // ==================== 扫描历史 ====================
          case 'get_folder_scans':
            return {
              scans: [
                {
                  id: 1,
                  path: args?.path || '/test-folder',
                  scan_timestamp: Date.now() / 1000 - 3600, // 1小时前
                  total_size: 1048576,
                  file_count: 100,
                  folder_count: 10,
                  scan_duration_ms: 523,
                },
                {
                  id: 2,
                  path: args?.path || '/test-folder',
                  scan_timestamp: Date.now() / 1000 - 7200, // 2小时前
                  total_size: 2097152, // 2MB
                  file_count: 200,
                  folder_count: 20,
                  scan_duration_ms: 1024,
                },
              ],
            };

          // ==================== 监控文件夹管理 ====================
          case 'list_watched_folders':
            return [
              {
                id: 1,
                path: 'C:\\Users\\Documents',
                alias: '文档文件夹',
                is_active: true,
                recursive: true,
                debounce_ms: 500,
                notify_on_create: true,
                notify_on_delete: true,
                notify_on_modify: false,
                total_events_count: 42,
                last_event_timestamp: Date.now() / 1000 - 300,
              },
              {
                id: 2,
                path: 'D:\\Projects',
                alias: undefined,
                is_active: false,
                recursive: true,
                debounce_ms: 500,
                notify_on_create: true,
                notify_on_delete: true,
                notify_on_modify: true,
                total_events_count: 128,
                last_event_timestamp: Date.now() / 1000 - 86400,
              },
            ];

          case 'add_watched_folder':
            return {
              id: 3,
              path: args?.path,
              alias: args?.alias,
              is_active: true,
              recursive: true,
              debounce_ms: 500,
              notify_on_create: true,
              notify_on_delete: true,
              notify_on_modify: false,
              total_events_count: 0,
            };

          case 'remove_watched_folder':
            return undefined;

          case 'toggle_watched_folder_active':
            return undefined;

          // ==================== 高级功能 ====================
          case 'get_folder_items':
            return [
              { name: 'file1.txt', size: 1024, type: 'file' },
              { name: 'file2.pdf', size: 2048, type: 'file' },
              { name: 'subfolder', size: 0, type: 'folder' },
            ];

          case 'get_file_type_stats':
            return [
              { extension: '.txt', count: 50, total_size: 51200 },
              { extension: '.pdf', count: 30, total_size: 307200 },
              { extension: '.jpg', count: 20, total_size: 204800 },
            ];

          case 'delete_folder_scan':
            return undefined;

          // ==================== 默认处理 ====================
          default:
            console.warn(`[Tauri Mock] 未Mock的命令: ${cmd}`);
            throw new Error(`Command ${cmd} not mocked`);
        }
      },
    };

    // 兼容旧版本 Tauri API
    (window as any).__TAURI__ = {
      core: {
        invoke: (window as any).__TAURI_INTERNALS__.invoke,
      },
    };
  });
}

/**
 * 模拟错误场景
 */
export async function simulateErrorScenario(page: any, scenario: 'cancel' | 'error' | 'timeout') {
  await page.addInitScript((scenarioType: string) => {
    const originalInvoke = (window as any).__TAURI_INTERNALS__.invoke;

    (window as any).__TAURI_INTERNALS__.invoke = async (cmd: string, args?: any) => {
      if (scenarioType === 'cancel' && cmd === 'select_folder') {
        // 模拟用户取消
        throw new Error('No folder selected');
      }

      if (scenarioType === 'error' && cmd === 'scan_folder') {
        // 模拟扫描失败
        throw new Error('Permission denied: Access to path denied');
      }

      if (scenarioType === 'timeout') {
        // 模拟超时
        return new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Operation timed out')), 5000);
        });
      }

      return originalInvoke(cmd, args);
    };
  }, scenario);
}

/**
 * 扩展 Playwright test fixture
 */
export const test = base.extend<{
  mockTauri: void;
}>({
  mockTauri: async ({ page }, use) => {
    await injectFolderAnalysisMock(page);
    await use();
  },
});

export { expect } from '@playwright/test';
