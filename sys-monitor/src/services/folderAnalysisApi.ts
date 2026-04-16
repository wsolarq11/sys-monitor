/**
 * Tauri API 封装层 - FolderAnalysis 模块专用
 * 
 * 提供类型安全的 Tauri 命令调用接口
 * 统一错误处理和日志记录
 * 支持测试环境 Mock
 */

import { invoke as tauriInvoke } from '@tauri-apps/api/core';

// ==================== 类型定义 ====================

/**
 * 扫描结果数据
 */
export interface ScanResultData {
  total_size: number;
  file_count: number;
  folder_count: number;
  scan_duration_ms: number; // 改为非null,与View保持一致
}

/**
 * 文件夹扫描历史记录
 */
export interface FolderScan {
  id: number;
  path: string; // 添加path字段,与View保持一致
  scan_timestamp: number; // 改为number类型,与View保持一致
  total_size: number;
  file_count: number;
  folder_count: number;
  scan_duration_ms: number | null;
}

/**
 * 监控文件夹
 */
export interface WatchedFolder {
  id: number;
  path: string;
  alias?: string;
  is_active: boolean;
  recursive: boolean;
  debounce_ms: number;
  size_threshold_bytes?: number;
  file_count_threshold?: number;
  notify_on_create: boolean;
  notify_on_delete: boolean;
  notify_on_modify: boolean;
  last_scan_timestamp?: number;
  last_event_timestamp?: number;
  total_events_count: number;
}

/**
 * Tauri 命令参数和返回值类型映射
 */
export interface TauriCommands {
  // 文件夹选择
  select_folder: {
    params: {};
    result: string | null;
  };
  
  // 数据库路径
  get_db_path: {
    params: {};
    result: string;
  };
  
  // 文件夹扫描
  scan_folder: {
    params: { path: string; db_path: string };
    result: ScanResultData;
  };
  
  // 获取扫描历史
  get_folder_scans: {
    params: { path: string; limit: number; db_path: string };
    result: FolderScan[]; // ✅ 修复: 后端直接返回数组，不是包装对象
  };
  
  // 获取文件夹项目列表
  get_folder_items: {
    params: { path: string; db_path: string };
    result: any[];
  };
  
  // 获取文件类型统计
  get_file_type_stats: {
    params: { path: string; db_path: string };
    result: any[];
  };
  
  // 删除扫描记录
  delete_folder_scan: {
    params: { scanId: number; db_path: string };
    result: void;
  };
  
  // 添加监控文件夹
  add_watched_folder: {
    params: { path: string; alias?: string; db_path: string }; // ✅ 修复: dbPath -> db_path
    result: number; // ✅ 修复: 后端返回 folder_id (Rust i64 对应 TS number)
  };
  
  // 列出监控文件夹
  list_watched_folders: {
    params: { db_path: string }; // ✅ 修复: dbPath -> db_path
    result: WatchedFolder[];
  };
  
  // 移除监控文件夹
  remove_watched_folder: {
    params: { folder_id: number; db_path: string }; // ✅ 修复: folderId -> folder_id, dbPath -> db_path
    result: void;
  };
  
  // 切换监控状态
  toggle_watched_folder_active: {
    params: { folder_id: number; is_active: boolean; db_path: string }; // ✅ 修复: 参数名统一为 snake_case
    result: boolean; // ✅ 修复: 后端返回 bool
  };
}

// ==================== 核心工具函数 ====================

/**
 * 判断是否为用户取消操作
 */
export function isUserCancelled(error: unknown): boolean {
  const errorMsg = String(error).toLowerCase();
  return (
    errorMsg.includes('no folder selected') ||
    errorMsg.includes('cancelled') ||
    errorMsg.includes('canceled')
  );
}

/**
 * 统一的 Tauri 命令调用函数
 * 
 * @param command - Tauri 命令名称
 * @param params - 命令参数
 * @returns 命令执行结果
 * 
 * @example
 * ```typescript
 * const path = await invokeSafe('select_folder');
 * const result = await invokeSafe('scan_folder', { path: 'C:\\test', db_path: 'data.db' });
 * ```
 */
export async function invokeSafe<K extends keyof TauriCommands>(
  command: K,
  params?: TauriCommands[K]['params']
): Promise<TauriCommands[K]['result']> {
  try {
    console.debug(`[TauriAPI] Calling ${command}`, params);
    const result = await tauriInvoke<TauriCommands[K]['result']>(command, params);
    console.debug(`[TauriAPI] ${command} succeeded`, result);
    return result;
  } catch (error) {
    console.error(`[TauriAPI] ${command} failed:`, error);
    throw error;
  }
}

// ==================== 文件夹选择相关 ====================

