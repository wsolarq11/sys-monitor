/**
 * Zustand Store 统一导出
 */

// Metrics Store - 系统指标管理
export { useMetricsStore } from './metricsStore';
export type { SystemMetric, MetricsStats } from './metricsStore';

// Scan Store - 文件夹扫描管理
export { useScanStore } from './scanStore';
export type {
  ScanProgress,
  ScanResult,
  ScanHistoryItem,
  ScanError,
} from './scanStore';

// Alert Store - 警报管理
export { useAlertStore } from './alertStore';
export { AlertLevel, AlertType } from './alertStore';
export type { Alert } from './alertStore';

// Settings Store - 应用配置管理
export { useSettingsStore } from './settingsStore';
export type {
  ThemeMode,
  ScanSettings,
  AlertSettings,
  UISettings,
  DatabaseSettings,
  AppSettings,
} from './settingsStore';
