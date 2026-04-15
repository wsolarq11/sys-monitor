# 远程构建状态监控系统 - 架构详解

## 🏗️ 系统架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                     SysMonitor 应用                           │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              React 前端层                               │  │
│  │                                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │        BuildStatusCard.tsx (UI 组件)              │  │  │
│  │  │                                                    │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐               │  │  │
│  │  │  │ 统计摘要卡片  │  │ 构建历史列表  │               │  │  │
│  │  │  │ - 成功率     │  │ - 工作流名称  │               │  │  │
│  │  │  │ - 总构建数   │  │ - 状态指示器  │               │  │  │
│  │  │  │ - 平均时长   │  │ - 分支信息    │               │  │  │
│  │  │  │ - 正在运行   │  │ - 构建时长    │               │  │  │
│  │  │  └─────────────┘  └─────────────┘               │  │  │
│  │  │                                                    │  │  │
│  │  │  ┌──────────────────────────────────────────────┐│  │  │
│  │  │  │         自动刷新机制 (useEffect)               ││  │  │
│  │  │  │  setInterval(fetchData, refreshInterval)      ││  │  │
│  │  │  └──────────────────────────────────────────────┘│  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                        ↓ 调用                           │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │     GitHubBuildMonitor (服务层/业务逻辑)          │  │  │
│  │  │                                                    │  │  │
│  │  │  • getRecentWorkflowRuns()                        │  │  │
│  │  │  • getBuildStatusSummary()                        │  │  │
│  │  │  • getWorkflowRunLogs()                           │  │  │
│  │  │  • triggerWorkflow()                              │  │  │
│  │  │                                                    │  │  │
│  │  │  • calculateDuration()                            │  │  │
│  │  │  • formatDuration()                               │  │  │
│  │  │  • getStatusText()                                │  │  │
│  │  │  • getStatusColor()                               │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS / REST API
                           │ Authorization: token xxx
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                    GitHub API                                 │
│                 api.github.com                                │
│                                                               │
│  GET  /repos/{owner}/{repo}/actions/runs                     │
│  GET  /repos/{owner}/{repo}/actions/runs/{id}/logs           │
│  POST /repos/{owner}/{repo}/actions/workflows/{id}/dispatches│
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                  GitHub Actions                               │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Workflow #1 │  │ Workflow #2 │  │ Workflow #3 │  ...    │
│  │  (CI/CD)    │  │  (Release)  │  │  (Deploy)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 组件层次结构

```
App
└── Dashboard (或其他父组件)
    └── BuildStatusCard
        ├── Header Section
        │   ├── Title ("远程构建状态")
        │   └── Refresh Button
        │
        ├── Statistics Summary (Grid Layout)
        │   ├── Success Rate Card
        │   ├── Total Builds Card
        │   ├── Average Duration Card
        │   └── Running Builds Card
        │
        ├── Recent Builds List
        │   └── Build Item (repeated)
        │       ├── Status Indicator (colored dot)
        │       ├── Build Name & Number
        │       ├── Update Time
        │       ├── Status Text
        │       ├── Branch Info
        │       ├── Duration
        │       └── Detail Link
        │
        └── Footer
            └── Last Update Time
```

---

## 🔄 数据流图

```
用户操作 / 定时器触发
        │
        ▼
┌─────────────────┐
│  fetchData()    │
│  (组件方法)      │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌────────────────┐  ┌──────────────────┐
│ getBuildStatus │  │getRecentWorkflow │
│   Summary()    │  │    Runs(5)       │
│                │  │                  │
│ 请求 20 条记录  │  │ 请求 5 条记录     │
└────────┬───────┘  └────────┬─────────┘
         │                   │
         │                   │
         ▼                   ▼
┌─────────────────────────────────┐
│   GitHub API (并行请求)          │
│   fetch('/repos/.../runs')      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   原始 JSON 响应                 │
│   { workflow_runs: [...] }      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   数据转换和处理                  │
│                                 │
│   • 计算成功率                   │
│   • 计算平均时长                 │
│   • 格式化时间                   │
│   • 映射状态文本和颜色            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   更新 React State               │
│   setSummary(summaryData)       │
│   setRecentRuns(runsData)       │
│   setLastUpdate(new Date())     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   React 重新渲染 UI              │
│   显示最新数据                   │
└─────────────────────────────────┘
```

---

## 🎯 类和方法关系图