/**
 * 打开文件夹选择对话框
 * 
 * @returns 用户选择的文件夹路径，如果取消则返回 null
 * 
 * @example
 * ```typescript
 * const path = await selectFolder();
 * if (path) {
 *   console.log('Selected:', path);
 * } else {
 *   console.log('User cancelled');
 * }
 * ```
 */
export async function selectFolder(): Promise<string | null> {
  return invokeSafe('select_folder');
}

/**
 * 获取数据库路径
 * 
 * @returns 数据库文件的绝对路径
 */
export async function getDbPath(): Promise<string> {
  return invokeSafe('get_db_path');
}

// ==================== 文件夹扫描相关 ====================

/**
 * 扫描指定文件夹
 * 
 * @param path - 要扫描的文件夹路径
 * @param dbPath - 数据库路径
 * @returns 扫描结果（总大小、文件数、文件夹数等）
 * 
 * @example
 * ```typescript
 * const result = await scanFolder('C:\\Users', 'data.db');
 * console.log(`Total size: ${result.total_size} bytes`);
 * ```
 */
export async function scanFolder(
  path: string,
  dbPath: string
): Promise<ScanResultData> {
  if (!path || !path.trim()) {
    throw new Error('路径不能为空');
  }
  
  return invokeSafe('scan_folder', { path, db_path: dbPath });
}

/**
 * 获取文件夹的扫描历史记录
 * 
 * @param path - 文件夹路径
 * @param dbPath - 数据库路径
 * @param limit - 返回记录数量限制（默认10）
 * @returns 扫描历史记录列表
 */
export async function getFolderScans(
  path: string,
  dbPath: string,
  limit: number = 10
): Promise<FolderScan[]> {
  // ✅ 修复: 后端直接返回 FolderScan[]，不需要解包 .scans
  return invokeSafe('get_folder_scans', {
    path,
    limit,
    db_path: dbPath,
  });
}

/**
 * 删除指定的扫描记录
 * 
 * @param scanId - 扫描记录ID
 * @param dbPath - 数据库路径
 */
export async function deleteFolderScan(
  scanId: number,
  dbPath: string
): Promise<void> {
  return invokeSafe('delete_folder_scan', { scanId, db_path: dbPath });
}

// ==================== 监控文件夹管理 ====================

/**
 * 添加监控文件夹
 * 
 * @param path - 文件夹路径
 * @param dbPath - 数据库路径
 * @param alias - 可选的别名
 * @returns 创建的监控文件夹 ID
 */
export async function addWatchedFolder(
  path: string,
  dbPath: string,
  alias?: string
): Promise<number> {
  // ✅ 修复: 使用 db_path 而不是 dbPath，返回值是 folder_id (number)
  return invokeSafe('add_watched_folder', { path, alias, db_path: dbPath });
}

/**
 * 列出所有监控文件夹
 * 
 * @param dbPath - 数据库路径
 * @returns 监控文件夹列表
 */
export async function listWatchedFolders(dbPath: string): Promise<WatchedFolder[]> {
  // ✅ 修复: 使用 db_path 而不是 dbPath
  return invokeSafe('list_watched_folders', { db_path: dbPath });
}

/**
 * 移除监控文件夹
 * 
 * @param folderId - 文件夹ID
 * @param dbPath - 数据库路径
 */
export async function removeWatchedFolder(
  folderId: number,
  dbPath: string
): Promise<void> {
  // ✅ 修复: 使用 folder_id 和 db_path
  return invokeSafe('remove_watched_folder', { folder_id: folderId, db_path: dbPath });
}

/**
 * 切换监控文件夹的激活状态
 * 
 * @param folderId - 文件夹ID
 * @param isActive - 新的激活状态
 * @param dbPath - 数据库路径
 * @returns 操作是否成功
 */
export async function toggleWatchedFolderActive(
  folderId: number,
  isActive: boolean,
  dbPath: string
): Promise<boolean> {
  // ✅ 修复: 使用 folder_id, is_active, db_path
  return invokeSafe('toggle_watched_folder_active', { 
    folder_id: folderId, 
    is_active: isActive, 
    db_path: dbPath 
  });
}

// ==================== 高级功能 ====================

/**
 * 获取文件夹项目列表
 * 
 * @param path - 文件夹路径
 * @param dbPath - 数据库路径
 * @returns 文件夹项目列表
 */
export async function getFolderItems(path: string, dbPath: string): Promise<any[]> {
  return invokeSafe('get_folder_items', { path, db_path: dbPath });
}

/**
 * 获取文件类型统计信息
 * 
 * @param path - 文件夹路径
 * @param dbPath - 数据库路径
 * @returns 文件类型统计数据
 */
export async function getFileTypeStats(path: string, dbPath: string): Promise<any[]> {
  return invokeSafe('get_file_type_stats', { path, db_path: dbPath });
}
