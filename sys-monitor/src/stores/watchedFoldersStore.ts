import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { useShallow } from 'zustand/react/shallow';
import {
  getDbPath,
  listWatchedFolders,
  addWatchedFolder,
  removeWatchedFolder,
  toggleWatchedFolderActive,
} from '../services/folderAnalysisApi';

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

interface WatchedFoldersState {
  folders: WatchedFolder[];
  loading: boolean;
  error: string | null;
  
  fetchFolders: () => Promise<void>;
  addFolder: (path: string, alias?: string) => Promise<void>;
  removeFolder: (id: number) => Promise<void>;
  toggleActive: (id: number) => Promise<void>;
}

export const useWatchedFoldersStore = create<WatchedFoldersState>()(
  devtools(
    (set, get) => ({
      folders: [],
      loading: false,
      error: null,
      
      fetchFolders: async () => {
        set({ loading: true, error: null });
        try {
          const dbPath = await getDbPath();
          const folders = await listWatchedFolders(dbPath);
          set({ folders, loading: false });
        } catch (error) {
          set({ error: String(error), loading: false });
        }
      },
      
      addFolder: async (path: string, alias?: string) => {
        try {
          const dbPath = await getDbPath();
          // ✅ 修复: addWatchedFolder 现在返回 folder_id (number)，不需要使用返回值
          await addWatchedFolder(path, dbPath, alias);
          await get().fetchFolders(); // 刷新列表
        } catch (error) {
          set({ error: String(error) });
          throw error;
        }
      },
      
      removeFolder: async (id: number) => {
        try {
          const dbPath = await getDbPath();
          await removeWatchedFolder(id, dbPath);
          await get().fetchFolders();
        } catch (error) {
          set({ error: String(error) });
          throw error;
        }
      },
      
      toggleActive: async (id: number) => {
        const previousState = get().folders.find(f => f.id === id);
        if (!previousState) {
          throw new Error(`Folder with id ${id} not found`);
        }
        
        const newState = !previousState.is_active;
        
        // 1. 乐观更新 UI
        set((state) => ({
          folders: state.folders.map((folder) =>
            folder.id === id ? { ...folder, is_active: newState } : folder
          ),
          error: null,
        }));
        
        try {
          // 2. 调用 API
          const dbPath = await getDbPath();
          // ✅ 修复: toggleWatchedFolderActive 现在返回 boolean
          await toggleWatchedFolderActive(id, newState, dbPath);
          
          // 3. 成功后刷新完整列表以确保一致性
          await get().fetchFolders();
        } catch (error) {
          // 4. 失败时回滚
          console.warn('[WatchedFoldersStore] 回滚乐观更新:', error);
          set((state) => ({
            folders: state.folders.map((folder) =>
              folder.id === id ? { ...folder, is_active: previousState.is_active } : folder
            ),
            error: String(error),
          }));
          throw error;
        }
      },
    }),
    { name: 'WatchedFoldersStore' }
  )
);

// ==================== 自定义 Hooks（性能优化）====================

/**
 * 获取监控文件夹列表
 */
export function useWatchedFolders() {
  return useWatchedFoldersStore(
    useShallow((state) => state.folders)
  );
}

/**
 * 获取加载状态
 */
export function useWatchedFoldersLoading() {
  return useWatchedFoldersStore((state) => state.loading);
}

/**
 * 获取错误信息
 */
export function useWatchedFoldersError() {
  return useWatchedFoldersStore((state) => state.error);
}
