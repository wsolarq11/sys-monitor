# Sys-Monitor 测试套件指南

## 📋 目录

- [概述](#概述)
- [测试结构](#测试结构)
- [环境准备](#环境准备)
- [运行测试](#运行测试)
- [测试覆盖范围](#测试覆盖范围)
- [最佳实践](#最佳实践)
- [故障排查](#故障排查)

## 概述

Sys-Monitor 项目采用多层次测试策略，确保代码质量和功能稳定性：

- **单元测试**：验证单个函数和模块的正确性
- **集成测试**：验证模块间的交互
- **E2E测试**：验证完整的用户流程
- **性能测试**：验证系统性能指标

## 测试结构

```
sys-monitor/
├── src-tauri/                    # Rust 后端
│   ├── src/
│   │   ├── commands/
│   │   │   ├── system.rs         # 系统监控命令
│   │   │   └── system_test.rs    # ✅ 系统命令测试
│   │   ├── db/
│   │   │   └── repository.rs     # 数据库操作（已包含测试）
│   │   └── services/
│   │       ├── file_watcher_service.rs      # 文件监听服务
│   │       └── file_watcher_service_test.rs # ✅ 文件监听测试
│   └── tests/                    # 集成测试目录
│
├── src/                          # TypeScript 前端
│   ├── services/
│   │   ├── folderAnalysisApi.ts           # API层
│   │   └── folderAnalysisApi.test.ts      # ✅ API测试
│   └── stores/
│       ├── metricsStore.ts                # 指标状态管理
│       ├── metricsStore.test.ts           # ✅ 指标Store测试
│       ├── scanStore.ts                   # 扫描状态管理
│       └── scanStore.test.ts              # ✅ 扫描Store测试
│
└── tests/e2e/tests/              # E2E测试
    ├── core-functionality.spec.ts         # ✅ 核心功能E2E
    └── performance.spec.ts                # ✅ 性能测试
```

## 环境准备

### 1. 安装依赖

```bash
# 安装 Rust 依赖
cd sys-monitor/src-tauri
cargo build

# 安装 Node.js 依赖
cd ..
pnpm install
```

### 2. 安装测试工具

```bash
# 安装 Playwright 浏览器
cd tests/e2e
npx playwright install

# 安装 Vitest UI（可选）
cd ../..
pnpm add -D @vitest/ui
```

## 运行测试

### Rust 单元测试

```bash
# 运行所有 Rust 测试
cd sys-monitor/src-tauri
cargo test

# 运行特定模块测试
cargo test system_tests
cargo test repository
cargo test file_watcher_service_tests

# 运行测试并显示输出
cargo test -- --nocapture

# 生成测试覆盖率报告
cargo install cargo-tarpaulin
cargo tarpaulin --out Html
```

**预期输出示例：**
```
running 15 tests
test commands::system_tests::test_get_system_metrics_returns_valid_data ... ok
test commands::system_tests::test_get_cpu_info_returns_valid_json ... ok
test db::repository::tests::test_repository_initialization ... ok
...

test result: ok. 15 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

### TypeScript 单元测试

```bash
# 运行所有 TypeScript 测试
cd sys-monitor
pnpm test

# 监视模式（开发时使用）
pnpm test:watch

# 使用 UI 界面
pnpm test:ui

# 运行特定测试文件
pnpm vitest run src/services/folderAnalysisApi.test.ts

# 生成覆盖率报告
pnpm vitest run --coverage
```

**预期输出示例：**
```
✓ src/services/folderAnalysisApi.test.ts (18)
✓ src/stores/metricsStore.test.ts (20)
✓ src/stores/scanStore.test.ts (22)

Test Files  3 passed (3)
Tests       60 passed (60)
Start at    10:30:00
Duration    1.2s
```

### E2E 测试

```bash
# 运行所有 E2E 测试
cd sys-monitor/tests/e2e
npx playwright test

# 运行特定测试文件
npx playwright test core-functionality.spec.ts
npx playwright test performance.spec.ts

# 以有头模式运行（可见浏览器）
npx playwright test --headed

# 调试模式
npx playwright test --debug

# 生成HTML报告
npx playwright test --reporter=html
npx playwright show-report
```

**预期输出示例：**
```
Running 24 tests using 4 workers

✓ tests/core-functionality.spec.ts:23:3 › 应该正确显示Dashboard页面 (2.1s)
✓ tests/core-functionality.spec.ts:35:3 › 应该显示CPU使用率图表 (3.5s)
✓ tests/performance.spec.ts:18:3 › 数据库批量插入性能测试 (800ms)
...

24 passed (45.2s)
```

### 性能测试

```bash
# 运行性能测试
cd sys-monitor/tests/e2e
npx playwright test performance.spec.ts

# 查看性能报告
npx playwright show-report
```

**关键性能指标：**
- 页面加载时间：< 5秒
- 首次内容绘制：< 3秒
- API响应时间：< 100ms
- 内存增长：< 10MB
- 批量插入性能：> 1000 ops/sec

## 测试覆盖范围

### P0: Rust 单元测试 ✅

#### 1. 系统监控命令 (`commands/system_test.rs`)
- ✅ `test_get_system_metrics_returns_valid_data` - 验证系统指标有效性
- ✅ `test_get_system_metrics_structure` - 验证数据结构完整性
- ✅ `test_get_cpu_info_returns_valid_json` - 验证CPU信息JSON格式
- ✅ `test_get_cpu_info_cpu_details` - 验证CPU详细信息
- ✅ `test_get_memory_info_returns_valid_json` - 验证内存信息
- ✅ `test_get_disk_info_returns_valid_json` - 验证磁盘信息
- ✅ `test_get_disk_info_disk_details` - 验证磁盘详情
- ✅ `test_get_network_info_returns_valid_json` - 验证网络信息
- ✅ `test_get_network_info_interface_details` - 验证网络接口详情
- ✅ `test_system_metrics_timestamp_is_current` - 验证时间戳实时性
- ✅ `test_multiple_calls_consistency` - 验证多次调用一致性

#### 2. 数据库操作 (`db/repository.rs`)
- ✅ `test_repository_initialization` - 数据库初始化
- ✅ `test_insert_and_get_system_metrics` - 系统指标CRUD
- ✅ `test_insert_cpu_core` - CPU核心数据
- ✅ `test_insert_and_get_disk_metrics` - 磁盘指标CRUD
- ✅ `test_insert_and_get_network_metrics` - 网络指标CRUD
- ✅ `test_folder_scan_lifecycle` - 文件夹扫描生命周期
- ✅ `test_insert_folder_item` - 文件夹项目插入
- ✅ `test_insert_file_type_stat` - 文件类型统计
- ✅ `test_batch_insert_folder_items` - 批量插入优化
- ✅ `test_batch_insert_file_type_stats` - 批量统计插入
- ✅ `test_watched_folder_crud` - 监控文件夹CRUD
- ✅ `test_insert_and_get_folder_events` - 文件夹事件
- ✅ `test_insert_alert` - 告警记录

#### 3. 文件监听服务 (`services/file_watcher_service_test.rs`)
- ✅ `test_file_event_type_to_string` - 事件类型转换
- ✅ `test_file_change_event_creation` - 事件创建
- ✅ `test_file_change_event_with_none_size` - 可选字段处理
- ✅ `test_debounced_event_structure` - 防抖事件结构
- ✅ `test_debounced_event_elapsed` - 时间计算
- ✅ `test_event_aggregation_counts` - 事件聚合计数
- ✅ `test_sample_files_extraction` - 示例文件提取
- ✅ `test_sample_files_limit` - 示例数量限制
- ✅ `test_empty_events_handling` - 空事件处理
- ✅ `test_event_serialization` - JSON序列化
- ✅ `test_event_deserialization` - JSON反序列化

### P1: TypeScript 单元测试 ✅

#### 1. API层测试 (`services/folderAnalysisApi.test.ts`)
- ✅ `invokeSafe` - 安全调用封装
  - 成功调用
  - 错误处理
  - 日志记录
- ✅ `isUserCancelled` - 取消检测
  - 多种取消消息格式
  - 大小写不敏感
- ✅ `selectFolder` - 文件夹选择
- ✅ `scanFolder` - 文件夹扫描
  - 参数验证
  - 空路径检查
- ✅ `getFolderScans` - 获取扫描历史
- ✅ `deleteFolderScan` - 删除扫描记录
- ✅ `addWatchedFolder` - 添加监控文件夹
- ✅ `listWatchedFolders` - 列出监控文件夹
- ✅ `removeWatchedFolder` - 移除监控文件夹
- ✅ `toggleWatchedFolderActive` - 切换激活状态

#### 2. Store测试 (`stores/metricsStore.test.ts`)
- ✅ 初始状态验证
- ✅ `setCurrentMetrics` - 设置当前指标
- ✅ `addHistoricalMetric` - 添加历史记录
- ✅ `clearHistoricalMetrics` - 清空历史
- ✅ `setLoading` / `setError` - 状态管理
- ✅ `calculateStats` - 统计计算
- ✅ 状态转换场景
- ✅ 并发安全性

#### 3. Store测试 (`stores/scanStore.test.ts`)
- ✅ 路径管理
- ✅ 扫描控制流程
- ✅ 进度更新
- ✅ 错误处理
- ✅ 历史记录管理
- ✅ 持久化配置
- ✅ 完整扫描流程

### P2: 组件测试 ⏳

> 组件测试可以使用 React Testing Library 实现，由于项目已有E2E测试覆盖UI，此处为可选。

### P3: E2E 测试 ✅

#### 1. 核心功能测试 (`core-functionality.spec.ts`)
- ✅ Dashboard页面显示
- ✅ CPU使用率图表
- ✅ 内存使用情况
- ✅ 文件夹选择与扫描
- ✅ 扫描历史记录
- ✅ 添加监控文件夹
- ✅ 磁盘使用情况
- ✅ 实时数据更新
- ✅ 错误状态处理
- ✅ 响应式布局
- ✅ 主题切换
- ✅ 加载状态
- ✅ 状态持久化
- ✅ 网络错误处理
- ✅ 页面加载性能
- ✅ 图表渲染性能

#### 2. 性能测试 (`performance.spec.ts`)
- ✅ 数据库批量插入性能
- ✅ 图表渲染性能
- ✅ 内存使用监控
- ✅ API响应时间
- ✅ 页面滚动性能
- ✅ 并发操作性能
- ✅ 大数据集渲染
- ✅ 事件处理性能
- ✅ DOM操作性能

### P4: 性能测试 ✅

已在 `performance.spec.ts` 中实现 comprehensive 性能测试。

## 最佳实践

### 1. 测试隔离

```rust
// Rust: 每个测试使用独立的临时数据库
#[test]
fn test_database_operations() {
    let temp_dir = TempDir::new().unwrap();
    let db_path = temp_dir.path().join("test.db");
    let repo = DatabaseRepository::new(db_path.to_str().unwrap()).unwrap();
    // 测试逻辑...
}
```

```typescript
// TypeScript: 每个测试前重置状态
beforeEach(() => {
  useMetricsStore.setState({
    currentMetrics: null,
    historicalMetrics: [],
    loading: false,
    error: null,
    stats: null,
  });
});
```

### 2. Mock外部依赖

```typescript
// Mock Tauri API
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));
```

### 3. 清晰的错误消息

```rust
assert!(metric.cpu_usage >= 0.0, 
    "CPU usage should be non-negative, got: {}", metric.cpu_usage);
```

### 4. 快速执行

- 单元测试：< 1秒
- 集成测试：< 10秒
- E2E测试：< 60秒
- 性能测试：< 30秒

### 5. 测试命名规范

```
test_<功能>_<场景>_<期望结果>
例如：
- test_get_system_metrics_returns_valid_data
- test_scan_folder_with_empty_path_throws_error
```

## 故障排查

### 问题1: Rust测试失败 - 找不到tempfile

**解决方案：**
```bash
cd sys-monitor/src-tauri
cargo clean
cargo build
cargo test
```

### 问题2: TypeScript测试 - 类型错误

**解决方案：**
```bash
cd sys-monitor
pnpm install
pnpm exec tsc --noEmit
```

### 问题3: E2E测试 - 浏览器未安装

**解决方案：**
```bash
cd sys-monitor/tests/e2e
npx playwright install
```

### 问题4: 测试超时

**解决方案：**
```typescript
// 增加超时时间
test('slow test', async ({ page }) => {
  test.setTimeout(60000); // 60秒
  // 测试逻辑...
}, 60000);
```

### 问题5: 端口冲突

**解决方案：**
```bash
# 检查端口占用
netstat -ano | findstr :3000

# 杀死占用进程
taskkill /PID <PID> /F
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-rust:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
      - name: Run Rust tests
        run: |
          cd sys-monitor/src-tauri
          cargo test

  test-typescript:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd sys-monitor
          pnpm install
      - name: Run TypeScript tests
        run: |
          cd sys-monitor
          pnpm test

  test-e2e:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Playwright
        run: |
          cd sys-monitor/tests/e2e
          npx playwright install
      - name: Run E2E tests
        run: |
          cd sys-monitor/tests/e2e
          npx playwright test
```

## 覆盖率目标

| 测试类型 | 目标覆盖率 | 当前状态 |
|---------|----------|---------|
| Rust 单元测试 | > 80% | ✅ 已实现 |
| TypeScript 单元测试 | > 75% | ✅ 已实现 |
| E2E 测试 | 关键路径100% | ✅ 已实现 |
| 性能测试 | 核心场景覆盖 | ✅ 已实现 |

## 持续改进

1. **定期审查测试**：每月审查测试用例，删除过时测试
2. **监控测试性能**：跟踪测试执行时间，优化慢测试
3. **收集反馈**：从CI失败中改进测试质量
4. **文档更新**：保持测试文档与代码同步

## 参考资料

- [Rust Testing Book](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)

---

**最后更新**: 2026-04-16  
**维护者**: Sys-Monitor Team
