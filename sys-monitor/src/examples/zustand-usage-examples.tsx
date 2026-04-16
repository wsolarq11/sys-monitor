/**
 * Zustand Store 使用示例
 * 
 * 本文件展示了如何使用优化后的 Zustand Stores
 * 
 * 注意：这是示例文件，仅用于演示目的，不会被实际使用
 */

/* eslint-disable @typescript-eslint/no-unused-vars */

import React from 'react';
import { 
  // Metrics Store
  useCurrentMetrics,
  useHistoricalMetrics,
  useMetricsLoading,
  useMetricsError,
  useMetricsStats,
  useMetricsStore,
  
  // Alert Store
  useAlerts,
  useUnreadCount,
  useUnresolvedAlerts,
  useAlertStore,
  AlertLevel,
  AlertType,
  
  // Settings Store
  useAppSettings,
  useScanSettings,
  useAlertSettings,
  useUISettings,
  useSettingsStore,
  ThemeMode,
  
  // Scan Store
  useSelectedPath,
  useIsScanning,
  useScanProgress,
  useCurrentScan,
  useScanHistory,
  useScanError,
  useScanStore,
  
  // Watched Folders Store
  useWatchedFolders,
  useWatchedFoldersLoading,
  useWatchedFoldersError,
  useWatchedFoldersStore,
} from '../stores';

// ==================== Metrics Store 示例 ====================

/**
 * 示例 1: 显示当前系统指标
 */
export function CurrentMetricsDisplay() {
  const metrics = useCurrentMetrics();
  const loading = useMetricsLoading();
  const error = useMetricsError();
  
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  if (!metrics) return <div>暂无数据</div>;
  
  return (
    <div>
      <h3>当前系统指标</h3>
      <p>CPU 使用率: {metrics.cpu_usage.toFixed(2)}%</p>
      <p>内存使用率: {metrics.memory_usage.toFixed(2)}%</p>
      <p>磁盘使用率: {(metrics.disk_usage ?? 0).toFixed(2)}%</p>
    </div>
  );
}

/**
 * 示例 2: 显示统计信息
 */
export function MetricsStatsDisplay() {
  const stats = useMetricsStats();
  const historicalMetrics = useHistoricalMetrics();
  
  if (!stats) return <div>暂无统计数据</div>;
  
  return (
    <div>
      <h3>统计信息</h3>
      <p>历史记录数量: {historicalMetrics.length}</p>
      <p>平均 CPU: {stats.avgCpu.toFixed(2)}%</p>
      <p>峰值 CPU: {stats.peakCpu.toFixed(2)}%</p>
      <p>平均内存: {stats.avgMemory.toFixed(2)}%</p>
      <p>峰值内存: {stats.peakMemory.toFixed(2)}%</p>
    </div>
  );
}

/**
 * 示例 3: 手动更新指标（Actions 使用）
 */
export function ManualMetricsUpdate() {
  const setCurrentMetrics = useMetricsStore(state => state.setCurrentMetrics);
  const addHistoricalMetric = useMetricsStore(state => state.addHistoricalMetric);
  const calculateStats = useMetricsStore(state => state.calculateStats);
  
  const handleUpdate = () => {
    const newMetric = {
      timestamp: Date.now(),
      cpu_usage: Math.random() * 100,
      memory_usage: Math.random() * 100,
      disk_usage: Math.random() * 100,
    };
    
    setCurrentMetrics(newMetric);
    addHistoricalMetric(newMetric);
    calculateStats();
  };
  
  return (
    <button onClick={handleUpdate}>
      生成随机指标
    </button>
  );
}

// ==================== Alert Store 示例 ====================

/**
 * 示例 4: 警报徽章
 */
export function AlertBadge() {
  const unreadCount = useUnreadCount();
  const unresolved = useUnresolvedAlerts();
  
  if (unreadCount === 0 && unresolved.length === 0) {
    return null;
  }
  
  return (
    <div className="alert-badge">
      {unreadCount > 0 && <span className="unread">{unreadCount}</span>}
      {unresolved.length > 0 && (
        <span className="unresolved">{unresolved.length}</span>
      )}
    </div>
  );
}

/**
 * 示例 5: 警报列表
 */
