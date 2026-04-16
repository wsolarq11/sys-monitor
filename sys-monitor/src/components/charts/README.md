# 图表组件库

## 概述

本目录包含 sys-monitor 项目的所有图表组件，基于 Recharts 构建，经过性能优化。

## 组件列表

### 1. RealTimeChart - 实时趋势图

用于显示 CPU、内存、磁盘等系统指标的实时变化趋势。

**特性：**
- 使用环形缓冲区管理数据（最多 100 个点）
- 自动滚动显示最新数据
- 禁用动画以提升性能
- 自定义提示框和样式

**使用示例：**

```tsx
import { RealTimeChart } from '../components/charts';
import { RingBuffer, type DataPoint } from '../utils/chartUtils';

const buffer = new RingBuffer<DataPoint>(100);

<RealTimeChart
  title="CPU 使用率"
  metric="cpu"
  buffer={buffer}
  color="#3b82f6"
  yAxisLabel="CPU %"
/>
```

### 2. SystemMonitorPanel - 系统监控面板

集成多个实时监控图表的面板组件。

**特性：**
- 同时显示 CPU、内存、磁盘监控
- 支持暂停/继续功能
- 自动每秒更新

**使用示例：**

```tsx
import { SystemMonitorPanel } from '../components/charts';

<SystemMonitorPanel />
```

### 3. FileTypePieChart - 文件类型分布饼图

展示不同文件类型的数量和大小分布。

**特性：**
- 自动合并小类别（超过 10 种时）
- 支持按数量或大小排序
- 自定义颜色方案
- 响应式设计

**使用示例：**

```tsx
import { FileTypePieChart, type FileTypeData } from '../components/charts';

const data: FileTypeData[] = [
  { extension: '.jpg', count: 150, totalSize: 52428800 },
  { extension: '.png', count: 80, totalSize: 31457280 },
  // ...
];

<FileTypePieChart
  data={data}
  title="文件类型分布"
  sortBy="size"
/>
```

### 4. FolderSizeBarChart - 文件夹大小柱状图

展示各文件夹的大小对比。

**特性：**
- 自动取最大的 N 个文件夹
- 颜色渐变表示大小（蓝→橙→红）
- 支持水平和垂直布局
- 显示完整路径提示

**使用示例：**

```tsx
import { FolderSizeBarChart, type FolderSizeData } from '../components/charts';

const data: FolderSizeData[] = [
  { name: 'Documents', path: '/home/user/Documents', size: 1073741824, fileCount: 500 },
  { name: 'Downloads', path: '/home/user/Downloads', size: 2147483648, fileCount: 1200 },
  // ...
];

<FolderSizeBarChart
  data={data}
  title="文件夹大小对比"
  maxItems={15}
  horizontal={false}
/>
```

## 工具函数

所有图表都使用 `src/utils/chartUtils.ts` 中的工具函数：

### 数据采样
- `simpleSampling(data, maxPoints)` - 简单均匀采样
- `lttbSampling(data, maxPoints, valueKey)` - LTTB 算法采样（保持趋势）

### 环形缓冲区
```typescript
import { RingBuffer } from '../utils/chartUtils';

const buffer = new RingBuffer<DataPoint>(100);
buffer.push(dataPoint);
const data = buffer.toArray();
```

### 格式化函数
- `formatBytes(bytes, decimals)` - 格式化字节数
- `formatPercent(value, decimals)` - 格式化百分比
- `formatTime(timestamp)` - 格式化时间

### 统计分析
- `average(arr)` - 计算平均值
- `standardDeviation(arr)` - 计算标准差
- `detectOutliers(arr, threshold)` - 检测异常值

## 性能优化

所有图表组件都应用了以下优化：

1. **禁用动画** - `isAnimationActive={false}`
2. **Memoization** - 使用 `useMemo` 和 `React.memo`
3. **数据采样** - 大数据集自动降采样
4. **按需导入** - Tree shaking 友好
5. **环形缓冲区** - 固定内存占用

## 最佳实践

### 1. 实时更新场景

```tsx
// 在组件外部创建缓冲区，避免重复创建
const buffer = new RingBuffer<DataPoint>(100);

function MyComponent() {
  useEffect(() => {
    const interval = setInterval(() => {
      buffer.push(newDataPoint);
      setData(buffer.toArray());
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return <RealTimeChart buffer={buffer} metric="cpu" />;
}
```

### 2. 大数据集处理

```tsx
import { simpleSampling } from '../utils/chartUtils';

const sampledData = useMemo(() => {
  if (data.length > 1000) {
    return simpleSampling(data, 100);
  }
  return data;
}, [data]);
```

### 3. 自定义颜色方案

```tsx
import { COLOR_SCHEMES } from '../utils/chartUtils';

// 使用预定义方案
const colors = COLOR_SCHEMES.blue;
const colors = COLOR_SCHEMES.mixed;

// 或自定义渐变色
import { generateGradient } from '../utils/chartUtils';
const gradient = generateGradient('#3b82f6', '#ef4444', 10);
```

## 未来计划

- [ ] HistoricalComparison - 历史数据对比组件
- [ ] 支持更多图表类型（面积图、散点图等）
- [ ] 导出图表为图片功能
- [ ] 可拖拽 Dashboard 布局

## 参考资料

- [Recharts 官方文档](https://recharts.org/)
- [Recharts 性能优化指南](https://recharts.org/en-US/guide/performance)
- [LTTB 降采样算法论文](https://skemman.is/bitstream/1946/15343/3/SS_MSthesis.pdf)
