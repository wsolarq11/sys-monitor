# React Performance Optimization Skill

## 概述

本 Skill 封装了 Vercel Engineering 团队的 React/Next.js 性能优化最佳实践（57+ 条规则），帮助 Agent 编写高性能、可维护的 React 代码。

**适用场景**:
- React 组件性能优化
- 避免不必要的重渲染
- Bundle 大小优化
- 加载性能优化
- 代码审查和性能审计

## 核心原则

### 1. 最小化重渲染
- ✅ 使用 `React.memo()` 缓存组件
- ✅ 使用 `useMemo()` 缓存计算结果
- ✅ 使用 `useCallback()` 缓存回调函数
- ✅ 合理设计组件边界
- ❌ 避免在 JSX 中创建内联对象/函数
- ❌ 避免传递新的引用作为 props

### 2. 代码分割
- ✅ 使用 `React.lazy()` + `Suspense` 懒加载
- ✅ 按路由分割代码
- ✅ 按功能模块分割
- ✅ 预加载关键资源
- ❌ 避免一次性加载所有代码
- ❌ 避免过小的代码块（增加 HTTP 请求）

### 3. 数据获取优化
- ✅ 并行获取数据（`Promise.all`）
- ✅ 使用 SWR/React Query 缓存
- ✅ 实现乐观更新
- ✅ 预取用户可能访问的数据
- ❌ 避免请求瀑布（Waterfall）
- ❌ 避免重复请求相同数据

### 4. Bundle 优化
- ✅ Tree Shaking 移除未使用代码
- ✅ 使用动态导入减少初始包大小
- ✅ 分析 Bundle 组成（`webpack-bundle-analyzer`）
- ✅ 压缩和优化图片
- ❌ 避免引入大型库的单个函数
- ❌ 避免重复依赖

## 性能优化模式

### 1. 组件记忆化

#### React.memo
```tsx
// ✅ 推荐：记忆化组件
interface UserCardProps {
  user: User;
  onClick: (id: string) => void;
}

const UserCard = React.memo<UserCardProps>(({ user, onClick }) => {
  return (
    <div onClick={() => onClick(user.id)}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
});

// ✅ 自定义比较函数
const ExpensiveList = React.memo<ListProps>(
  ({ items }) => <ul>{items.map(item => <li key={item.id}>{item.name}</li>)}</ul>,
  (prevProps, nextProps) => {
    // 仅在 items 长度变化时重渲染
    return prevProps.items.length === nextProps.items.length;
  }
);

// ❌ 避免：不必要的记忆化
const SimpleText = React.memo(({ text }: { text: string }) => <span>{text}</span>);
// 简单组件不需要 memo，开销大于收益
```

#### useMemo
```tsx
// ✅ 缓存昂贵计算
const Dashboard = ({ transactions }: { transactions: Transaction[] }) => {
  // 昂贵的计算
  const totalAmount = useMemo(() => {
    return transactions.reduce((sum, t) => sum + t.amount, 0);
  }, [transactions]);  // 仅在 transactions 变化时重新计算
  
  const filteredTransactions = useMemo(() => {
    return transactions.filter(t => t.amount > 100);
  }, [transactions]);
  
  return (
    <div>
      <h2>Total: ${totalAmount}</h2>
      <TransactionList transactions={filteredTransactions} />
    </div>
  );
};

// ❌ 避免：缓存简单计算
const name = useMemo(() => `${firstName} ${lastName}`, [firstName, lastName]);
// 字符串拼接很快，不需要 useMemo
```

#### useCallback
```tsx
// ✅ 缓存回调函数
const UserList = () => {
  const [users, setUsers] = useState<User[]>([]);
  
  // 缓存回调，避免每次渲染创建新函数
  const handleDelete = useCallback((userId: string) => {
    setUsers(prev => prev.filter(u => u.id !== userId));
  }, []);
  
  const handleUpdate = useCallback((userId: string, data: Partial<User>) => {
    setUsers(prev => prev.map(u => u.id === userId ? { ...u, ...data } : u));
  }, []);
  
  return (
    <div>
      {users.map(user => (
        <UserCard
          key={user.id}
          user={user}
          onDelete={handleDelete}  // 引用稳定
          onUpdate={handleUpdate}  // 引用稳定
        />
      ))}
    </div>
  );
};

// ❌ 避免：内联箭头函数
{users.map(user => (
  <UserCard
    key={user.id}
    user={user}
    onDelete={() => handleDelete(user.id)}  // 每次渲染创建新函数
  />
))}
```

### 2. 代码分割

