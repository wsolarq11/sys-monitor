/**
 * 文件夹分析API单元测试
 * 
 * 测试范围：
 * - invokeSafe错误处理
 * - isUserCancelled检测
 * - API函数参数验证
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { 
  invokeSafe, 
  isUserCancelled,
  selectFolder,
  scanFolder,
  getFolderScans,
  deleteFolderScan,
  addWatchedFolder,
  listWatchedFolders,
  removeWatchedFolder,
  toggleWatchedFolderActive,
  type FolderScan,
} from '../services/folderAnalysisApi';

// Mock Tauri API
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

import { invoke as tauriInvoke } from '@tauri-apps/api/core';

describe('invokeSafe', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该成功调用Tauri命令并返回结果', async () => {
    const mockResult = { success: true };
    (tauriInvoke as any).mockResolvedValue(mockResult);

    const result = await invokeSafe('get_db_path');
    
    expect(result).toEqual(mockResult);
    expect(tauriInvoke).toHaveBeenCalledWith('get_db_path', undefined);
  });

  it('应该在命令失败时抛出错误', async () => {
    const mockError = new Error('Command failed');
    (tauriInvoke as any).mockRejectedValue(mockError);

    await expect(invokeSafe('get_db_path')).rejects.toThrow('Command failed');
  });

  it('应该记录调试日志', async () => {
    const consoleDebugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});
    (tauriInvoke as any).mockResolvedValue({});

    await invokeSafe('get_db_path');

    expect(consoleDebugSpy).toHaveBeenCalledWith('[TauriAPI] Calling get_db_path', undefined);
    expect(consoleDebugSpy).toHaveBeenCalledWith('[TauriAPI] get_db_path succeeded', {});
    
    consoleDebugSpy.mockRestore();
  });
});

describe('isUserCancelled', () => {
  it('应该检测到用户取消操作（no folder selected）', () => {
    const error = 'No folder selected';
    expect(isUserCancelled(error)).toBe(true);
  });

  it('应该检测到用户取消操作（cancelled）', () => {
    const error = 'Operation cancelled';
    expect(isUserCancelled(error)).toBe(true);
  });

  it('应该检测到用户取消操作（canceled）', () => {
    const error = 'User canceled the operation';
    expect(isUserCancelled(error)).toBe(true);
  });

  it('不应该将其他错误识别为取消', () => {
    const error = 'Permission denied';
    expect(isUserCancelled(error)).toBe(false);
  });

  it('应该处理大小写不敏感', () => {
    expect(isUserCancelled('NO FOLDER SELECTED')).toBe(true);
    expect(isUserCancelled('Cancelled')).toBe(true);
  });
});

describe('selectFolder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该调用select_folder命令', async () => {
    (tauriInvoke as any).mockResolvedValue('/test/path');

    const result = await selectFolder();

    expect(tauriInvoke).toHaveBeenCalledWith('select_folder', undefined);
    expect(result).toBe('/test/path');
  });

  it('应该返回null当用户取消时', async () => {
    (tauriInvoke as any).mockResolvedValue(null);

    const result = await selectFolder();

    expect(result).toBeNull();
  });
});

describe('scanFolder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该成功扫描文件夹', async () => {
    const mockResult = {
      total_size: 1024000,
      file_count: 100,
      folder_count: 10,
      scan_duration_ms: 500,
    };
    (tauriInvoke as any).mockResolvedValue(mockResult);

    const result = await scanFolder('/test/path', 'data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('scan_folder', {
      path: '/test/path',
      db_path: 'data.db',
    });
    expect(result).toEqual(mockResult);
  });

  it('应该在路径为空时抛出错误', async () => {
    await expect(scanFolder('', 'data.db')).rejects.toThrow('路径不能为空');
  });

  it('应该在路径只有空格时抛出错误', async () => {
    await expect(scanFolder('   ', 'data.db')).rejects.toThrow('路径不能为空');
  });
});

describe('getFolderScans', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该获取扫描历史（默认limit=10）', async () => {
    const mockScans: FolderScan[] = [
      { id: 1, path: '/test', scan_timestamp: 1000, total_size: 1000, file_count: 10, folder_count: 2, scan_duration_ms: 100 },
    ];
    (tauriInvoke as any).mockResolvedValue(mockScans);

    const result = await getFolderScans('/test/path', 'data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('get_folder_scans', {
      path: '/test/path',
      limit: 10,
      db_path: 'data.db',
    });
    expect(result).toEqual(mockScans);
  });

  it('应该使用自定义的limit', async () => {
    const mockScans: FolderScan[] = [];
    (tauriInvoke as any).mockResolvedValue(mockScans);

    await getFolderScans('/test/path', 'data.db', 5);

    expect(tauriInvoke).toHaveBeenCalledWith('get_folder_scans', {
      path: '/test/path',
      limit: 5,
      db_path: 'data.db',
    });
  });
});

describe('deleteFolderScan', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该删除扫描记录', async () => {
    (tauriInvoke as any).mockResolvedValue(undefined);

    await deleteFolderScan(123, 'data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('delete_folder_scan', {
      scanId: 123,
      db_path: 'data.db',
    });
  });
});

describe('addWatchedFolder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该添加监控文件夹（无别名）', async () => {
    (tauriInvoke as any).mockResolvedValue(1);

    const result = await addWatchedFolder('/test/path', 'data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('add_watched_folder', {
      path: '/test/path',
      alias: undefined,
      db_path: 'data.db',
    });
    expect(result).toBe(1);
  });

  it('应该添加监控文件夹（带别名）', async () => {
    (tauriInvoke as any).mockResolvedValue(2);

    const result = await addWatchedFolder('/test/path', 'data.db', 'My Folder');

    expect(tauriInvoke).toHaveBeenCalledWith('add_watched_folder', {
      path: '/test/path',
      alias: 'My Folder',
      db_path: 'data.db',
    });
    expect(result).toBe(2);
  });
});

describe('listWatchedFolders', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该列出所有监控文件夹', async () => {
    const mockFolders = [
      { id: 1, path: '/test1', is_active: true, recursive: true, debounce_ms: 500, notify_on_create: true, notify_on_delete: true, notify_on_modify: true, total_events_count: 0 },
      { id: 2, path: '/test2', is_active: false, recursive: false, debounce_ms: 500, notify_on_create: false, notify_on_delete: false, notify_on_modify: false, total_events_count: 5 },
    ];
    (tauriInvoke as any).mockResolvedValue(mockFolders);

    const result = await listWatchedFolders('data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('list_watched_folders', {
      db_path: 'data.db',
    });
    expect(result).toEqual(mockFolders);
  });
});

describe('removeWatchedFolder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该移除监控文件夹', async () => {
    (tauriInvoke as any).mockResolvedValue(undefined);

    await removeWatchedFolder(1, 'data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('remove_watched_folder', {
      folder_id: 1,
      db_path: 'data.db',
    });
  });
});

describe('toggleWatchedFolderActive', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该激活监控文件夹', async () => {
    (tauriInvoke as any).mockResolvedValue(true);

    const result = await toggleWatchedFolderActive(1, true, 'data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('toggle_watched_folder_active', {
      folder_id: 1,
      is_active: true,
      db_path: 'data.db',
    });
    expect(result).toBe(true);
  });

  it('应该停用监控文件夹', async () => {
    (tauriInvoke as any).mockResolvedValue(false);

    const result = await toggleWatchedFolderActive(1, false, 'data.db');

    expect(tauriInvoke).toHaveBeenCalledWith('toggle_watched_folder_active', {
      folder_id: 1,
      is_active: false,
      db_path: 'data.db',
    });
    expect(result).toBe(false);
  });
});
