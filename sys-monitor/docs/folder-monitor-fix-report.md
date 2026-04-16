# 文件夹监控功能修复报告

## 📋 执行摘要

**修复时间**: 2026-04-16  
**修复人员**: 文件夹监控修复专家  
**项目**: sys-monitor (Tauri v2 + React 19 + Rust)  
**状态**: ✅ 已完成 P0 和 P1 级别修复

---

## 🔍 问题诊断

### P0: 严重 Bug - API 层参数命名不一致

#### 问题 1: `getFolderScans` 返回值解析错误

**症状**: 前端无法获取扫描历史记录  
**根本原因**: 
- 前端期望: `{ scans: FolderScan[] }` (包装对象)
- 后端返回: `Vec<FolderScan>` (直接数组)
- 代码位置: `folderAnalysisApi.ts:243`

**影响范围**: 所有调用 `getFolderScans` 的功能都会失败

#### 问题 2: Watched Folder API 参数名不一致

**症状**: 所有监控文件夹操作（添加、删除、切换状态）都失败  
**根本原因**:
- 前端发送: `dbPath`, `folderId`, `isActive` (camelCase)
- 后端期望: `db_path`, `folder_id`, `is_active` (snake_case)
- Tauri 命令参数映射是严格的，名称必须完全匹配

**受影响的 API**:
- `addWatchedFolder`: `dbPath` → `db_path`
- `listWatchedFolders`: `dbPath` → `db_path`
- `removeWatchedFolder`: `folderId, dbPath` → `folder_id, db_path`
- `toggleWatchedFolderActive`: `folderId, isActive, dbPath` → `folder_id, is_active, db_path`

### P1: 类型不匹配问题

#### 问题 3: `add_watched_folder` 返回值类型

**前端期望**: `WatchedFolder` 对象  
**后端返回**: `i64` (folder_id)  
**影响**: Store 层需要调整，但不影响核心功能

#### 问题 4: `toggle_watched_folder_active` 返回值

**前端期望**: `void`  
**后端返回**: `bool`  
**影响**: 轻微，类型定义不一致

---

## ✅ 修复方案

### 修复 1: folderAnalysisApi.ts

#### 修改内容

```typescript
// ❌ 修复前
get_folder_scans: {
  params: { path: string; limit: number; db_path: string };
  result: { scans: FolderScan[] };  // 错误的包装对象
};

export async function getFolderScans(...): Promise<FolderScan[]> {
  const response = await invokeSafe('get_folder_scans', {...});
  return response.scans || [];  // 尝试解包不存在的属性
}

// ✅ 修复后
get_folder_scans: {
  params: { path: string; limit: number; db_path: string };
  result: FolderScan[];  // 直接返回数组
};

export async function getFolderScans(...): Promise<FolderScan[]> {
  return invokeSafe('get_folder_scans', {
    path,
    limit,
    db_path: dbPath,
  });  // 直接返回，不解包
}
```

#### 参数命名统一

```typescript
// ❌ 修复前
add_watched_folder: {
  params: { path: string; alias?: string; dbPath: string };
  result: WatchedFolder;
};

// ✅ 修复后
add_watched_folder: {
  params: { path: string; alias?: string; db_path: string };
  result: number;  // Rust i64 对应 TS number
};
```

**所有受影响的方法**:
- ✅ `addWatchedFolder`: `dbPath` → `db_path`
- ✅ `listWatchedFolders`: `dbPath` → `db_path`
- ✅ `removeWatchedFolder`: `folderId, dbPath` → `folder_id, db_path`
- ✅ `toggleWatchedFolderActive`: `folderId, isActive, dbPath` → `folder_id, is_active, db_path`

### 修复 2: watchedFoldersStore.ts

#### 适配新的返回值类型

```typescript
// addFolder 方法
// ❌ 修复前
const newFolder = await addWatchedFolder(path, dbPath, alias);
// 期望得到 WatchedFolder 对象

// ✅ 修复后
await addWatchedFolder(path, dbPath, alias);
// 返回值为 folder_id (number)，不需要使用
await get().fetchFolders(); // 刷新列表获取完整数据
```

```typescript
// toggleActive 方法
// ❌ 修复前
await toggleWatchedFolderActive(id, newState, dbPath);
// 期望返回 void

// ✅ 修复后
await toggleWatchedFolderActive(id, newState, dbPath);
// 返回 boolean，但 Store 层不需要使用
```

---

## 🧪 测试验证

### 测试用例 1: 添加监控文件夹

```typescript
// 测试步骤
1. 选择文件夹路径
2. 调用 addWatchedFolder(path, dbPath, alias)
3. 验证返回值为 number (folder_id)
4. 验证列表中新增该文件夹
5. 验证文件监听服务已启动

// 预期结果
✅ API 调用成功
✅ 返回 folder_id > 0
✅ 列表刷新后显示新文件夹
✅ is_active = true
✅ 收到 "watcher-status-changed" 事件
```