#### 路由级分割
```tsx
// ✅ Next.js App Router - 自动代码分割
// app/dashboard/page.tsx
export default function DashboardPage() {
  return <Dashboard />;
}

// app/settings/page.tsx
export default function SettingsPage() {
  return <Settings />;
}

// ✅ React.lazy + Suspense（SPA）
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

#### 组件级分割
```tsx
// ✅ 懒加载重型组件
import { lazy, Suspense } from 'react';

const ChartComponent = lazy(() => import('./ChartComponent'));

function AnalyticsDashboard() {
  const [showChart, setShowChart] = useState(false);
  
  return (
    <div>
      <button onClick={() => setShowChart(true)}>
        Show Chart
      </button>
      
      {showChart && (
        <Suspense fallback={<ChartSkeleton />}>
          <ChartComponent />
        </Suspense>
      )}
    </div>
  );
}

// ✅ 条件加载第三方库
async function loadPDFLib() {
  return import('pdf-lib');  // 仅在需要时加载
}

async function generatePDF() {
  const PDFLib = await loadPDFLib();
  // 使用 PDFLib...
}
```

### 3. 数据获取优化

#### 避免请求瀑布
```tsx
// ❌ 错误：请求瀑布（串行请求）
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  
  useEffect(() => {
    // 第一个请求
    fetchUser(userId).then(user => {
      setUser(user);
      // 第二个请求（等待第一个完成）
      fetchPosts(user.id).then(setPosts);
    });
  }, [userId]);
  
  return <div>...</div>;
}

// ✅ 正确：并行请求
function UserProfile({ userId }: { userId: string }) {
  const [data, setData] = useState<{ user: User; posts: Post[] } | null>(null);
  
  useEffect(() => {
    Promise.all([
      fetchUser(userId),
      fetchPosts(userId),  // 不等待 user 结果
    ]).then(([user, posts]) => {
      setData({ user, posts });
    });
  }, [userId]);
  
  return <div>...</div>;
}

// ✅ 最佳：使用 React Query / SWR
import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string }) {
  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });
  
  const { data: posts } = useQuery({
    queryKey: ['posts', userId],
    queryFn: () => fetchPosts(userId),
    enabled: !!user,  // 可选：依赖 user
  });
  
  return <div>...</div>;
}
```

#### 缓存和预取
```tsx
// ✅ 使用 SWR 自动缓存
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

function Dashboard() {
  const { data: stats } = useSWR('/api/stats', fetcher, {
    refreshInterval: 30000,  // 30秒刷新
    revalidateOnFocus: false,
  });
  
  const { data: users } = useSWR('/api/users', fetcher, {
    dedupingInterval: 5000,  // 5秒内去重
  });
  
  return <div>...</div>;
}

// ✅ 预取数据
import { prefetchQuery } from '@tanstack/react-query';

function UserList() {
  const queryClient = useQueryClient();
  
  const handleMouseEnter = (userId: string) => {
    // 鼠标悬停时预取用户详情
    prefetchQuery(queryClient, {
      queryKey: ['user', userId],
      queryFn: () => fetchUser(userId),
    });
  };
  
  return (
    <ul>
      {users.map(user => (
        <li
          key={user.id}
          onMouseEnter={() => handleMouseEnter(user.id)}
        >
          <Link to={`/users/${user.id}`}>{user.name}</Link>
        </li>
      ))}
    </ul>
  );
}
```

### 4. Bundle 优化

#### Tree Shaking
```tsx
// ✅ 正确：命名导入（支持 Tree Shaking）
import { Button, Input, Modal } from '@mui/material';

// ❌ 错误：默认导入（阻止 Tree Shaking）
import MUI from '@mui/material';
const { Button, Input, Modal } = MUI;

// ✅ 使用 lodash-es 而非 lodash
import { debounce } from 'lodash-es';  // 仅导入 debounce
// 而非
import _ from 'lodash';  // 导入整个库
```

#### 分析和优化
```bash
# 安装 Bundle 分析工具
npm install webpack-bundle-analyzer --save-dev

# package.json
{
  "scripts": {
    "analyze": "ANALYZE=true npm run build"
  }
}

# vite.config.ts
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true }),  // 自动生成报告
  ],
});
```

## 性能监控

### 1. React DevTools Profiler
```tsx
// 启用 Profiler
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number
) {
  console.log(`${id} took ${actualDuration}ms to render`);
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  );
}
```

### 2. Web Vitals
```tsx
// 安装 web-vitals
npm install web-vitals

// reportWebVitals.ts
import { ReportHandler } from 'web-vitals';

const reportWebVitals = (onPerfEntry?: ReportHandler) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;

