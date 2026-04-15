# 远程构建状态监控功能

## 📋 功能概述

此功能允许您在 SysMonitor 应用内实时监控 GitHub Actions 的构建状态，无需离开应用即可查看 CI/CD 运行情况。

## ✨ 主要特性

- ✅ **实时状态监控** - 自动刷新构建状态（默认每60秒）
- 📊 **统计摘要** - 显示成功率、平均构建时长等关键指标
- 📝 **构建历史** - 查看最近的构建记录和详细信息
- 🔗 **快速链接** - 一键跳转到 GitHub Actions 详情页
- 🎨 **状态可视化** - 颜色编码的状态指示器

## 🚀 使用方法

### 1. 在应用中集成组件

```tsx
import BuildStatusCard from './components/BuildStatus/BuildStatusCard';

function App() {
  return (
    <div>
      {/* 基本用法 */}
      <BuildStatusCard 
        owner="your-username"
        repo="FolderSizeMonitor"
      />
      
      {/* 带认证令牌（推荐，避免API限制）*/}
      <BuildStatusCard 
        owner="your-username"
        repo="FolderSizeMonitor"
        token="ghp_your_personal_access_token"
        refreshInterval={30000} // 30秒刷新一次
      />
    </div>
  );
}
```

### 2. 获取 GitHub Personal Access Token

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择权限范围：
   - ✅ `repo` (完整仓库访问)
   - ✅ `workflow` (工作流访问)
4. 生成并复制令牌
5. **重要**: 妥善保管令牌，不要提交到代码库

### 3. 配置环境变量（推荐）

创建 `.env` 文件：

```env
VITE_GITHUB_TOKEN=ghp_your_personal_access_token
VITE_GITHUB_OWNER=your-username
VITE_GITHUB_REPO=FolderSizeMonitor
```

然后在组件中使用：

```tsx
<BuildStatusCard 
  owner={import.meta.env.VITE_GITHUB_OWNER}
  repo={import.meta.env.VITE_GITHUB_REPO}
  token={import.meta.env.VITE_GITHUB_TOKEN}
/>
```

## 📊 API 说明

### GitHubBuildMonitor 类

```typescript
const monitor = new GitHubBuildMonitor(owner, repo, token);

// 获取最近的工作流运行
const runs = await monitor.getRecentWorkflowRuns(10);

// 获取特定工作流的运行
const ciRuns = await monitor.getWorkflowRunsByName('CI/CD Multi-Platform Tests', 5);

// 获取构建状态摘要
const summary = await monitor.getBuildStatusSummary();

// 重新触发工作流
await monitor.triggerWorkflow('ci.yml', 'main');
```

### 数据类型

```typescript
interface WorkflowRun {
  id: number;
  name: string;
  status: 'queued' | 'in_progress' | 'completed' | 'waiting';
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null;
  created_at: string;
  updated_at: string;
  run_number: number;
  event: 'push' | 'pull_request' | 'schedule';
  branch: string;
  commit_sha: string;
  html_url: string;
  duration_ms?: number;
}

interface BuildStatusSummary {
  totalRuns: number;
  successRate: number;      // 成功率百分比
  averageDuration: number;  // 平均时长（毫秒）
  lastBuildTime: string;
  currentStatus: WorkflowRun[]; // 正在运行的构建
}
```

## ⚙️ 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `owner` | string | - | GitHub 用户名或组织名 |
| `repo` | string | - | 仓库名称 |
| `token` | string | undefined | GitHub Personal Access Token（可选） |
| `refreshInterval` | number | 60000 | 自动刷新间隔（毫秒） |

## 🔒 安全注意事项

1. **不要硬编码 Token**
   ```tsx
   // ❌ 错误做法
   const token = "ghp_xxxxxxxxxxxx";
   
   // ✅ 正确做法
   const token = import.meta.env.VITE_GITHUB_TOKEN;
   ```

2. **使用环境变量文件**
   - 将 `.env` 添加到 `.gitignore`
   - 使用 `.env.example` 提供模板

3. **Token 权限最小化**
   - 只授予必要的权限
   - 定期轮换 Token

## 🐛 故障排除

### 问题 1: API 速率限制

**症状**: 收到 403 错误，提示速率限制

**解决方案**:
- 使用 Personal Access Token 可提高限制（从 60次/小时 到 5000次/小时）
- 增加 `refreshInterval` 减少请求频率

### 问题 2: 跨域错误

**症状**: CORS 错误

**解决方案**:
- GitHub API 支持 CORS，检查网络请求
- 确保使用正确的 API URL: `https://api.github.com`

### 问题 3: 认证失败

**症状**: 401 Unauthorized

**解决方案**:
- 检查 Token 是否有效
- 确认 Token 未过期
- 验证 Token 权限范围

## 📈 高级用法

### 自定义构建监控面板

```tsx
import { GitHubBuildMonitor } from '../../services/githubBuildMonitor';

function CustomBuildDashboard() {
  const [monitor] = useState(() => 
    new GitHubBuildMonitor('owner', 'repo', token)
  );
  
  const [ciStatus, setCiStatus] = useState(null);
  const [releaseStatus, setReleaseStatus] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      const [ci, release] = await Promise.all([
        monitor.getWorkflowRunsByName('CI/CD Multi-Platform Tests'),
        monitor.getWorkflowRunsByName('Release Build & Publish')
      ]);
      
      setCiStatus(ci[0]);
      setReleaseStatus(release[0]);
    };
    
    fetchStatus();
    const interval = setInterval(fetchStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>CI 状态: {ciStatus?.status}</h2>
      <h2>发布状态: {releaseStatus?.status}</h2>
    </div>
  );
}
```

### 构建通知集成

```typescript
// 当构建状态变化时发送通知
async function monitorBuildChanges() {
  let lastStatus = null;
  
  setInterval(async () => {
    const runs = await monitor.getRecentWorkflowRuns(1);
    const currentStatus = runs[0];
    
    if (lastStatus && currentStatus.status !== lastStatus.status) {
      // 状态发生变化，发送通知
      sendNotification({
        title: `构建 ${currentStatus.name}`,
        message: `状态: ${currentStatus.status}`,
        type: currentStatus.conclusion === 'success' ? 'success' : 'error'
      });
    }
    
    lastStatus = currentStatus;
  }, 30000);
}
```

## 🔗 相关资源

- [GitHub Actions API 文档](https://docs.github.com/en/rest/actions)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub API 速率限制](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)

## 📝 更新日志

### v1.0.0 (2026-04-15)
- ✨ 初始版本发布
- ✅ 支持获取工作流运行状态
- ✅ 自动刷新功能
- ✅ 构建统计摘要
- ✅ 状态可视化展示