export function AlertList() {
  const alerts = useAlerts();
  const acknowledgeAlert = useAlertStore(state => state.acknowledgeAlert);
  const resolveAlert = useAlertStore(state => state.resolveAlert);
  const removeAlert = useAlertStore(state => state.removeAlert);
  
  if (alerts.length === 0) {
    return <div>暂无警报</div>;
  }
  
  return (
    <ul>
      {alerts.map(alert => (
        <li key={alert.id} className={`alert alert-${alert.level}`}>
          <div>
            <strong>{alert.title}</strong>
            <p>{alert.message}</p>
            <small>{new Date(alert.timestamp).toLocaleString()}</small>
          </div>
          <div className="alert-actions">
            {!alert.acknowledged && (
              <button onClick={() => acknowledgeAlert(alert.id)}>
                确认
              </button>
            )}
            {!alert.resolved && (
              <button onClick={() => resolveAlert(alert.id)}>
                解决
              </button>
            )}
            <button onClick={() => removeAlert(alert.id)}>
              删除
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

/**
 * 示例 6: 添加测试警报
 */
export function AddTestAlert() {
  const addAlert = useAlertStore(state => state.addAlert);
  
  const handleClick = () => {
    addAlert({
      level: AlertLevel.Warning,
      type: AlertType.System,
      title: '测试警报',
      message: '这是一个测试警报消息',
    });
  };
  
  return <button onClick={handleClick}>添加测试警报</button>;
}

// ==================== Settings Store 示例 ====================

/**
 * 示例 7: 主题切换器
 */
export function ThemeSwitcher() {
  const uiSettings = useUISettings();
  const updateUISettings = useSettingsStore(state => state.updateUISettings);
  
  const toggleTheme = () => {
    const newTheme = 
      uiSettings.theme === ThemeMode.Light ? ThemeMode.Dark : ThemeMode.System;
    updateUISettings({ theme: newTheme });
  };
  
  return (
    <div>
      <p>当前主题: {uiSettings.theme}</p>
      <button onClick={toggleTheme}>切换主题</button>
    </div>
  );
}

/**
 * 示例 8: 设置面板
 */
export function SettingsPanel() {
  const settings = useAppSettings();
  const scanSettings = useScanSettings();
  const alertSettings = useAlertSettings();
  
  const updateScanSettings = useSettingsStore(state => state.updateScanSettings);
  const updateAlertSettings = useSettingsStore(state => state.updateAlertSettings);
  const resetToDefaults = useSettingsStore(state => state.resetToDefaults);
  
  return (
    <div className="settings-panel">
      <h2>应用设置</h2>
      
      <section>
        <h3>扫描设置</h3>
        <label>
          最大深度:
          <input
            type="number"
            value={scanSettings.maxDepth}
            onChange={(e) => updateScanSettings({ maxDepth: Number(e.target.value) })}
          />
        </label>
        <label>
          <input
            type="checkbox"
            checked={scanSettings.includeHidden}
            onChange={(e) => updateScanSettings({ includeHidden: e.target.checked })}
          />
          包含隐藏文件
        </label>
      </section>
      
      <section>
        <h3>警报设置</h3>
        <label>
          <input
            type="checkbox"
            checked={alertSettings.enabled}
            onChange={(e) => updateAlertSettings({ enabled: e.target.checked })}
          />
          启用警报
        </label>
        <label>
          CPU 阈值:
          <input
            type="number"
            value={alertSettings.cpuThreshold}
            onChange={(e) => updateAlertSettings({ cpuThreshold: Number(e.target.value) })}
          />
        </label>
      </section>
      
      <button onClick={resetToDefaults}>重置为默认值</button>
    </div>
  );
}

// ==================== Scan Store 示例 ====================

/**
 * 示例 9: 扫描进度显示
 */
export function ScanProgressDisplay() {
  const isScanning = useIsScanning();
  const progress = useScanProgress();
  const currentScan = useCurrentScan();
  const error = useScanError();
  
  if (error) {
    return <div className="error">扫描错误: {error.message}</div>;
  }
  
  if (!isScanning && !currentScan) {
    return <div>未开始扫描</div>;
  }
  
  return (
    <div>
      {isScanning && progress && (
        <div>
          <progress value={progress.percentage} max="100" />
          <p>
            {progress.current} / {progress.total}
            {progress.currentFile && ` - ${progress.currentFile}`}
          </p>
        </div>
      )}
      
      {currentScan && !isScanning && (
        <div>
          <h3>扫描完成</h3>
          <p>路径: {currentScan.path}</p>
          <p>大小: {(currentScan.size / 1024 / 1024).toFixed(2)} MB</p>
          <p>文件数: {currentScan.fileCount}</p>
          <p>文件夹数: {currentScan.folderCount}</p>
        </div>
      )}
    </div>
  );
}

/**
 * 示例 10: 扫描历史
 */
export function ScanHistoryList() {
  const history = useScanHistory();
  const clearHistory = useScanStore(state => state.clearHistory);
  const removeHistoryItem = useScanStore(state => state.removeHistoryItem);
  
  if (history.length === 0) {
    return <div>暂无扫描历史</div>;
  }
  
  return (
    <div>
      <button onClick={clearHistory}>清空历史</button>
      <ul>
        {history.map(item => (
          <li key={item.id}>
            <div>
              <strong>{item.path}</strong>
              <p>{new Date(item.timestamp).toLocaleString()}</p>
              <p>耗时: {item.duration}ms</p>
              <p>大小: {(item.result.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button onClick={() => removeHistoryItem(item.id)}>删除</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * 示例 11: 启动扫描
 */
export function StartScanButton() {
  const selectedPath = useSelectedPath();
  const startScan = useScanStore(state => state.startScan);
  const completeScan = useScanStore(state => state.completeScan);
  const setSelectedPath = useScanStore(state => state.setSelectedPath);
  
  const handleStartScan = async () => {
    if (!selectedPath) {
      alert('请先选择扫描路径');
      return;
    }
    
    startScan();
    
    try {
      // 模拟扫描过程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const result = {
        path: selectedPath,
        size: Math.random() * 1000000000,
        fileCount: Math.floor(Math.random() * 1000),
        folderCount: Math.floor(Math.random() * 100),
        timestamp: Date.now(),
      };
      
      completeScan(result, 2000);
    } catch (error) {
      console.error('扫描失败:', error);
    }
  };
  
  return (
    <div>
      <input
        type="text"
        placeholder="输入扫描路径"
        value={selectedPath || ''}
        onChange={(e) => setSelectedPath(e.target.value)}
      />
      <button onClick={handleStartScan}>开始扫描</button>
    </div>
  );
}

// ==================== Watched Folders Store 示例 ====================

/**
 * 示例 12: 监控文件夹列表
 */
export function WatchedFoldersList() {
  const folders = useWatchedFolders();
  const loading = useWatchedFoldersLoading();
  const error = useWatchedFoldersError();
  
  const fetchFolders = useWatchedFoldersStore(state => state.fetchFolders);
  const toggleActive = useWatchedFoldersStore(state => state.toggleActive);
  const removeFolder = useWatchedFoldersStore(state => state.removeFolder);
  
  React.useEffect(() => {
    fetchFolders();
  }, [fetchFolders]);
  
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  if (folders.length === 0) return <div>暂无监控文件夹</div>;
  
  return (
    <ul>
      {folders.map(folder => (
        <li key={folder.id}>
          <div>
            <strong>{folder.alias || folder.path}</strong>
            <p>{folder.path}</p>
            <p>状态: {folder.is_active ? '✅ 活跃' : '❌ 禁用'}</p>
            <p>事件数: {folder.total_events_count}</p>
          </div>
          <div>
            <button onClick={() => toggleActive(folder.id)}>
              {folder.is_active ? '禁用' : '启用'}
            </button>
            <button onClick={() => removeFolder(folder.id)}>删除</button>
          </div>
        </li>
      ))}
    </ul>
  );
}

/**
 * 示例 13: 添加监控文件夹
 */
export function AddWatchedFolder() {
  const [path, setPath] = React.useState('');
  const [alias, setAlias] = React.useState('');
  const addFolder = useWatchedFoldersStore(state => state.addFolder);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!path) return;
    
    try {
      await addFolder(path, alias || undefined);
      setPath('');
      setAlias('');
    } catch (error) {
      console.error('添加失败:', error);
      alert('添加失败: ' + error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="文件夹路径"
        value={path}
        onChange={(e) => setPath(e.target.value)}
      />
      <input
        type="text"
        placeholder="别名（可选）"
        value={alias}
        onChange={(e) => setAlias(e.target.value)}
      />
      <button type="submit">添加</button>
    </form>
  );
}

// ==================== 组合使用示例 ====================

/**
 * 示例 14: 完整的监控仪表板
 */
export function MonitorDashboard() {
  const metrics = useCurrentMetrics();
  const stats = useMetricsStats();
  const unreadAlerts = useUnreadCount();
  const uiSettings = useUISettings();
  
  return (
    <div className={`dashboard theme-${uiSettings.theme}`}>
      <header>
        <h1>系统监控仪表板</h1>
        {unreadAlerts > 0 && (
          <span className="badge">{unreadAlerts} 个未读警报</span>
        )}
      </header>
      
      <main>
        <section>
          <h2>实时指标</h2>
          <CurrentMetricsDisplay />
        </section>
        
        <section>
          <h2>统计信息</h2>
          <MetricsStatsDisplay />
        </section>
        
        <section>
          <h2>警报</h2>
          <AlertBadge />
          <AlertList />
        </section>
        
        <section>
          <h2>快速操作</h2>
          <ManualMetricsUpdate />
          <AddTestAlert />
        </section>
      </main>
    </div>
  );
}
