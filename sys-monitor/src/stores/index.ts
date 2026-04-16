/**
 * Zustand Store 统一导出
 * 
 * 提供所有 Store 的访问入口和类型定义
 */

// Metrics Store - 系统指标管理
export { useMetricsStore } from './metricsStore';
export type { SystemMetric, MetricsStats } from './metricsStore';
export { 
  useCurrentMetrics,
  useHistoricalMetrics,
  useMetricsLoading,
  useMetricsError,
  useMetricsStats,
} from './metricsStore';

// Scan Store - 文件夹扫描管理
export { useScanStore } from './scanStore';
export type {
  ScanProgress,
  ScanResult,
  ScanHistoryItem,
  ScanError,
} from './scanStore';
export {
  useSelectedPath,
  useIsScanning,
  useScanProgress,
  useCurrentScan,
  useScanHistory,
  useScanError,
} from './scanStore';

// Alert Store - 警报管理
export { useAlertStore, AlertLevel, AlertType } from './alertStore';
export type { Alert } from './alertStore';
export {
  useAlerts,
  useUnreadCount,
  useUnresolvedAlerts,
} from './alertStore';

// Settings Store - 应用配置管理
export { useSettingsStore, ThemeMode } from './settingsStore';
export type {
  ScanSettings,
  AlertSettings,
  UISettings,
  DatabaseSettings,
  AppSettings,
} from './settingsStore';
export {
  useAppSettings,
  useScanSettings,
  useAlertSettings,
  useUISettings,
  useDatabaseSettings,
} from './settingsStore';

// Watched Folders Store - 监控文件夹管理
export { useWatchedFoldersStore } from './watchedFoldersStore';
export type { WatchedFolder } from './watchedFoldersStore';
export {
  useWatchedFolders,
  useWatchedFoldersLoading,
  useWatchedFoldersError,
} from './watchedFoldersStore';
