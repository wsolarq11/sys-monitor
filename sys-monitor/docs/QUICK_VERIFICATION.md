# 文件夹监控功能 - 快速验证指南

## 🎯 验证目标

确认修复后的文件夹监控功能可以正常工作。

---

## ✅ 验证步骤

### Step 1: 编译检查

```bash
cd sys-monitor

# 前端 TypeScript 编译检查
npm run type-check

# 或者完整构建
npm run build
```

**预期结果**: 
- ✅ 无 TypeScript 错误
- ✅ 无类型不匹配警告

---

### Step 2: 启动应用

```bash
# 开发模式
npm run tauri dev

# 或生产模式
npm run tauri build
```

**预期结果**:
- ✅ 应用成功启动
- ✅ 控制台无错误日志

---

### Step 3: 功能测试

#### 测试 3.1: 添加监控文件夹

1. 打开应用，进入"文件夹监控"页面
2. 点击"添加监控文件夹"按钮
3. 选择一个测试文件夹（例如 `C:\Test`）
4. 输入别名（可选）
5. 点击确认

**预期结果**:
- ✅ 文件夹添加到列表
- ✅ 状态显示为 "Active"
- ✅ 控制台显示: `[TauriAPI] add_watched_folder succeeded`
- ✅ 返回值为数字 (folder_id)

**验证命令** (浏览器控制台):
```javascript
// 检查 API 调用
console.log('添加的文件夹 ID:', folderId); // 应该是 number
```

---

#### 测试 3.2: 查看扫描历史

1. 先对文件夹执行一次扫描
2. 在文件夹详情页面查看"扫描历史"

**预期结果**:
- ✅ 显示扫描历史记录列表
- ✅ 每条记录包含: ID、时间戳、文件大小、文件数量
- ✅ 控制台无 "Cannot read property 'scans' of undefined" 错误

**验证命令** (浏览器控制台):
```javascript
// 手动调用 API 验证
import { getFolderScans, getDbPath } from './services/folderAnalysisApi';

const dbPath = await getDbPath();
const scans = await getFolderScans('C:\\Test', dbPath, 10);
console.log('扫描历史:', scans);
console.log('是否为数组:', Array.isArray(scans)); // 应该是 true
```

---

#### 测试 3.3: 切换监控状态

1. 在监控文件夹列表中，找到刚添加的文件夹
2. 点击"停用"按钮

**预期结果**:
- ✅ 文件夹状态变为 "Inactive"
- ✅ UI 立即更新（乐观更新）
- ✅ 控制台显示: `[TauriAPI] toggle_watched_folder_active succeeded`
- ✅ 返回值为 `true`

**验证命令** (浏览器控制台):
```javascript
// 监听状态变化事件
window.__TAURI__.event.listen('watcher-status-changed', (event) => {
  console.log('监听器状态变化:', event.payload);
  // 应该显示: { folder_id: X, status: "stopped" }
});
```

---

#### 测试 3.4: 移除监控文件夹

1. 点击文件夹的"删除"按钮
2. 确认删除操作

**预期结果**:
- ✅ 文件夹从列表中消失
- ✅ 控制台无错误
- ✅ 文件监听服务已停止

---

### Step 4: 文件变更通知测试

#### 测试 4.1: 触发文件变更

1. 确保文件夹处于 "Active" 状态
2. 在监控的文件夹中创建/修改/删除文件
3. 等待 5 秒（防抖时间）

**预期结果**:
- ✅ 收到聚合通知事件
- ✅ 控制台显示文件变更信息
- ✅ 数据库记录了事件

**验证命令** (浏览器控制台):
```javascript
// 监听文件变更事件
window.__TAURI__.event.listen('folder-change-aggregated', (event) => {
  console.log('文件变更聚合:', event.payload);
  /*
  应该显示类似:
  {
    folder_id: 1,
    folder_path: "C:\\Test",
    create_count: 2,
    delete_count: 0,
    modify_count: 1,
    total_count: 3,
    summary: "新建 2 个文件, 修改 1 个文件",
    sample_files: ["C:\\Test\\file1.txt", ...]
  }
  */
});
```

---

#### 测试 4.2: 阈值告警测试

1. 设置文件夹的大小阈值（如果 UI 支持）
2. 向文件夹添加大文件，超过阈值
3. 等待下一次扫描

**预期结果**:
- ✅ 收到阈值告警事件
- ✅ 控制台显示告警信息

