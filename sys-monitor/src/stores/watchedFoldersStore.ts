import { create } from 'zustand';
import { invoke } from '@tauri-apps/api/core';

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

export const useWatchedFoldersStore = create<WatchedFoldersState>()((set, get) => ({
  folders: [],
  loading: false,
  error: null,
  
  fetchFolders: async () => {
    set({ loading: true, error: null });
    try {
      const dbPath = await invoke<string>('get_db_path');
      const folders = await invoke<WatchedFolder[]>('list_watched_folders', { dbPath });
      set({ folders, loading: false });
    } catch (error) {
      set({ error: String(error), loading: false });
    }
  },
  
  addFolder: async (path: string, alias?: string) => {
    try {
      const dbPath = await invoke<string>('get_db_path');
      await invoke('add_watched_folder', { path, alias, dbPath });
      await get().fetchFolders(); // 刷新列表
    } catch (error) {
      set({ error: String(error) });
      throw error;
    }
  },
  
  removeFolder: async (id: number) => {
    try {
      const dbPath = await invoke<string>('get_db_path');
      await invoke('remove_watched_folder', { folderId: id, dbPath });
      await get().fetchFolders();
    } catch (error) {
      set({ error: String(error) });
      throw error;
    }
  },
  
  toggleActive: async (id: number) => {
    try {
      const dbPath = await invoke<string>('get_db_path');
      
      // 获取当前状态
      const currentState = get().folders.find(f => f.id === id);
      if (!currentState) {
        throw new Error(`Folder with id ${id} not found`);
      }
      
      // 切换状态并调用后端
      const newState = !currentState.is_active;
      await invoke('toggle_watched_folder_active', { 
        folderId: id, 
        isActive: newState,
        dbPath 
      });
      
      // 更新本地状态
      set((state) => ({
        folders: state.folders.map((folder) =>
          folder.id === id ? { ...folder, is_active: newState } : folder
        ),
      }));
    } catch (error) {
      set({ error: String(error) });
      throw error;
    }
  },
}));
