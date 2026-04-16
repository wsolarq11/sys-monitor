import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { useShallow } from 'zustand/react/shallow';

/**
 * 主题模式
 */
export enum ThemeMode {
  Light = 'light',
  Dark = 'dark',
  System = 'system',
}

/**
 * 扫描配置
 */
export interface ScanSettings {
  maxDepth: number;           // 最大扫描深度
  includeHidden: boolean;     // 包含隐藏文件
  excludePatterns: string[];  // 排除模式
  followSymlinks: boolean;    // 跟随符号链接
  autoScanOnStartup: boolean; // 启动时自动扫描
}

/**
 * 警报配置
 */
export interface AlertSettings {
  enabled: boolean;           // 启用警报
  soundEnabled: boolean;      // 启用声音
  desktopNotifications: boolean; // 桌面通知
  cpuThreshold: number;       // CPU 阈值 (%)
  memoryThreshold: number;    // 内存阈值 (%)
  diskThreshold: number;      // 磁盘阈值 (%)
}

/**
 * 界面配置
 */
export interface UISettings {
  theme: ThemeMode;           // 主题模式
  language: 'zh-CN' | 'en-US'; // 语言
  compactMode: boolean;       // 紧凑模式
  showGraphs: boolean;        // 显示图表
  refreshInterval: number;    // 刷新间隔 (ms)
}

/**
 * 数据库配置
 */
export interface DatabaseSettings {
  path: string;               // 数据库路径
  autoBackup: boolean;        // 自动备份
  backupInterval: number;     // 备份间隔 (小时)
  maxHistoryDays: number;     // 最大历史天数
}

/**
 * 完整应用配置
 */
export interface AppSettings {
  scan: ScanSettings;
  alert: AlertSettings;
  ui: UISettings;
  database: DatabaseSettings;
}

interface SettingsState {
  // 状态
  settings: AppSettings;
  loading: boolean;
  error: string | null;
  lastSaved: number | null;
  
  // Actions - 设置更新
  updateScanSettings: (settings: Partial<ScanSettings>) => void;
  updateAlertSettings: (settings: Partial<AlertSettings>) => void;
  updateUISettings: (settings: Partial<UISettings>) => void;
  updateDatabaseSettings: (settings: Partial<DatabaseSettings>) => void;
  
  // Actions - 状态管理
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setLastSaved: (timestamp: number) => void;
  
  // Actions - 重置
  resetToDefaults: () => void;
  loadSettings: (settings: AppSettings) => void;
}

const defaultSettings: AppSettings = {
  scan: {
    maxDepth: 10,
    includeHidden: false,
    excludePatterns: ['node_modules', '.git', '__pycache__'],
    followSymlinks: false,
    autoScanOnStartup: false,
  },
  alert: {
    enabled: true,
    soundEnabled: true,
    desktopNotifications: true,
    cpuThreshold: 80,
    memoryThreshold: 85,
    diskThreshold: 90,
  },
  ui: {
    theme: ThemeMode.System,
    language: 'zh-CN',
    compactMode: false,
    showGraphs: true,
    refreshInterval: 5000,
  },
  database: {
    path: '',
    autoBackup: true,
    backupInterval: 24,
    maxHistoryDays: 30,
  },
};

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set) => ({
        // 初始状态
        settings: defaultSettings,
        loading: false,
        error: null,
        lastSaved: null,
        
        // Actions - 设置更新
        updateScanSettings: (newSettings) => set((state) => ({
          settings: {
            ...state.settings,
            scan: { ...state.settings.scan, ...newSettings },
          },
          lastSaved: Date.now(),
        })),
        
        updateAlertSettings: (newSettings) => set((state) => ({
          settings: {
            ...state.settings,
            alert: { ...state.settings.alert, ...newSettings },
          },
          lastSaved: Date.now(),
        })),
        
        updateUISettings: (newSettings) => set((state) => ({
          settings: {
            ...state.settings,
            ui: { ...state.settings.ui, ...newSettings },
          },
          lastSaved: Date.now(),
        })),
        
        updateDatabaseSettings: (newSettings) => set((state) => ({
          settings: {
            ...state.settings,
            database: { ...state.settings.database, ...newSettings },
          },
          lastSaved: Date.now(),
        })),
        
        // Actions - 状态管理
        setLoading: (loading) => set({ loading }),
        setError: (error) => set({ error }),
        setLastSaved: (timestamp) => set({ lastSaved: timestamp }),
        
        // Actions - 重置
        resetToDefaults: () => set({
          settings: defaultSettings,
          lastSaved: Date.now(),
        }),
        
        loadSettings: (settings) => set({
          settings,
          lastSaved: Date.now(),
        }),
      }),
      {
        name: 'app-settings',
        // 只持久化 settings，不持久化临时状态
        partialize: (state) => ({ settings: state.settings }),
        // 版本迁移支持
        version: 2,
        migrate: (persistedState, version) => {
          const state = persistedState as SettingsState;
          
          // v1 -> v2: 添加新的配置项
          if (version === 1) {
            return {
              ...state,
              settings: {
                ...state.settings,
                // 确保新字段有默认值
                ui: {
                  ...state.settings.ui,
                  compactMode: state.settings.ui.compactMode ?? false,
                },
              },
            };
          }
          
          return state;
        },
      }
    ),
    { name: 'SettingsStore' }
  )
);

// ==================== 自定义 Hooks（性能优化）====================

/**
 * 获取完整应用配置
 */
export function useAppSettings() {
  return useSettingsStore(
    useShallow((state) => state.settings)
  );
}

/**
 * 获取扫描配置
 */
export function useScanSettings() {
  return useSettingsStore(
    useShallow((state) => state.settings.scan)
  );
}

/**
 * 获取警报配置
 */
export function useAlertSettings() {
  return useSettingsStore(
    useShallow((state) => state.settings.alert)
  );
}

/**
 * 获取界面配置
 */
export function useUISettings() {
  return useSettingsStore(
    useShallow((state) => state.settings.ui)
  );
}

/**
 * 获取数据库配置
 */
export function useDatabaseSettings() {
  return useSettingsStore(
    useShallow((state) => state.settings.database)
  );
}
