# Zustand Store 迁移检查清单

## 📋 迁移前准备

### 1. 环境检查
- [ ] 确认 Zustand 版本 >= 5.0.0
- [ ] 安装 Redux DevTools 浏览器扩展
- [ ] 备份当前代码（创建 Git 分支）

### 2. 了解变更
- [ ] 阅读 [优化指南](./zustand-optimization-guide.md)
- [ ] 查看 [快速参考](./zustand-quick-reference.md)
- [ ] 浏览 [使用示例](../src/examples/zustand-usage-examples.tsx)

---

## 🔄 逐步迁移

### Phase 1: 更新导入（低风险）

#### Step 1.1: 更新 Store 导入路径
**影响范围**: 所有使用 Store 的文件

```typescript
// 之前
import { useMetricsStore } from '../stores/metricsStore';

// 之后
import { useMetricsStore, useCurrentMetrics } from '@/stores';
// 或
import { useMetricsStore, useCurrentMetrics } from '../stores';
```

**检查清单**:
- [ ] `src/contexts/MonitorContext.tsx`
- [ ] `src/hooks/useFolderWatcher.ts`
- [ ] `src/components/**/*.tsx` (所有组件)
- [ ] 其他使用 Store 的文件

---

### Phase 2: 替换解构用法（中风险）

#### Step 2.1: Metrics Store 迁移

**查找模式**: 
```typescript
const { currentMetrics, loading, error } = useMetricsStore();
```

**替换为**:
```typescript
const currentMetrics = useCurrentMetrics();
const loading = useMetricsLoading();
const error = useMetricsError();
```

**需要迁移的文件**:
- [ ] 搜索 `useMetricsStore()` 的使用
- [ ] 逐个文件替换
- [ ] 测试每个文件的功能

**示例文件**:
```typescript
// src/components/MetricsDisplay.tsx
function MetricsDisplay() {
  // ❌ 之前
  const { currentMetrics, stats } = useMetricsStore();
  
  // ✅ 之后
  const currentMetrics = useCurrentMetrics();
  const stats = useMetricsStats();
  
  return <div>{/* ... */}</div>;
}
```

---

#### Step 2.2: Alert Store 迁移

**查找模式**:
```typescript
const { alerts, unreadCount } = useAlertStore();
```

**替换为**:
```typescript
const alerts = useAlerts();
const unreadCount = useUnreadCount();
```

**需要迁移的文件**:
- [ ] `src/hooks/useFolderWatcher.ts` (已使用正确方式)
- [ ] 搜索 `useAlertStore()` 的其他使用
- [ ] 警报相关组件

---

#### Step 2.3: Settings Store 迁移

**查找模式**:
```typescript
const { settings } = useSettingsStore();
```

**替换为**:
```typescript
const settings = useAppSettings();
// 或更细粒度
const uiSettings = useUISettings();
const scanSettings = useScanSettings();
```

**需要迁移的文件**:
- [ ] 设置相关组件
- [ ] 主题切换组件
- [ ] 配置面板

---

#### Step 2.4: Scan Store 迁移

**查找模式**:
```typescript
const { isScanning, progress, error } = useScanStore();
```

**替换为**:
```typescript
const isScanning = useIsScanning();
const progress = useScanProgress();
const error = useScanError();
```

**需要迁移的文件**:
- [ ] 扫描相关组件
- [ ] 进度显示组件
- [ ] 历史记录组件

---

#### Step 2.5: Watched Folders Store 迁移

**查找模式**:
```typescript
const { folders, loading } = useWatchedFoldersStore();
```

**替换为**:
```typescript
const folders = useWatchedFolders();
const loading = useWatchedFoldersLoading();
```

**需要迁移的文件**:
- [ ] `src/components/FolderAnalysis/WatchedFoldersList.tsx`
- [ ] 文件夹监控相关组件

---

### Phase 3: Actions 保持不变（无变更）

Actions 的使用方式**不需要改变**：

```typescript
// ✅ 仍然有效
const setCurrentMetrics = useMetricsStore(state => state.setCurrentMetrics);
const addAlert = useAlertStore(state => state.addAlert);
const updateUISettings = useSettingsStore(state => state.updateUISettings);
```

**检查清单**:
- [ ] 确认所有 actions 仍然正常工作
- [ ] 测试异步 actions
- [ ] 验证乐观更新

---

### Phase 4: 验证持久化（新功能）

#### Step 4.1: 测试 Metrics Store 持久化
- [ ] 刷新页面后检查历史指标是否保留
- [ ] 验证只保留了最近 10 条记录
- [ ] 检查 localStorage 中的 `metrics-storage` 键

#### Step 4.2: 测试 Settings Store 持久化
- [ ] 修改设置
- [ ] 刷新页面
- [ ] 验证设置是否保持
- [ ] 检查 localStorage 中的 `app-settings` 键

#### Step 4.3: 测试 Scan Store 持久化
- [ ] 执行几次扫描
- [ ] 刷新页面
- [ ] 验证扫描历史是否保留
- [ ] 检查 localStorage 中的 `scan-storage` 键

---

### Phase 5: 调试工具验证

#### Step 5.1: Redux DevTools
- [ ] 打开浏览器 DevTools
- [ ] 切换到 Redux 标签
- [ ] 触发一些 actions
- [ ] 验证状态变化是否正确记录
- [ ] 检查时间旅行调试功能

