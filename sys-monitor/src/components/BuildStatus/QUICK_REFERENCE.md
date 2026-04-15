# 远程构建状态监控 - 快速参考

## 🚀 5分钟快速上手

### 1️⃣ 获取 Token（2分钟）
```
访问: https://github.com/settings/tokens
权限: repo + workflow
复制生成的 Token
```

### 2️⃣ 配置环境（1分钟）
创建 `.env` 文件：
```env
VITE_GITHUB_TOKEN=ghp_xxxxxxxxxxxx
VITE_GITHUB_OWNER=your-username
VITE_GITHUB_REPO=FolderSizeMonitor
```

### 3️⃣ 集成组件（2分钟）
```tsx
import BuildStatusCard from './components/BuildStatus/BuildStatusCard';

<BuildStatusCard 
  owner={import.meta.env.VITE_GITHUB_OWNER}
  repo={import.meta.env.VITE_GITHUB_REPO}
  token={import.meta.env.VITE_GITHUB_TOKEN}
/>
```

---

## 📖 API 速查

### GitHubBuildMonitor 类

```typescript
// 创建实例
const monitor = new GitHubBuildMonitor(owner, repo, token);

// 获取最近的工作流运行
const runs = await monitor.getRecentWorkflowRuns(10);

// 获取特定工作流
const ciRuns = await monitor.getWorkflowRunsByName('CI/CD Tests', 5);

// 获取统计摘要
const summary = await monitor.getBuildStatusSummary();

// 触发工作流
await monitor.triggerWorkflow('ci.yml', 'main');
```

### 工具方法

```typescript
// 格式化时长
GitHubBuildMonitor.formatDuration(300000) // "5m 0s"

// 获取状态文本
GitHubBuildMonitor.getStatusText('completed', 'success') // "✅ 成功"

// 获取状态颜色
GitHubBuildMonitor.getStatusColor('completed', 'success') // "#10b981"
```

---

## 🔧 常用配置

### 刷新频率
```tsx
// 开发环境：10秒
refreshInterval={10000}

// 生产环境：60秒（默认）
refreshInterval={60000}

// 低频监控：5分钟
refreshInterval={300000}
```

### 多仓库监控
```tsx
const repos = [
  { owner: 'org', repo: 'project-a' },
  { owner: 'org', repo: 'project-b' },
];

{repos.map(({ owner, repo }) => (
  <BuildStatusCard 
    key={`${owner}/${repo}`}
    owner={owner}
    repo={repo}
    token={token}
  />
))}
```

---

## ⚠️ 常见问题速解

### ❌ 403 错误
```bash
# 检查速率限制
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit

# 解决方案：使用 Token 或增加刷新间隔
```

### ❌ 401 错误
```bash
# Token 无效，重新生成
# 访问: https://github.com/settings/tokens
```

### ❌ 数据为空
```tsx
// 确认仓库有 Actions 工作流
// 检查工作流名称是否匹配
const runs = await monitor.getWorkflowRunsByName('准确的工作流名称');
```

---

## 🎨 自定义样式

### 修改卡片样式
```tsx
<div className="custom-wrapper">
  <BuildStatusCard ... />
</div>

<style>{`
  .custom-wrapper .bg-gray-800 {
    background: linear-gradient(...);
  }
`}</style>
```

### 自定义状态颜色
```typescript
// 在 githubBuildMonitor.ts 中修改
static getStatusColor(status, conclusion) {
  if (conclusion === 'success') return '#你的颜色';
  // ...
}
```

---

## 📊 关键指标说明

| 指标 | 计算公式 | 说明 |
|------|---------|------|
| 成功率 | 成功数 / 完成数 × 100% | 越高越好 |
| 平均时长 | 总时长 / 完成数 | 反映构建效率 |
| 正在运行 | status != 'completed' | 当前活跃构建 |
| 总构建数 | 请求的 runs 数量 | 样本大小 |

---

## 🔍 调试技巧

### 查看 API 响应
```typescript
const runs = await monitor.getRecentWorkflowRuns(1);
console.log('Raw API Response:', runs);
```

### 检查网络请求
```
浏览器 DevTools → Network → 过滤 "api.github.com"
```

### 验证 Token 权限
```bash
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user
```

---

## 💡 最佳实践清单

- [ ] 使用环境变量存储 Token
- [ ] 将 `.env` 加入 `.gitignore`
- [ ] 设置合理的刷新频率
- [ ] 添加错误处理和重试机制
- [ ] 定期检查 Token 有效性
- [ ] 监控 API 使用量
- [ ] 编写单元测试

---

## 📚 相关文件

```
sys-monitor/src/
├── services/
│   ├── githubBuildMonitor.ts        # 核心服务
│   └── githubBuildMonitor.test.ts   # 测试文件
├── components/
│   └── BuildStatus/
│       ├── BuildStatusCard.tsx      # UI 组件
│       └── README.md                # 详细文档
└── examples/
    └── BuildStatusExample.tsx       # 使用示例
```

---

## 🔗 有用链接

- [完整文档](./BUILD_MONITOR_GUIDE.md)
- [GitHub Actions API](https://docs.github.com/en/rest/actions)
- [Token 管理](https://github.com/settings/tokens)
- [API 速率限制](https://docs.github.com/en/rest/overview/rate-limits)

---

**提示**: 将此文件加入书签，方便随时查阅！
