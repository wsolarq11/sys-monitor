# Zustand Store 快速参考

## 📦 Store 概览

| Store | 持久化 | DevTools | 自定义 Hooks |
|-------|--------|----------|--------------|
| MetricsStore | ✅ (10条) | ✅ | 5 |
| AlertStore | ❌ | ✅ | 3 |
| SettingsStore | ✅ (全部) | ✅ | 5 |
| ScanStore | ✅ (10条) | ✅ | 6 |
| WatchedFoldersStore | ❌ | ✅ | 3 |

## 🎯 常用 Hooks 速查

### Metrics Store
```typescript
import { 
  useCurrentMetrics,      // SystemMetric | null
  useHistoricalMetrics,   // SystemMetric[]
  useMetricsLoading,      // boolean
  useMetricsError,        // string | null
  useMetricsStats,        // MetricsStats | null
} from '@/stores';
```

### Alert Store
```typescript
import { 
  useAlerts,              // Alert[]
  useUnreadCount,         // number
  useUnresolvedAlerts,    // Alert[]
} from '@/stores';
```

### Settings Store
```typescript
import { 
  useAppSettings,         // AppSettings
  useScanSettings,        // ScanSettings
  useAlertSettings,       // AlertSettings
  useUISettings,          // UISettings
  useDatabaseSettings,    // DatabaseSettings
} from '@/stores';
```

### Scan Store
```typescript
import { 
  useSelectedPath,        // string | null
  useIsScanning,          // boolean
  useScanProgress,        // ScanProgress | null
  useCurrentScan,         // ScanResult | null
  useScanHistory,         // ScanHistoryItem[]
  useScanError,           // ScanError | null
} from '@/stores';
```

### Watched Folders Store
```typescript
import { 
  useWatchedFolders,              // WatchedFolder[]
  useWatchedFoldersLoading,       // boolean
  useWatchedFoldersError,         // string | null
} from '@/stores';
```

## 🔧 Actions 使用示例

```typescript
// 获取 actions
const setCurrentMetrics = useMetricsStore(state => state.setCurrentMetrics);
const addAlert = useAlertStore(state => state.addAlert);
const updateUISettings = useSettingsStore(state => state.updateUISettings);
const startScan = useScanStore(state => state.startScan);
const fetchFolders = useWatchedFoldersStore(state => state.fetchFolders);

// 调用 actions
setCurrentMetrics({ timestamp: Date.now(), cpu_usage: 50, memory_usage: 60 });

addAlert({
  level: AlertLevel.Info,
  type: AlertType.System,
  title: '系统更新',
  message: '配置已更新',
});

updateUISettings({ theme: ThemeMode.Dark });
startScan();
await fetchFolders();
```

## ⚡ 性能优化对比

### ❌ 不推荐
```typescript
function Component() {
  const { currentMetrics, loading, error } = useMetricsStore();
  return <div>{currentMetrics?.cpu_usage}</div>;
}
```

### ✅ 推荐
```typescript
function Component() {
  const currentMetrics = useCurrentMetrics();
  const loading = useMetricsLoading();
  return <div>{currentMetrics?.cpu_usage}</div>;
}
```

## 🐛 调试技巧

### Redux DevTools
1. 安装扩展
2. 打开 DevTools → Redux 标签
3. 查看 State 和 Actions

### 手动检查状态
```typescript
// 在控制台查看当前状态
console.log(useMetricsStore.getState());

// 订阅状态变化
const unsubscribe = useMetricsStore.subscribe((state) => {
  console.log('State changed:', state);
});

// 取消订阅
unsubscribe();
```

## 📝 迁移清单

- [ ] 替换解构用法为自定义 Hooks
- [ ] 移除不必要的 `useMemo`
- [ ] 测试 Redux DevTools
- [ ] 验证持久化功能
- [ ] 检查性能改进

## 🔗 相关链接

- [完整优化指南](./zustand-optimization-guide.md)
- [Zustand 文档](https://github.com/pmndrs/zustand)
- [Redux DevTools](https://github.com/reduxjs/redux-devtools)