// main.tsx
import reportWebVitals from './reportWebVitals';

reportWebVitals(metric => {
  console.log(metric);
  // 发送到分析服务
  sendToAnalytics(metric);
});
```

### 3. 性能预算
```json
// performance-budget.json
{
  "budgets": [
    {
      "resourceType": "script",
      "budget": 200000,  // 200KB
      "maxInitialLoad": 150000  // 首屏 150KB
    },
    {
      "resourceType": "image",
      "budget": 500000  // 500KB
    },
    {
      "metric": "first-contentful-paint",
      "budget": 1800  // 1.8秒
    },
    {
      "metric": "largest-contentful-paint",
      "budget": 2500  // 2.5秒
    }
  ]
}
```

## Tauri + React 特定优化

### 1. IPC 通信优化
```tsx
// ✅ 批量发送命令
async function updateMultipleFolders(updates: FolderUpdate[]) {
  // 一次性发送所有更新
  await invoke('batch_update_folders', { updates });
}

// ❌ 避免：逐个发送
for (const update of updates) {
  await invoke('update_folder', update);  // 多次 IPC 调用
}

// ✅ 使用事件监听替代轮询
import { listen } from '@tauri-apps/api/event';

useEffect(() => {
  const unlisten = listen<FolderEvent>('folder-changed', event => {
    // 处理文件夹变更
    updateFolder(event.payload);
  });
  
  return () => {
    unlisten.then(fn => fn());
  };
}, []);

// ❌ 避免：定时轮询
useEffect(() => {
  const interval = setInterval(async () => {
    const folders = await invoke('get_folders');  // 频繁 IPC 调用
    setFolders(folders);
  }, 1000);
  
  return () => clearInterval(interval);
}, []);
```

### 2. 状态同步
```tsx
// ✅ 使用 Zustand 管理全局状态
import { create } from 'zustand';

interface FolderStore {
  folders: Folder[];
  setFolders: (folders: Folder[]) => void;
  updateFolder: (id: string, data: Partial<Folder>) => void;
}

const useFolderStore = create<FolderStore>((set) => ({
  folders: [],
  setFolders: (folders) => set({ folders }),
  updateFolder: (id, data) => set(state => ({
    folders: state.folders.map(f => f.id === id ? { ...f, ...data } : f)
  })),
}));

// ✅ 从 Tauri 命令更新状态
async function loadFolders() {
  const folders = await invoke<Folder[]>('get_folders');
  useFolderStore.getState().setFolders(folders);
}
```

## 检查清单

### 开发时检查
```bash
# 启用 React Strict Mode（检测副作用）
<React.StrictMode>
  <App />
</React.StrictMode>

# 启用 ESLint React 插件
npm install eslint-plugin-react-hooks --save-dev

# .eslintrc.json
{
  "plugins": ["react-hooks"],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

### 构建时检查
```bash
# 生成生产构建并分析
npm run build
npm run analyze

# 检查 Bundle 大小
ls -lh dist/assets/*.js

# Lighthouse 审计
npx lighthouse http://localhost:3000 --view
```

### 运行时监控
- [ ] 监控 FCP（First Contentful Paint）< 1.8s
- [ ] 监控 LCP（Largest Contentful Paint）< 2.5s
- [ ] 监控 CLS（Cumulative Layout Shift）< 0.1
- [ ] 监控 FID（First Input Delay）< 100ms
- [ ] 监控 TTI（Time to Interactive）< 3.8s

## 工具和资源

### 开发工具
```bash
# React DevTools
# Chrome 扩展：https://chrome.google.com/webstore/detail/react-developer-tools

# Why Did You Render（检测不必要的重渲染）
npm install @welldone-software/why-did-you-render --save-dev

// wdyr.ts
import React from 'react';

if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = require('@welldone-software/why-did-you-render');
  whyDidYouRender(React, {
    trackAllPureComponents: true,
  });
}
```

### 性能测试
```bash
# Lighthouse CI
npm install -g @lhci/cli
lhci autorun

# WebPageTest
# https://www.webpagetest.org/

# BundlePhobia（检查包大小）
# https://bundlephobia.com/
```

### 学习资源
- [Vercel React Best Practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) - 官方来源
- [React Performance Documentation](https://react.dev/reference/react) - 官方文档
- [Web Vitals](https://web.dev/vitals/) - Google 性能指标
- [Patterns.dev](https://www.patterns.dev/) - React 性能模式

---

**最后更新**: 2026-04-15  
**版本**: v1.0.0  
**状态**: ✅ Active  
**来源**: Vercel Engineering vercel-react-best-practices (57+ rules)
