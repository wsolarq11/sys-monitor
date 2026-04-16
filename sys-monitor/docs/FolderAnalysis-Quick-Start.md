# FolderAnalysis 模块 - 快速入门指南

## 🚀 5分钟了解模块

### 这是什么？

FolderAnalysis 是一个**文件夹大小分析工具**，提供两大核心功能：

1. **单次扫描** - 手动选择文件夹，立即获取大小、文件数等信息
2. **持续监控** - 添加文件夹到监控列表，实时跟踪变化

---

## 📦 模块组成

```
FolderAnalysis/
├── FolderAnalysisContainer.tsx    # 主容器（状态管理 + 业务逻辑）
├── FolderAnalysisView.tsx         # 扫描界面（纯 UI）
└── WatchedFoldersList.tsx         # 监控列表（独立组件）
```

---

## 🎯 核心概念

### 1. Container-Presenter 模式

```typescript
// Container: 管理状态和逻辑
FolderAnalysisContainer
  ├─ useState (本地状态)
  ├─ useEffect (副作用)
  └─ 调用 Tauri 命令

// Presenter: 只负责渲染
FolderAnalysisView
  └─ 接收 props，返回 JSX
```

**为什么这样设计？**
- ✅ 易于测试（Presenter 是纯函数）
- ✅ 关注点分离
- ✅ 可复用性强

---

### 2. 状态管理策略

#### 局部状态 (useState)
用于**临时性、UI 相关**的数据：
```typescript
const [selectedPath, setSelectedPath] = useState('');
const [isScanning, setIsScanning] = useState(false);
const [scanResult, setScanResult] = useState(null);
```

#### 全局状态 (Zustand)
用于**跨组件共享、需要持久化**的数据：
```typescript
const { folders, addFolder, removeFolder } = useWatchedFoldersStore();
```

**选择原则**:
- 只在当前组件使用 → `useState`
- 多个组件需要访问 → `Zustand Store`

---

## 🔧 常用操作

### 执行一次扫描

```typescript
// 1. 用户输入路径
<input value={selectedPath} onChange={e => setSelectedPath(e.target.value)} />

// 2. 点击扫描按钮
<button onClick={handleScan}>扫描文件夹</button>

// 3. 内部流程
handleScan() {
  ├─ 验证路径 ✓
  ├─ 调用 scan_folder 命令
  ├─ 显示结果
  └─ 刷新历史记录
}
```

---

### 添加监控文件夹

```typescript
// WatchedFoldersList 组件内部
const handleAddFolder = async () => {
  const path = await invoke('select_folder');  // 打开选择对话框
  await addFolder(path);                        // 添加到数据库
  toast.success('已开始监控');                   // 显示通知
};
```

---

### 切换监控状态

```typescript
// 乐观更新：先改 UI，再调后端
const handleToggleActive = async (folder) => {
  await toggleActive(folder.id);  // Store 内部会立即更新 UI
  toast.success('状态已切换');
};
```

---

## 📊 数据流示例

### 场景：用户点击"扫描文件夹"

```
用户操作
   ↓
Container.handleScan()
   ↓
验证路径 (validation.ts)
   ↓
调用 Tauri: scan_folder(path, db_path)
   ↓
Rust 后端扫描文件夹
   ↓
返回 ScanResultData
   ↓
更新 scanResult 状态
   ↓
调用 Tauri: get_folder_scans(path, limit, db_path)
   ↓
返回历史记录数组
   ↓
更新 scans 状态
   ↓
Presenter 重新渲染，显示结果
```

---

## 🛠️ 开发调试技巧

### 1. 查看详细日志

Container 中有大量 `console.log`：
```typescript
console.log('=== 开始扫描流程 ===');
console.log('扫描路径:', selectedPath);
console.log('数据库路径:', dbPath);
```

在浏览器控制台查看完整流程。

---

### 2. 检查 Store 状态

安装 Redux DevTools（Zustand 兼容），或使用：
```typescript
const state = useWatchedFoldersStore.getState();
console.log(state);
```

---

### 3. 模拟错误

修改 Tauri 命令返回值，测试错误处理：
```typescript
// 临时修改，测试错误 UI
throw new Error('模拟网络错误');
```

---

## ⚠️ 常见问题

### Q1: 为什么扫描后没有显示历史纪录？

**检查清单**:
1. 确认 `dbPath` 已正确获取
2. 查看控制台是否有错误日志
3. 验证后端 `get_folder_scans` 命令是否返回数据

**调试代码**:
```typescript
console.log('扫描历史加载完成:', folderScans.scans?.length || 0, '条记录');
```

---

### Q2: 切换激活状态后，刷新页面又变回去了？

**原因**: 后端更新失败，但 UI 已乐观更新。

**当前问题**: Store 的 `toggleActive` 缺少回滚机制。

**临时解决**: 手动刷新页面重新加载数据。

**长期修复**: 实现错误回滚（见技术债务文档）。

---

### Q3: 如何添加新的扫描指标？

**步骤**:

1. 修改类型定义 (`FolderAnalysisView.tsx`):
```typescript
interface ScanResultData {
  total_size: number;
  file_count: number;
  folder_count: number;
  scan_duration_ms: number;
  new_metric: number;  // 新增字段
}
```