```
GitHubBuildMonitor Class
│
├── Constructor
│   └── new GitHubBuildMonitor(owner, repo, token)
│
├── Public Methods (API)
│   ├── getRecentWorkflowRuns(limit)
│   │   └── → Promise<WorkflowRun[]>
│   │
│   ├── getWorkflowRunsByName(name, limit)
│   │   └── → Promise<WorkflowRun[]>
│   │
│   ├── getBuildStatusSummary()
│   │   └── → Promise<BuildStatusSummary>
│   │       ├── totalRuns
│   │       ├── successRate
│   │       ├── averageDuration
│   │       ├── lastBuildTime
│   │       └── currentStatus
│   │
│   ├── getWorkflowRunLogs(runId)
│   │   └── → Promise<string>
│   │
│   └── triggerWorkflow(workflowId, branch)
│       └── → Promise<boolean>
│
├── Private Methods
│   ├── calculateDuration(startTime, endTime)
│   │   └── → number (milliseconds)
│   │
│   └── getHeaders()
│       └── → HeadersInit
│
└── Static Utility Methods
    ├── formatDuration(ms)
    │   └── → string (e.g., "5m 23s")
    │
    ├── getStatusText(status, conclusion)
    │   └── → string (e.g., "✅ 成功")
    │
    └── getStatusColor(status, conclusion)
        └── → string (e.g., "#10b981")
```

---

## 🔐 认证流程图

```
┌──────────────┐
│  用户配置     │
│  Token       │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ 传入到组件        │
│ <BuildStatusCard │
│   token={token}  │
│ />               │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 创建 Monitor 实例 │
│ new GitHubBuild  │
│ Monitor(...,     │
│   token)         │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 设置请求头        │
│ Authorization:   │
│ token xxx        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ GitHub API 验证   │
│                  │
│ ✅ 有效 → 返回数据│
│ ❌ 无效 → 401    │
│ ⚠️  超限 → 403   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 组件处理响应      │
│                  │
│ 成功 → 显示数据   │
│ 失败 → 显示错误   │
└──────────────────┘
```

---

## ⏱️ 生命周期时序图

```
时间轴 ─────────────────────────────────────────────────────→

T0: 组件挂载
    │
    ├─ useState 初始化
    │   ├─ monitor = new GitHubBuildMonitor(...)
    │   ├─ summary = null
    │   ├─ recentRuns = []
    │   ├─ loading = true
    │   └─ error = null
    │
    ├─ useEffect 执行
    │   ├─ 立即调用 fetchData()
    │   │   ├─ setLoading(true)
    │   │   ├─ 并行请求 API
    │   │   ├─ 等待响应...
    │   │   ├─ 处理数据
    │   │   ├─ setState(...)
    │   │   └─ setLoading(false)
    │   │
    │   └─ 设置定时器
    │       └─ interval = setInterval(fetchData, 60000)
    │
T0+60s: 第一次自动刷新
    │   ├─ fetchData() 再次调用
    │   └─ 更新数据
    │
T0+120s: 第二次自动刷新
    │   ├─ fetchData() 再次调用
    │   └─ 更新数据
    │
    ... (持续每 60 秒刷新)
    │
Tn: 用户点击刷新按钮
    │   └─ 立即调用 fetchData()
    │
Tn+60s: 继续自动刷新
    │
    ... 
    │
组件卸载:
    └─ useEffect cleanup
        └─ clearInterval(interval)
```

---

## 🎨 UI 状态机

```
                    ┌─────────────┐
                    │  Initial    │
                    │  State      │
                    └──────┬──────┘
                           │
                           │ 组件挂载
                           ▼
                    ┌─────────────┐
              ┌────▶│  Loading    │◀─────┐
              │     │  State      │      │
              │     └──────┬──────┘      │
              │            │             │
              │            │ 请求 API     │
              │            ▼             │
              │     ┌─────────────┐      │
              │     │  Fetching   │      │
              │     │  Data       │      │
              │     └──────┬──────┘      │
              │            │             │
              │      ┌─────┴─────┐       │
              │      │           │       │
              │      ▼           ▼       │
              │ ┌────────┐ ┌────────┐   │
              │ │Success │ │ Error  │   │
              │ │ State  │ │ State  │   │
              │ └────┬───┘ └───┬────┘   │
              │      │         │         │
              │      │         │ 重试    │
              │      │         └─────────┘
              │      │
              │      │ 60秒后自动刷新
              └──────┘
```

---

## 📊 数据结构关系

```
WorkflowRun (单个构建记录)
├── id: number
├── name: string
├── status: enum
├── conclusion: enum | null
├── created_at: ISO string
├── updated_at: ISO string
├── run_number: number
├── event: enum
├── branch: string
├── commit_sha: string
├── html_url: string
└── duration_ms: number (计算得出)

BuildStatusSummary (统计摘要)
├── totalRuns: number
├── successRate: number (百分比)
├── averageDuration: number (毫秒)
├── lastBuildTime: ISO string
└── currentStatus: WorkflowRun[] (正在运行的构建)

BuildStatusCard Props
├── owner: string (required)
├── repo: string (required)
├── token?: string (optional)
└── refreshInterval?: number (optional, default: 60000)
```

---

## 🔧 依赖关系图

