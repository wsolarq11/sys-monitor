# FolderAnalysis 模块 - API 参考文档

## 📑 目录

- [组件 API](#组件-api)
- [类型定义](#类型定义)
- [Store API](#store-api)
- [工具函数](#工具函数)
- [Tauri 命令](#tauri-命令)

---

## 组件 API

### FolderAnalysisContainer

**文件**: `src/components/FolderAnalysis/FolderAnalysisContainer.tsx`  
**类型**: Container Component (无 props，内部管理状态)

#### 导出

```typescript
export function FolderAnalysisContainer(): JSX.Element
```

#### 使用示例

```tsx
import { FolderAnalysisContainer } from './components/FolderAnalysis';

function App() {
  return <FolderAnalysisContainer />;
}
```

#### 内部状态

| 状态 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| selectedPath | `string` | `''` | 当前选中的文件夹路径 |
| scans | `FolderScan[]` | `[]` | 扫描历史记录 |
| isScanning | `boolean` | `false` | 是否正在扫描 |
| scanResult | `ScanResultData \| null` | `null` | 最近一次扫描结果 |
| dbPath | `string` | `''` | 数据库路径 |
| error | `string \| null` | `null` | 错误信息 |
| scanProgress | `string \| null` | `null` | 扫描进度文本 |

#### 内部方法

##### handleSelectFolder

```typescript
const handleSelectFolder: () => Promise<void>
```

打开系统文件夹选择对话框，更新 `selectedPath` 状态。

**异常**:
- 用户取消选择：静默处理（记录日志）
- 其他错误：设置 `error` 状态

##### handlePathChange

```typescript
const handlePathChange: (path: string) => void
```

**参数**:
- `path`: 新的路径字符串

更新 `selectedPath` 并清除之前的错误。

##### handleScan

```typescript
const handleScan: () => Promise<void>
```

执行完整的扫描流程：
1. 验证路径
2. 调用 `scan_folder` 命令
3. 更新扫描结果
4. 刷新历史记录

**依赖**: `selectedPath`, `dbPath`

---

### FolderAnalysisView

**文件**: `src/components/FolderAnalysis/FolderAnalysisView.tsx`  
**类型**: Presentational Component

#### Props 接口

```typescript
interface FolderAnalysisViewProps {
  selectedPath: string;
  onPathChange: (path: string) => void;
  onSelectFolder: () => void;
  onScan: () => void;
  isScanning: boolean;
  error: string | null;
  scanProgress: string | null;
  scanResult: ScanResultData | null;
  scans: FolderScan[];
}
```

#### 导出

```typescript
export function FolderAnalysisView(props: FolderAnalysisViewProps): JSX.Element
```

#### 使用示例

```tsx
<FolderAnalysisView
  selectedPath={selectedPath}
  onPathChange={setSelectedPath}
  onSelectFolder={handleSelectFolder}
  onScan={handleScan}
  isScanning={isScanning}
  error={error}
  scanProgress={scanProgress}
  scanResult={scanResult}
  scans={scans}
/>
```

#### UI 结构

```
┌─────────────────────────────────────┐
│  [路径输入框] [浏览] [扫描文件夹]    │
├─────────────────────────────────────┤
│  [错误提示] (条件渲染)               │
├─────────────────────────────────────┤
│  [扫描进度] (条件渲染)               │
├─────────────────────────────────────┤
│  [扫描结果] (条件渲染)               │
│  - 总大小                            │
│  - 文件数                            │
│  - 文件夹数                          │
│  - 扫描耗时                          │
├─────────────────────────────────────┤
│  [扫描历史列表] (条件渲染)           │
│  - 时间戳                            │
│  - 大小                              │
│  - 文件/文件夹数量                   │
└─────────────────────────────────────┘
```

---

### WatchedFoldersList

**文件**: `src/components/FolderAnalysis/WatchedFoldersList.tsx`  
**类型**: Standalone Component (自包含状态管理)

#### 导出

```typescript
export function WatchedFoldersList(): JSX.Element
```

#### 使用示例

```tsx
<WatchedFoldersList />
```

#### 内部状态（来自 Store）

| 状态 | 类型 | 来源 |
|------|------|------|
| folders | `WatchedFolder[]` | `useWatchedFoldersStore` |
| loading | `boolean` | `useWatchedFoldersStore` |
| error | `string \| null` | `useWatchedFoldersStore` |

#### 内部方法

##### handleAddFolder

```typescript
const handleAddFolder: () => Promise<void>
```

添加新的监控文件夹。

**流程**:
1. 调用 `select_folder` 命令
2. 调用 `store.addFolder(path)`
3. 显示 Toast 通知

**异常处理**:
- 用户取消：静默处理
- 其他错误：显示错误 Toast

##### handleRemoveFolder

```typescript
const handleRemoveFolder: (folder: WatchedFolder) => Promise<void>
```

**参数**:
- `folder`: 要移除的文件夹对象

移除指定的监控文件夹并显示通知。

##### handleToggleActive

```typescript
const handleToggleActive: (folder: WatchedFolder) => Promise<void>
```

**参数**:
- `folder`: 要切换状态的文件夹对象

切换文件夹的激活状态（运行中 ↔ 已停用）。

---

## 类型定义

### ScanResultData

**位置**: `FolderAnalysisView.tsx`

```typescript
interface ScanResultData {
  total_size: number;          // 总字节数
  file_count: number;          // 文件数量
  folder_count: number;        // 文件夹数量
  scan_duration_ms: number;    // 扫描耗时（毫秒）
}
```

**用途**: 表示单次扫描的结果数据

**示例**:
```typescript
{
  total_size: 1073741824,      // 1 GB
  file_count: 1523,
  folder_count: 234,
  scan_duration_ms: 3456
}
```

---

### FolderScan

**位置**: `FolderAnalysisView.tsx`

```typescript
interface FolderScan {
  id: number;                  // 记录 ID（数据库主键）
  path: string;                // 扫描的文件夹路径
  scan_timestamp: number;      // 扫描时间戳（Unix 秒）
  total_size: number;          // 总大小（字节）
  file_count: number;          // 文件数量
  folder_count: number;        // 文件夹数量
  scan_duration_ms: number | null; // 扫描耗时（毫秒），可为 null
}
```

**用途**: 表示一条扫描历史记录

**示例**:
```typescript
{
  id: 42,
  path: "C:\\Users\\Admin\\Documents",
  scan_timestamp: 1713254400,  // 2024-04-16 12:00:00 UTC
  total_size: 5368709120,      // 5 GB
  file_count: 8934,
  folder_count: 567,
  scan_duration_ms: 12345
}
```

---

### WatchedFolder

**位置**: `src/stores/watchedFoldersStore.ts`

```typescript
interface WatchedFolder {
  id: number;                      // 记录 ID
  path: string;                    // 文件夹路径
  alias?: string;                  // 别名（可选）
  is_active: boolean;              // 是否激活监控
  recursive: boolean;              // 是否递归监控子文件夹
  debounce_ms: number;             // 事件防抖延迟（毫秒）
  size_threshold_bytes?: number;   // 大小阈值（字节）
  file_count_threshold?: number;   // 文件数量阈值
  notify_on_create: boolean;       // 文件创建时通知
  notify_on_delete: boolean;       // 文件删除时通知
  notify_on_modify: boolean;       // 文件修改时通知
  last_scan_timestamp?: number;    // 最后扫描时间戳
  last_event_timestamp?: number;   // 最后事件时间戳
  total_events_count: number;      // 总事件数量
}
```

**用途**: 表示一个被监控的文件夹配置

**示例**:
```typescript
{
  id: 1,
  path: "D:\\Projects",
  alias: "项目文件夹",
  is_active: true,
  recursive: true,
  debounce_ms: 500,
  size_threshold_bytes: 1073741824,  // 1 GB
  file_count_threshold: 10000,
  notify_on_create: true,
  notify_on_delete: false,
  notify_on_modify: true,
  last_scan_timestamp: 1713254400,
  last_event_timestamp: 1713258000,
  total_events_count: 156
}
```

---

## Store API

### useWatchedFoldersStore

**文件**: `src/stores/watchedFoldersStore.ts`  
**库**: Zustand 5.0.0

#### State

```typescript
interface WatchedFoldersState {
  folders: WatchedFolder[];    // 监控文件夹列表
  loading: boolean;            // 加载状态
  error: string | null;        // 错误信息
}
```

#### Actions

##### fetchFolders

```typescript
fetchFolders: () => Promise<void>
```

从后端获取所有监控文件夹列表。

**副作用**:
- 设置 `loading = true`
- 调用 `get_db_path` 命令
- 调用 `list_watched_folders` 命令
- 更新 `folders` 状态
- 错误时设置 `error`

**使用示例**:
```typescript
const { fetchFolders } = useWatchedFoldersStore();

useEffect(() => {
  fetchFolders();
}, []);
```

---

##### addFolder

```typescript
addFolder: (path: string, alias?: string) => Promise<void>
```

添加新的监控文件夹。

**参数**:
- `path`: 文件夹路径（必需）
- `alias`: 别名（可选）

**副作用**:
- 调用 `get_db_path` 命令
- 调用 `add_watched_folder` 命令
- 自动调用 `fetchFolders()` 刷新列表
- 错误时设置 `error` 并抛出异常

**异常**:
- 抛出后端返回的错误

**使用示例**:
```typescript
const { addFolder } = useWatchedFoldersStore();

try {
  await addFolder("C:\\Users\\Admin\\Documents", "文档");
  console.log('添加成功');
} catch (error) {
  console.error('添加失败:', error);
}
```

---

##### removeFolder

```typescript
removeFolder: (id: number) => Promise<void>
```

移除指定的监控文件夹。

**参数**:
- `id`: 文件夹记录 ID

**副作用**:
- 调用 `get_db_path` 命令
- 调用 `remove_watched_folder` 命令
- 自动调用 `fetchFolders()` 刷新列表
- 错误时设置 `error` 并抛出异常

**使用示例**:
```typescript
const { removeFolder } = useWatchedFoldersStore();

await removeFolder(42);
```

---

##### toggleActive

```typescript
toggleActive: (id: number) => Promise<void>
```

切换文件夹的激活状态。

**参数**:
- `id`: 文件夹记录 ID

**副作用**:
- 调用 `get_db_path` 命令
- 调用 `toggle_watched_folder_active` 命令
- **乐观更新**本地状态（立即更新 UI）
- 错误时设置 `error` 并抛出异常

**注意**: ⚠️ 当前实现缺少回滚机制，如果后端失败，UI 状态会与实际不一致。

**使用示例**:
```typescript
const { toggleActive } = useWatchedFoldersStore();

await toggleActive(42);
```

---

#### 完整使用示例

```typescript
import { useWatchedFoldersStore } from '../stores/watchedFoldersStore';

function MyComponent() {
  const { 
    folders, 
    loading, 
    error, 
    fetchFolders, 
    addFolder, 
    removeFolder, 
    toggleActive 
  } = useWatchedFoldersStore();
  
  useEffect(() => {
    fetchFolders();
  }, []);
  
  const handleAdd = async () => {
    try {
      await addFolder("D:\\Test", "测试文件夹");
    } catch (err) {
      console.error(err);
    }
  };
  
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  
  return (
    <ul>
      {folders.map(folder => (
        <li key={folder.id}>
          {folder.path}
          <button onClick={() => toggleActive(folder.id)}>
            {folder.is_active ? '停用' : '激活'}
          </button>
          <button onClick={() => removeFolder(folder.id)}>
            移除
          </button>
        </li>
      ))}
    </ul>
  );
}
```

---

## 工具函数

### validation.ts

**文件**: `src/utils/validation.ts`

#### isValidPath

```typescript
function isValidPath(path: string): boolean
```

验证路径是否为非空字符串。

**参数**:
- `path`: 待验证的路径

**返回**: `true` 如果路径有效

**示例**:
```typescript
isValidPath("C:\\Users");     // true
isValidPath("");              // false
isValidPath("   ");           // false
```

---

#### isValidPathFormat

```typescript
function isValidPathFormat(path: string): boolean
```

验证路径格式是否符合当前操作系统规范。

**参数**:
- `path`: 待验证的路径

**返回**: `true` 如果格式正确

**规则**:
- Windows: `X:\...` 或 `\\...` (UNC 路径)
- Unix: `/...`

**示例**:
```typescript
// Windows
isValidPathFormat("C:\\Users\\Admin");  // true
isValidPathFormat("\\\\server\\share"); // true
isValidPathFormat("relative\\path");    // false

// Unix
isValidPathFormat("/home/user");        // true
isValidPathFormat("./relative");        // false
```

---

#### getPathValidationError

```typescript
function getPathValidationError(path: string): string
```

获取路径验证错误信息。

**参数**:
- `path`: 待验证的路径

**返回**: 错误消息字符串，如果验证通过则返回空字符串

**示例**:
```typescript
getPathValidationError("");             // "路径不能为空"
getPathValidationError("invalid");      // "路径格式不正确"
getPathValidationError("C:\\Valid");    // ""
```

**使用场景**:
```typescript
const error = getPathValidationError(selectedPath);
if (error) {
  setError(error);
  return;
}
```

---

### format.ts

**文件**: `src/utils/format.ts`

#### formatBytes

```typescript
function formatBytes(bytes: number): string
```

格式化字节数为可读的大小字符串（支持 B/KB/MB/GB/TB）。

**参数**:
- `bytes`: 字节数

**返回**: 格式化后的字符串，保留 2 位小数

**示例**:
```typescript
formatBytes(0);              // "0 B"
formatBytes(1024);           // "1 KB"
formatBytes(1048576);        // "1 MB"
formatBytes(1073741824);     // "1 GB"
formatBytes(1536);           // "1.5 KB"
```

**算法**:
```typescript
const k = 1024;
const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
const i = Math.floor(Math.log(bytes) / Math.log(k));
return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
```

---

#### formatPercent

```typescript
function formatPercent(value: number): string
```

格式化数值为百分比字符串。

**参数**:
- `value`: 数值（0-100）

**返回**: 格式化后的百分比，保留 1 位小数

**示例**:
```typescript
formatPercent(85.5);      // "85.5%"
formatPercent(100);       // "100.0%"
formatPercent(0);         // "0.0%"
```

---

#### formatSize

```typescript
function formatSize(bytes: number): string
```

格式化字节数为简短的可读大小（用于扫描结果展示）。

**参数**:
- `bytes`: 字节数

**返回**: 格式化后的字符串（仅支持 B/KB/MB/GB）

**与 formatBytes 的区别**:
- 不支持 TB
- 更简洁的实现
- 专为扫描结果优化

**示例**:
```typescript
formatSize(500);                 // "500 B"
formatSize(1536);                // "1.50 KB"
formatSize(1048576);             // "1.00 MB"
formatSize(5368709120);          // "5.00 GB"
```

**实现**:
```typescript
if (bytes < 1024) return `${bytes} B`;
if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
```

---

### time.ts

**文件**: `src/utils/time.ts`

#### formatTimestamp

```typescript
function formatTimestamp(timestamp: number): string
```

格式化 Unix 时间戳为本地日期时间字符串。

**参数**:
- `timestamp`: Unix 时间戳（秒）

**返回**: 本地化的日期时间字符串（中文格式）

**示例**:
```typescript
formatTimestamp(1713254400);  
// "2024/4/16 12:00:00" (取决于系统区域设置)
```

**实现**:
```typescript
return new Date(timestamp * 1000).toLocaleString('zh-CN');
```

---

#### formatTimestampShort

```typescript
function formatTimestampShort(timestamp: number): string
```

格式化 Unix 时间戳为简短的日期时间字符串。

**参数**:
- `timestamp`: Unix 时间戳（秒）

**返回**: 简短格式（月/日 时:分）

**示例**:
```typescript
formatTimestampShort(1713254400);  
// "4/16 12:00"
```

**实现**:
```typescript
return new Date(timestamp * 1000).toLocaleString('zh-CN', {
  month: 'numeric',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
});
```

---

#### formatDuration

```typescript
function formatDuration(ms: number): string
```

格式化毫秒数为可读的耗时字符串。

**参数**:
- `ms`: 毫秒数

**返回**: 格式化后的耗时（ms 或 s）

**示例**:
```typescript
formatDuration(500);       // "500ms"
formatDuration(1500);      // "1.50s"
formatDuration(60000);     // "60.00s"
```

**实现**:
```typescript
if (ms < 1000) return `${ms}ms`;
return `${(ms / 1000).toFixed(2)}s`;
```

---

#### formatRelativeTime

```typescript
function formatRelativeTime(timestamp: number): string
```

格式化相对时间（多久以前）。

**参数**:
- `timestamp`: Unix 时间戳（秒）

**返回**: 相对时间字符串（刚刚、X分钟前、X小时前、X天前）

**示例**:
```typescript
// 假设现在是 2024-04-16 12:00:00
formatRelativeTime(1713254100);  // "5分钟前" (300秒前)
formatRelativeTime(1713250800);  // "1小时前" (3600秒前)
formatRelativeTime(1713168000);  // "1天前" (86400秒前)
```

**实现**:
```typescript
const now = Date.now();
const diff = now - timestamp * 1000;

const seconds = Math.floor(diff / 1000);
const minutes = Math.floor(seconds / 60);
const hours = Math.floor(minutes / 60);
const days = Math.floor(hours / 24);

if (days > 0) return `${days}天前`;
if (hours > 0) return `${hours}小时前`;
if (minutes > 0) return `${minutes}分钟前`;
return '刚刚';
```

---

## Tauri 命令

### 数据库相关

#### get_db_path

```rust
#[tauri::command]
fn get_db_path() -> Result<String, String>
```

**前端调用**:
```typescript
const dbPath = await invoke<string>('get_db_path');
```

**返回**: 数据库文件的绝对路径

**用途**: 获取 SQLite 数据库路径，用于所有数据库操作

---

### 文件夹选择

#### select_folder

```rust
#[tauri::command]
fn select_folder() -> Result<String, String>
```

**前端调用**:
```typescript
const path = await invoke<string>('select_folder');
```

**返回**: 用户选择的文件夹路径

**异常**:
- 用户取消选择：抛出 `"No folder selected"` 错误

**用途**: 打开系统文件夹选择对话框

---

### 扫描相关

#### scan_folder

```rust
#[tauri::command]
fn scan_folder(path: String, db_path: String) -> Result<ScanResultData, String>
```

**前端调用**:
```typescript
const result = await invoke<ScanResultData>('scan_folder', { 
  path: selectedPath, 
  db_path: dbPath 
});
```

**参数**:
- `path`: 要扫描的文件夹路径
- `db_path`: 数据库路径

**返回**: `ScanResultData` 对象

**用途**: 执行文件夹深度扫描，计算总大小、文件数、文件夹数

---

#### get_folder_scans

```rust
#[tauri::command]
fn get_folder_scans(path: String, limit: u32, db_path: String) -> Result<FolderScansResponse, String>
```

**前端调用**:
```typescript
const response = await invoke<{ scans: FolderScan[] }>('get_folder_scans', { 
  path: selectedPath, 
  limit: 10,
  db_path: dbPath 
});
```

**参数**:
- `path`: 文件夹路径
- `limit`: 返回记录数量限制
- `db_path`: 数据库路径

**返回**: `{ scans: FolderScan[] }` 对象

**用途**: 获取指定文件夹的历史扫描记录

---

### 监控文件夹管理

#### list_watched_folders

```rust
#[tauri::command]
fn list_watched_folders(db_path: String) -> Result<WatchedFolder[], String>
```

**前端调用**:
```typescript
const folders = await invoke<WatchedFolder[]>('list_watched_folders', { dbPath });
```

**参数**:
- `dbPath`: 数据库路径

**返回**: `WatchedFolder[]` 数组

**用途**: 获取所有监控文件夹列表

---

#### add_watched_folder

```rust
#[tauri::command]
fn add_watched_folder(path: String, alias: Option<String>, db_path: String) -> Result<(), String>
```

**前端调用**:
```typescript
await invoke('add_watched_folder', { 
  path: "C:\\Users\\Admin", 
  alias: "用户文件夹",
  dbPath 
});
```

**参数**:
- `path`: 文件夹路径
- `alias`: 别名（可选）
- `dbPath`: 数据库路径

**返回**: `void`

**用途**: 添加新的监控文件夹到数据库

---

#### remove_watched_folder

```rust
#[tauri::command]
fn remove_watched_folder(folder_id: u32, db_path: String) -> Result<(), String>
```

**前端调用**:
```typescript
await invoke('remove_watched_folder', { 
  folderId: 42, 
  dbPath 
});
```

**参数**:
- `folderId`: 文件夹记录 ID
- `dbPath`: 数据库路径

**返回**: `void`

**用途**: 从数据库中移除监控文件夹

---

#### toggle_watched_folder_active

```rust
#[tauri::command]
fn toggle_watched_folder_active(folder_id: u32, is_active: bool, db_path: String) -> Result<(), String>
```

**前端调用**:
```typescript
await invoke('toggle_watched_folder_active', { 
  folderId: 42, 
  isActive: true,
  dbPath 
});
```

**参数**:
- `folderId`: 文件夹记录 ID
- `isActive`: 新的激活状态
- `dbPath`: 数据库路径

**返回**: `void`

**用途**: 切换文件夹的监控激活状态

---

## 附录

### 错误码参考

| 错误消息 | 来源 | 处理方式 |
|---------|------|---------|
| `No folder selected` | `select_folder` | 用户取消，静默处理 |
| `路径不能为空` | `validation.ts` | 显示内联错误 |
| `路径格式不正确` | `validation.ts` | 显示内联错误 |
| 网络/IO 错误 | Tauri Backend | 显示 Toast 通知 |
| 数据库错误 | Tauri Backend | 显示 Toast 通知 |

### 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | 2026-04-16 | 初始文档生成 |

### 相关文档

- [架构设计文档](./FolderAnalysis-Module-Architecture.md)
- [架构图解](./FolderAnalysis-Architecture-Diagrams.md)

---

**文档维护**: Documentation Agent  
**最后更新**: 2026-04-16