**验证命令** (浏览器控制台):
```javascript
// 监听阈值告警
window.__TAURI__.event.listen('folder-threshold-alert', (event) => {
  console.log('阈值告警:', event.payload);
  /*
  应该显示类似:
  {
    folder_id: 1,
    alert_type: "size_exceeded",
    title: "文件夹 C:\\Test 大小超标",
    description: "当前大小: 150.50 MB, 阈值: 100.00 MB",
    threshold_value: 100.0,
    actual_value: 150.5
  }
  */
});
```

---

## 🔍 常见问题排查

### 问题 1: API 调用失败，提示参数错误

**症状**: 
```
[TauriAPI] add_watched_folder failed: invalid parameters
```

**原因**: 参数名称不匹配  
**解决**: 确认使用的是 `db_path` 而不是 `dbPath`

**验证**:
```javascript
// ❌ 错误
await invoke('add_watched_folder', { path: '...', dbPath: '...' });

// ✅ 正确
await invoke('add_watched_folder', { path: '...', db_path: '...' });
```

---

### 问题 2: 获取扫描历史返回空数组

**症状**: `getFolderScans` 返回 `[]`

**可能原因**:
1. 尚未执行过扫描
2. 路径不匹配（注意大小写和斜杠）

**解决**:
```javascript
// 先执行扫描
await scanFolder('C:\\Test', dbPath);

// 再获取历史
const scans = await getFolderScans('C:\\Test', dbPath, 10);
console.log('扫描历史:', scans);
```

---

### 问题 3: 文件监听不工作

**症状**: 文件变更后没有收到通知

**检查清单**:
- [ ] 文件夹状态是 "Active"
- [ ] 文件监听服务已启动
- [ ] 等待了至少 5 秒（防抖时间）
- [ ] 文件确实在监控的文件夹内

**验证**:
```javascript
// 检查正在监听的文件夹
const folders = await listWatchedFolders(dbPath);
const activeFolders = folders.filter(f => f.is_active);
console.log('活跃的监控文件夹:', activeFolders);
```

---

### 问题 4: TypeScript 编译错误

**症状**: 
```
Type 'number' is not assignable to type 'WatchedFolder'
```

**原因**: Store 层未适配新的返回值类型  
**解决**: 确认 `watchedFoldersStore.ts` 已更新

---

## 📊 验证检查表

完成以下检查项，确认所有功能正常：

- [ ] **编译通过**: 无 TypeScript 错误
- [ ] **应用启动**: 无运行时错误
- [ ] **添加文件夹**: 成功添加并返回 folder_id
- [ ] **列出文件夹**: 正确显示所有监控文件夹
- [ ] **扫描历史**: 返回数组格式，数据正确
- [ ] **切换状态**: 状态切换成功，监听器启停正常
- [ ] **删除文件夹**: 成功删除，清理监听器
- [ ] **文件变更通知**: 收到聚合事件
- [ ] **阈值告警**: 超过阈值时收到告警（如已配置）

---

## 🐛 调试技巧

### 启用详细日志

在浏览器控制台中：
```javascript
// 启用调试日志
localStorage.setItem('debug', '*');

// 或只查看 Tauri API 日志
localStorage.setItem('debug', 'TauriAPI:*');
```

### 查看后端日志

Rust 后端日志输出到：
- Windows: `%APPDATA%\sys-monitor\logs\`
- 或在开发模式下直接显示在终端

### 网络请求监控

使用浏览器开发者工具：
1. 打开 DevTools (F12)
2. 切换到 "Network" 标签
3. 筛选 "tauri" 相关请求
4. 查看请求参数和响应

---

## 📝 测试报告模板

完成验证后，填写此报告：

```markdown
## 测试报告

**测试日期**: ___________
**测试人员**: ___________
**应用版本**: ___________

### 测试结果

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 编译检查 | ☐ 通过 ☐ 失败 | |
| 添加文件夹 | ☐ 通过 ☐ 失败 | |
| 扫描历史 | ☐ 通过 ☐ 失败 | |
| 切换状态 | ☐ 通过 ☐ 失败 | |
| 删除文件夹 | ☐ 通过 ☐ 失败 | |
| 文件变更通知 | ☐ 通过 ☐ 失败 | |
| 阈值告警 | ☐ 通过 ☐ 失败 ☐ 未测试 | |

### 发现的问题

1. _________________________________
2. _________________________________

### 总体评价

☐ 完全通过，可以发布
☐ 基本通过，有小问题
☐ 需要进一步修复
```

---

## 🎉 验证完成

如果所有测试都通过，恭喜！文件夹监控功能已成功修复。

**下一步建议**:
1. 运行完整的 E2E 测试套件
2. 进行性能测试（大量文件场景）
3. 更新用户文档
4. 准备发布新版本

---

**文档版本**: v1.0  
**最后更新**: 2026-04-16