2. 更新 UI 展示 (`FolderAnalysisView.tsx`):
```tsx
<p><span className="font-medium">新指标:</span> {scanResult.new_metric}</p>
```

3. 修改 Rust 后端返回对应字段。

---

## 📚 深入学习路径

### 第 1 天：理解架构
- [ ] 阅读 [架构设计文档](./FolderAnalysis-Module-Architecture.md)
- [ ] 查看组件树结构
- [ ] 理解 Container-Presenter 模式

### 第 2 天：掌握数据流
- [ ] 跟踪一次完整的扫描流程
- [ ] 理解 Zustand Store 的工作方式
- [ ] 绘制数据流图

### 第 3 天：实践修改
- [ ] 添加一个新的状态字段
- [ ] 修改 UI 样式
- [ ] 添加错误处理逻辑

### 第 4 天：优化性能
- [ ] 使用 React.memo 优化渲染
- [ ] 添加请求缓存
- [ ] 实现加载骨架屏

---

## 🎓 关键代码片段

### 获取 Store 数据

```typescript
import { useWatchedFoldersStore } from '../../stores/watchedFoldersStore';

function MyComponent() {
  const { folders, loading } = useWatchedFoldersStore();
  
  return <div>{folders.length} 个文件夹</div>;
}
```

---

### 调用 Tauri 命令

```typescript
import { invoke } from '@tauri-apps/api/core';

async function fetchData() {
  try {
    const result = await invoke<MyType>('command_name', { param: value });
    console.log(result);
  } catch (error) {
    console.error('命令执行失败:', error);
  }
}
```

---

### 表单验证

```typescript
import { getPathValidationError } from '../../utils/validation';

const error = getPathValidationError(selectedPath);
if (error) {
  setError(error);
  return;  // 阻止后续操作
}
```

---

### 格式化数据

```typescript
import { formatSize } from '../../utils/format';
import { formatTimestamp } from '../../utils/time';

<p>大小: {formatSize(1073741824)}</p>  {/* "1.00 GB" */}
<p>时间: {formatTimestamp(1713254400)}</p>  {/* "2024/4/16 12:00:00" */}
```

---

## 🔗 相关资源

### 官方文档
- [React Hooks](https://react.dev/reference/react)
- [Zustand](https://zustand-demo.pmnd.rs/)
- [Tauri v2](https://v2.tauri.app/)
- [TailwindCSS](https://tailwindcss.com/docs)

### 项目文档
- [架构设计](./FolderAnalysis-Module-Architecture.md)
- [API 参考](./FolderAnalysis-API-Reference.md)
- [架构图解](./FolderAnalysis-Architecture-Diagrams.md)

---

## 💡 最佳实践

### ✅ 推荐做法

1. **保持 Presenter 纯净**
```typescript
// ✓ 好：纯函数组件
function View({ data, onClick }) {
  return <button onClick={onClick}>{data}</button>;
}

// ✗ 坏：包含业务逻辑
function View() {
  const data = await fetchFromAPI();  // 不应该在这里
  return <button>{data}</button>;
}
```

2. **使用 useCallback 稳定引用**
```typescript
const handleClick = useCallback(() => {
  // ...
}, [dependencies]);
```

3. **统一的错误处理**
```typescript
try {
  await doSomething();
} catch (error) {
  toast.error('操作失败', { description: String(error) });
}
```

---

### ❌ 避免的陷阱

1. **不要在 Presenter 中调用 API**
```typescript
// ✗ 错误
function View() {
  const data = await invoke('get_data');  // 不应该
}
```

2. **不要直接修改 Store 状态**
```typescript
// ✗ 错误
store.folders.push(newFolder);

// ✓ 正确
await store.addFolder(path);
```

3. **不要忘记清理副作用**
```typescript
useEffect(() => {
  const timer = setInterval(...);
  return () => clearInterval(timer);  // 清理
}, []);
```

---

## 🐛 快速排错指南

| 现象 | 可能原因 | 解决方案 |
|------|---------|---------|
| 扫描按钮无响应 | 路径未验证通过 | 检查控制台错误信息 |
| 监控列表为空 | Store 未加载数据 | 确认 `fetchFolders()` 被调用 |
| Toast 不显示 | Sonner 未正确配置 | 检查 `<Toaster />` 组件 |
| 类型错误 | TypeScript 推断失败 | 显式声明类型注解 |
| 样式不生效 | Tailwind 类名拼写错误 | 检查类名是否正确 |

---

## 📞 获取帮助

遇到问题？按以下顺序排查：

1. **查看控制台日志** - 90% 的问题会有错误提示
2. **检查网络请求** - Tauri 命令是否成功调用
3. **验证数据类型** - TypeScript 类型是否匹配
4. **查阅本文档** - 搜索关键词
5. **查看完整文档** - [架构设计](./FolderAnalysis-Module-Architecture.md)

---

**下一步**: 
- 📖 阅读 [架构设计文档](./FolderAnalysis-Module-Architecture.md) 深入了解
- 🔍 查看 [API 参考](./FolderAnalysis-API-Reference.md) 了解细节
- 💻 开始编码实践！

---

**文档版本**: 1.0.0  
**适用人群**: 新加入的开发者  
**预计阅读时间**: 5-10 分钟