#### Step 5.2: Store 名称验证
在 Redux DevTools 中应该看到：
- [ ] `MetricsStore`
- [ ] `AlertStore`
- [ ] `SettingsStore`
- [ ] `ScanStore`
- [ ] `WatchedFoldersStore`

---

## 🧪 测试清单

### 单元测试
- [ ] 运行 `pnpm test`
- [ ] 确保所有测试通过
- [ ] metricsStore.test.ts 应该通过
- [ ] scanStore.test.ts 应该通过

### 集成测试
- [ ] 启动开发服务器 `pnpm dev`
- [ ] 访问各个页面
- [ ] 测试所有交互功能

### 性能测试
- [ ] 打开 Chrome DevTools Performance 标签
- [ ] 记录操作过程
- [ ] 检查重渲染次数
- [ ] 对比优化前后的性能

### 手动测试场景

#### Metrics Store
- [ ] 实时指标更新
- [ ] 历史数据累积
- [ ] 统计数据计算
- [ ] 页面刷新后数据恢复

#### Alert Store
- [ ] 添加新警报
- [ ] 确认警报
- [ ] 解决警报
- [ ] 删除警报
- [ ] 未读计数更新

#### Settings Store
- [ ] 修改扫描设置
- [ ] 修改警报设置
- [ ] 修改界面设置
- [ ] 修改数据库设置
- [ ] 重置为默认值
- [ ] 页面刷新后设置保持

#### Scan Store
- [ ] 开始扫描
- [ ] 取消扫描
- [ ] 完成扫描
- [ ] 查看扫描历史
- [ ] 删除历史记录

#### Watched Folders Store
- [ ] 加载文件夹列表
- [ ] 添加新文件夹
- [ ] 删除文件夹
- [ ] 启用/禁用文件夹
- [ ] 错误处理

---

## 🐛 常见问题排查

### 问题 1: 组件不更新
**症状**: 状态改变了但组件没有重新渲染

**可能原因**:
- 使用了错误的订阅方式
- 忘记了 `useShallow`

**解决方案**:
```typescript
// ❌ 错误
const metrics = useMetricsStore((state) => state.currentMetrics);

// ✅ 正确
const metrics = useCurrentMetrics();
// 或
const metrics = useMetricsStore(useShallow((state) => state.currentMetrics));
```

---

### 问题 2: TypeScript 类型错误
**症状**: `useShallow` 相关的类型错误

**解决方案**:
- 确认使用的是 `useShallow` 而不是 `shallow`
- 检查导入路径: `import { useShallow } from 'zustand/react/shallow'`

---

### 问题 3: 持久化不工作
**症状**: 刷新页面后数据丢失

**检查清单**:
- [ ] 确认 Store 配置了 `persist` 中间件
- [ ] 检查 `name` 属性是否唯一
- [ ] 检查 `partialize` 函数是否正确
- [ ] 打开 Application 标签查看 localStorage

---

### 问题 4: Redux DevTools 不显示
**症状**: DevTools 中没有显示 Store

**解决方案**:
- [ ] 确认安装了 Redux DevTools 扩展
- [ ] 确认 Store 配置了 `devtools` 中间件
- [ ] 检查中间件顺序: `devtools(persist(...))`
- [ ] 刷新页面重试

---

## 📊 迁移进度跟踪

### 文件迁移统计

| 文件路径 | 状态 | 备注 |
|---------|------|------|
| `src/contexts/MonitorContext.tsx` | ⬜ 待迁移 | 使用 useMetricsStore |
| `src/hooks/useFolderWatcher.ts` | ⬜ 待迁移 | 使用 useAlertStore |
| `src/components/**/*.tsx` | ⬜ 待迁移 | 所有组件 |
| ... | ... | ... |

### 总体进度

```
Phase 1: 更新导入        [░░░░░░░░░░] 0%
Phase 2: 替换解构用法    [░░░░░░░░░░] 0%
Phase 3: Actions 验证   [░░░░░░░░░░] 0%
Phase 4: 持久化验证     [░░░░░░░░░░] 0%
Phase 5: 调试工具验证   [░░░░░░░░░░] 0%
测试                   [░░░░░░░░░░] 0%
```

---

## ✅ 迁移完成检查

- [ ] 所有文件已迁移
- [ ] 所有测试通过
- [ ] Redux DevTools 正常工作
- [ ] 持久化功能正常
- [ ] 性能有所提升
- [ ] 没有 TypeScript 错误
- [ ] 代码审查通过
- [ ] 文档已更新

---

## 🎯 回滚计划

如果迁移过程中遇到严重问题：

1. **立即停止迁移**
2. **切换到备份分支**
   ```bash
   git checkout main
   ```
3. **分析问题原因**
4. **修复后重新尝试**

---

## 📞 获取帮助

- [完整优化指南](./zustand-optimization-guide.md)
- [快速参考](./zustand-quick-reference.md)
- [使用示例](../src/examples/zustand-usage-examples.tsx)
- [Zustand 官方文档](https://github.com/pmndrs/zustand)

---

**最后更新**: 2026-04-16
**维护者**: 状态管理架构优化团队