### 测试用例 2: 获取扫描历史

```typescript
// 测试步骤
1. 先执行 scan_folder 创建扫描记录
2. 调用 getFolderScans(path, dbPath, limit=10)
3. 验证返回值为 FolderScan[] 数组

// 预期结果
✅ API 调用成功
✅ 返回数组而非包装对象
✅ 数组包含至少一条扫描记录
✅ 每条记录包含 id, path, scan_timestamp 等字段
```

### 测试用例 3: 切换监控状态

```typescript
// 测试步骤
1. 找到 active 的文件夹
2. 调用 toggleWatchedFolderActive(id, false, dbPath)
3. 验证返回值为 boolean
4. 验证文件夹状态变为 inactive
5. 验证文件监听服务已停止

// 预期结果
✅ API 调用成功
✅ 返回 true
✅ 文件夹 is_active = false
✅ 收到 "watcher-status-changed" 事件 (status: "stopped")
```

### 测试用例 4: 移除监控文件夹

```typescript
// 测试步骤
1. 选择要删除的文件夹 ID
2. 调用 removeWatchedFolder(folderId, dbPath)
3. 验证文件夹从列表中消失

// 预期结果
✅ API 调用成功
✅ 列表刷新后不包含该文件夹
✅ 文件监听服务已清理
```

---

## 📊 修复统计

| 类别 | 数量 | 状态 |
|------|------|------|
| P0 严重 Bug | 2 | ✅ 已修复 |
| P1 类型问题 | 2 | ✅ 已修复 |
| 修改的文件 | 2 | ✅ 完成 |
| 修改的代码行 | ~50 行 | ✅ 完成 |
| 添加的注释 | 8 条 | ✅ 完成 |

---

## 🔧 技术细节

### Tauri 命令参数映射规则

Tauri v2 使用严格的参数名称匹配：

```rust
// Rust 后端
#[tauri::command]
pub async fn add_watched_folder(
    app: tauri::AppHandle<R>,
    path: String,
    alias: Option<String>,
    db_path: String,  // snake_case
) -> Result<i64, AppError>
```

```typescript
// TypeScript 前端
await invokeSafe('add_watched_folder', {
  path: 'C:\\test',
  alias: 'My Folder',
  db_path: 'data.db'  // 必须使用 snake_case
});
```

**关键规则**:
1. 参数名称必须完全匹配（包括大小写和下划线）
2. Rust 的 `snake_case` 对应前端的 `snake_case`
3. 不能使用 camelCase 作为参数键名

### 类型映射

| Rust 类型 | TypeScript 类型 | 说明 |
|-----------|----------------|------|
| `i64` | `number` | JavaScript 没有 64 位整数 |
| `String` | `string` | 直接映射 |
| `Option<String>` | `string \| undefined` | 可选参数 |
| `bool` | `boolean` | 直接映射 |
| `Vec<T>` | `T[]` | 数组映射 |

---

## ⚠️ 注意事项

### 向后兼容性

✅ **完全兼容**: 所有修复都是内部实现细节，不影响外部调用方式

### 潜在风险

⚠️ **数据库路径**: 确保 `getDbPath()` 返回正确的路径  
⚠️ **文件权限**: 确保应用有权限访问监控的文件夹  
⚠️ **并发问题**: Store 层的乐观更新已正确处理回滚

### 性能优化建议

1. **批量操作**: 避免频繁调用 `fetchFolders()`，可以合并多次操作
2. **防抖处理**: 文件监听服务已有 5 秒防抖，无需额外处理
3. **内存管理**: 大量文件变更时注意事件缓冲区大小（当前 1000）

---

## 📝 后续工作建议

### P2: 功能增强

- [ ] 添加监控文件夹配置界面（阈值设置）
- [ ] 实现阈值告警通知 UI
- [ ] 添加文件变更历史查看功能
- [ ] 支持导出监控报告

### P3: 优化改进

- [ ] 添加单元测试覆盖 API 层
- [ ] 集成 E2E 测试验证端到端流程
- [ ] 添加性能监控和日志分析
- [ ] 优化大数据量时的扫描性能

---

## 🎯 结论

本次修复成功解决了文件夹监控功能的所有 P0 和 P1 级别问题：

1. ✅ 修复了 `getFolderScans` 返回值解析错误
2. ✅ 统一了所有 Watched Folder API 的参数命名
3. ✅ 修正了返回值类型定义
4. ✅ 更新了 Store 层以适配新的 API

**预期效果**: 文件夹监控功能现在应该可以正常工作，包括添加、删除、切换状态和查看扫描历史。

**建议下一步**: 进行完整的端到端测试，验证所有功能正常运行。

---

**修复完成时间**: 2026-04-16  
**文档版本**: v1.0  
**维护人员**: 文件夹监控修复专家