```
BuildStatusCard.tsx
│
├── React (useState, useEffect)
│
├── GitHubBuildMonitor (service)
│   ├── Fetch API (browser)
│   └── TypeScript Interfaces
│
├── Tailwind CSS (styling)
│   ├── Grid layout
│   ├── Color utilities
│   └── Responsive classes
│
└── Environment Variables
    └── import.meta.env.VITE_*

githubBuildMonitor.test.ts
│
├── Vitest (test framework)
│   ├── describe, it, expect
│   └── vi.fn() for mocking
│
├── GitHubBuildMonitor (tested module)
│
└── Mock Fetch Implementation
```

---

## 🌐 网络请求流程

```
Browser                          GitHub API
    │                                  │
    │  GET /repos/owner/repo/          │
    │  actions/runs?per_page=20        │
    │  Headers:                        │
    │  - Accept: application/json      │
    │  - Authorization: token xxx      │
    │─────────────────────────────────>│
    │                                  │
    │                                  │ 验证 Token
    │                                  │ 查询数据库
    │                                  │ 构建响应
    │                                  │
    │  HTTP 200 OK                     │
    │  {                               │
    │    "workflow_runs": [            │
    │      {                           │
    │        "id": 123,                │
    │        "status": "completed",    │
    │        "conclusion": "success",  │
    │        ...                       │
    │      }                           │
    │    ]                             │
    │  }                               │
    │<─────────────────────────────────│
    │                                  │
    │ 解析 JSON                         │
    │ 转换数据                          │
    │ 更新 UI                          │
    │                                  │
```

---

## 🛡️ 错误处理流程

```
API 调用
    │
    ├─ 网络错误
    │   └─ catch (error)
    │       └─ setError("网络错误")
    │           └─ 显示错误 UI
    │               └─ 提供"重试"按钮
    │
    ├─ HTTP 401 (未授权)
    │   └─ setError("认证失败，请检查 Token")
    │       └─ 显示错误 UI
    │
    ├─ HTTP 403 (速率限制)
    │   └─ setError("API 速率限制，请稍后重试")
    │       └─ 显示错误 UI
    │
    ├─ HTTP 404 (未找到)
    │   └─ setError("仓库或工作流不存在")
    │       └─ 显示错误 UI
    │
    └─ 其他错误
        └─ setError(error.message)
            └─ 显示错误 UI
```

---

## 📈 性能优化策略

```
┌────────────────────────────────────────┐
│         性能优化措施                    │
├────────────────────────────────────────┤
│                                        │
│  1. 并行请求                           │
│     Promise.all([                      │
│       getSummary(),                    │
│       getRuns()                        │
│     ])                                 │
│     ↓ 减少 50% 等待时间                │
│                                        │
│  2. 合理的刷新频率                     │
│     默认 60 秒                         │
│     可配置 30-300 秒                   │
│     ↓ 平衡实时性和 API 使用量           │
│                                        │
│  3. 条件渲染                           │
│     loading && !summary → Skeleton    │
│     error → Error Message             │
│     else → Normal UI                  │
│     ↓ 避免不必要的渲染                 │
│                                        │
│  4. 内存管理                           │
│     useEffect cleanup                  │
│     clearInterval on unmount           │
│     ↓ 防止内存泄漏                     │
│                                        │
│  5. 懒加载 (未来)                      │
│     按需加载组件                       │
│     ↓ 减少初始包大小                   │
│                                        │
└────────────────────────────────────────┘
```

---

## 🎯 关键设计决策

### 1. 为什么选择轮询而非 WebSocket？

**决策**: 使用定时轮询（setInterval）

**原因**:
- ✅ 实现简单，无需额外服务器
- ✅ GitHub API 原生支持 REST
- ✅ 对于 60 秒刷新频率足够
- ❌ WebSocket 需要自建中转服务器
- ❌ 增加系统复杂度

**权衡**: 实时性稍差，但实现成本低

### 2. 为什么将服务层和 UI 层分离？

**决策**: GitHubBuildMonitor (服务) + BuildStatusCard (UI)

**原因**:
- ✅ 关注点分离
- ✅ 易于测试（可单独测试服务层）
- ✅ 可复用（服务层可用于其他组件）
- ✅ 易于维护

### 3. 为什么使用环境变量而非配置文件？

**决策**: 使用 `.env` 文件

**原因**:
- ✅ Vite 原生支持
- ✅ 不会提交到 Git（配合 .gitignore）
- ✅ 不同环境不同配置
- ✅ 构建时注入，运行时不可变

---

## 📝 总结

这个架构设计遵循了以下原则：

1. **单一职责**: 每个模块只做一件事
2. **分层清晰**: UI 层、服务层、API 层分离
3. **类型安全**: 完整的 TypeScript 类型定义
4. **错误容忍**: 完善的错误处理机制
5. **性能优先**: 并行请求、合理刷新、内存管理
6. **可扩展性**: 易于添加新功能和集成其他平台

这种架构使得系统既**易于理解**，又**易于维护和扩展**。
