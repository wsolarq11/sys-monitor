# 远程构建状态监控系统 - 完整指南

## 📚 目录

1. [系统概述](#系统概述)
2. [架构设计](#架构设计)
3. [核心功能](#核心功能)
4. [快速开始](#快速开始)
5. [深入理解](#深入理解)
6. [最佳实践](#最佳实践)
7. [故障排查](#故障排查)

---

## 系统概述

### 什么是远程构建状态监控？

远程构建状态监控是一个允许您在应用程序内实时查看和跟踪 CI/CD（持续集成/持续部署）构建状态的系统。它通过调用 GitHub API 获取工作流运行信息，并以可视化的方式展示给用户。

### 为什么需要这个功能？

**传统方式的痛点：**
- ❌ 需要切换到 GitHub 网站查看构建状态
- ❌ 无法在应用内直接了解构建进度
- ❌ 缺少实时的构建统计和分析
- ❌ 多项目时需要频繁切换页面

**本系统的优势：**
- ✅ 在应用内一站式查看所有构建状态
- ✅ 实时自动刷新，无需手动检查
- ✅ 提供构建成功率、平均时长等统计数据
- ✅ 支持多仓库监控
- ✅ 可自定义刷新频率和显示内容

---

## 架构设计

### 技术栈

- **前端框架**: React 18 + TypeScript
- **状态管理**: React Hooks (useState, useEffect)
- **HTTP 客户端**: Fetch API
- **样式**: Tailwind CSS
- **测试**: Vitest

### 文件结构

```
sys-monitor/src/
├── services/
│   ├── githubBuildMonitor.ts        # GitHub API 服务层
│   └── githubBuildMonitor.test.ts   # 单元测试
├── components/
│   └── BuildStatus/
│       ├── BuildStatusCard.tsx      # UI 组件
│       └── README.md                # 使用文档
└── examples/
    └── BuildStatusExample.tsx       # 使用示例
```

---

## 核心功能

### 1. 实时状态监控

系统每 60 秒（可配置）自动从 GitHub API 获取最新的构建状态。

### 2. 构建统计摘要

提供关键指标的可视化展示：
- **成功率**: 成功构建数 / 总构建数 × 100%
- **总构建数**: 最近 N 次构建的总数
- **平均时长**: 所有已完成构建的平均耗时
- **正在运行**: 当前正在执行或排队的构建数量

### 3. 构建历史列表

展示最近的构建记录，包括：
- 工作流名称和编号
- 构建状态（带颜色标识）
- 触发分支
- 构建时长
- 更新时间
- 链接到 GitHub 详情页

### 4. 状态可视化

| 状态 | 图标 | 颜色 | 说明 |
|------|------|------|------|
| 成功 | ✅ | 🟢 绿色 | 构建成功完成 |
| 失败 | ❌ | 🔴 红色 | 构建失败 |
| 构建中 | 🔄 | 🔵 蓝色 | 正在执行 |
| 排队中 | ⏳ | 🟡 黄色 | 等待执行 |
| 已取消 | ⚠️ | 🟠 橙色 | 被手动取消 |

---

## 快速开始

### 步骤 1: 获取 GitHub Token

1. 访问 [GitHub Personal Access Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - ✅ `repo` - 访问私有仓库
   - ✅ `workflow` - 管理工作流
4. 生成并复制 Token

### 步骤 2: 配置环境变量

创建 `.env` 文件（不要提交到 Git）：

```env
VITE_GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
VITE_GITHUB_OWNER=your-username
VITE_GITHUB_REPO=FolderSizeMonitor
```

### 步骤 3: 在应用中使用

```tsx
import BuildStatusCard from './components/BuildStatus/BuildStatusCard';

function App() {
  return (
    <BuildStatusCard 
      owner={import.meta.env.VITE_GITHUB_OWNER}
      repo={import.meta.env.VITE_GITHUB_REPO}
      token={import.meta.env.VITE_GITHUB_TOKEN}
      refreshInterval={60000}
    />
  );
}
```

### 步骤 4: 运行测试

```bash
cd sys-monitor
pnpm test githubBuildMonitor
```

---

## 深入理解

### GitHub API 端点

#### 1. 获取工作流运行列表

```
GET /repos/{owner}/{repo}/actions/runs
```

**请求参数：**
- `per_page`: 每页数量（默认 30，最大 100）
- `page`: 页码
- `branch`: 过滤分支
- `status`: 过滤状态（queued, in_progress, completed）

#### 2. 获取工作流日志

```
GET /repos/{owner}/{repo}/actions/runs/{run_id}/logs
```

#### 3. 触发工作流

```
POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches
```

**请求体：**
```json
{
  "ref": "main"
}
```

### API 速率限制

| 认证方式 | 限制 |
|---------|------|
| 未认证 | 60 次/小时 |
| Personal Access Token | 5,000 次/小时 |
| GitHub App | 15,000 次/小时 |

**建议：** 始终使用 Token 以避免速率限制。

### 数据流详解

```
用户打开应用
    ↓
BuildStatusCard 组件挂载
    ↓
创建 GitHubBuildMonitor 实例
    ↓
调用 getBuildStatusSummary()
    ↓
并行请求：
  - getRecentWorkflowRuns(20)  ← 获取统计用数据
  - getRecentWorkflowRuns(5)   ← 获取展示用数据
    ↓
GitHub API 返回原始数据
    ↓
数据转换和计算：
  - 计算成功率
  - 计算平均时长
  - 格式化时间
    ↓
更新 React 状态
    ↓
重新渲染 UI
    ↓
设置定时器，60秒后重复
```

### 性能优化

1. **并行请求**: 使用 `Promise.all` 同时获取多个数据
2. **缓存策略**: 可以添加本地缓存减少 API 调用
3. **防抖刷新**: 避免频繁的手动刷新
4. **懒加载**: 仅在需要时加载组件

---

## 最佳实践

### 1. 安全管理 Token

```tsx
// ❌ 错误：硬编码 Token
const token = "ghp_xxxxxxxxxxxx";

// ✅ 正确：使用环境变量
const token = import.meta.env.VITE_GITHUB_TOKEN;

// ✅ 更好：提供降级方案
const token = import.meta.env.VITE_GITHUB_TOKEN || undefined;
```

### 2. 错误处理

```tsx
try {
  const data = await monitor.getBuildStatusSummary();
  setSummary(data);
} catch (error) {
  if (error.message.includes('403')) {
    setError('API 速率限制，请稍后重试');
  } else if (error.message.includes('401')) {
    setError('认证失败，请检查 Token');
  } else {
    setError('未知错误');
  }
}
```

### 3. 合理的刷新频率

```tsx
// 开发环境：频繁刷新
const refreshInterval = import.meta.env.DEV ? 10000 : 60000;

// 生产环境：降低频率
const refreshInterval = 120000; // 2分钟
```

### 4. 条件渲染

```tsx
if (loading && !summary) {
  return <LoadingSkeleton />;
}

if (error) {
  return <ErrorMessage error={error} onRetry={fetchData} />;
}

return <BuildStatusCard ... />;
```

### 5. 内存泄漏防护

```tsx
useEffect(() => {
  let cancelled = false;
  
  const fetchData = async () => {
    const data = await monitor.getBuildStatusSummary();
    if (!cancelled) {
      setSummary(data);
    }
  };
  
  fetchData();
  const interval = setInterval(fetchData, 60000);
  
  return () => {
    cancelled = true;
    clearInterval(interval);
  };
}, []);
```

---

## 故障排查

### 问题 1: 403 Forbidden - API Rate Limit Exceeded

**症状：**
```
Error: GitHub API error: 403
```

**原因：**
- 未使用 Token，达到匿名限制（60次/小时）
- Token 无效或过期

**解决方案：**
```tsx
// 1. 确保使用 Token
const monitor = new GitHubBuildMonitor(owner, repo, token);

// 2. 检查 Token 有效性
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit

// 3. 增加刷新间隔
<BuildStatusCard refreshInterval={120000} />
```

### 问题 2: 401 Unauthorized

**症状：**
```
Error: GitHub API error: 401
```

**原因：**
- Token 格式错误
- Token 已撤销

**解决方案：**
```tsx
// 检查 Token 格式
console.log('Token:', token?.substring(0, 10) + '...');

// 重新生成 Token
// 访问: https://github.com/settings/tokens
```

### 问题 3: CORS 错误

**症状：**
浏览器控制台显示 CORS 相关错误

**解决方案：**
```tsx
// 1. 确保使用正确的 URL
const baseUrl = 'https://api.github.com'; // 不是 github.com

// 2. 检查网络请求详情
// 3. GitHub API 支持 CORS，检查其他可能的原因
```

### 问题 4: 数据显示不准确

**症状：**
- 成功率为 0%
- 构建数量为 0

**原因：**
- 仓库没有工作流运行记录
- API 返回数据格式变化

**解决方案：**
```tsx
// 1. 确认仓库有 GitHub Actions 工作流
// 2. 检查 API 响应
console.log('API Response:', data);

// 3. 验证工作流名称
const runs = await monitor.getWorkflowRunsByName('CI/CD Multi-Platform Tests');
console.log('CI Runs:', runs);
```

### 问题 5: 组件不刷新

**症状：**
- 数据一直显示旧值
- 手动刷新按钮无反应

**解决方案：**
```tsx
// 检查 useEffect 依赖
useEffect(() => {
  console.log('Setting up interval:', refreshInterval);
  fetchData();
  const interval = setInterval(fetchData, refreshInterval);
  return () => {
    console.log('Clearing interval');
    clearInterval(interval);
  };
}, [refreshInterval]); // 确保依赖正确
```

---

## 扩展功能

### 1. 添加构建通知

```typescript
// 当构建状态变化时发送浏览器通知
function sendBuildNotification(run: WorkflowRun) {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(`构建 ${run.name}`, {
      body: `状态: ${run.conclusion}`,
      icon: run.conclusion === 'success' ? '✅' : '❌'
    });
  }
}
```

### 2. 构建趋势图表

可以使用 Recharts 或其他图表库展示构建时长趋势、成功率趋势等。

### 3. Webhook 集成

除了轮询，还可以设置 GitHub Webhook 实现推送式更新：

```typescript
// 在服务器端接收 webhook
app.post('/webhook/github', (req, res) => {
  const event = req.headers['x-github-event'];
  const payload = req.body;
  
  if (event === 'workflow_run') {
    // 广播给所有连接的客户端
    io.emit('build-status-update', payload);
  }
  
  res.sendStatus(200);
});
```

---

## 总结

远程构建状态监控系统为您提供了：

✅ **实时监控** - 自动刷新，随时掌握构建状态  
✅ **数据统计** - 成功率、平均时长等关键指标  
✅ **可视化展示** - 直观的颜色和图标表示  
✅ **易于集成** - 简单的组件化设计  
✅ **可扩展性** - 支持自定义和扩展功能  

通过这个系统，您可以：
- 减少上下文切换，提高工作效率
- 及时发现构建问题，快速响应
- 了解构建趋势，优化 CI/CD 流程
- 在一个地方管理多个项目的构建状态

---

## 相关资源

- [GitHub Actions API 文档](https://docs.github.com/en/rest/actions)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub API 速率限制](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [React Hooks 文档](https://react.dev/reference/react)
- [TypeScript 官方文档](https://www.typescriptlang.org/)

---

## 更新日志

### v1.0.0 (2026-04-15)
- ✨ 初始版本发布
- ✅ 支持获取工作流运行状态
- ✅ 自动刷新功能
- ✅ 构建统计摘要
- ✅ 状态可视化展示
- ✅ 完整的单元测试
- ✅ 详细的使用文档
