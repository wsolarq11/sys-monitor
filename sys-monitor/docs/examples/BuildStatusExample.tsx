/**
 * 远程构建状态监控 - 使用示例
 * 
 * 此文件展示了如何在 SysMonitor 应用中集成 GitHub Actions 构建状态监控功能
 */

import React from 'react';
import BuildStatusCard from '../components/BuildStatus/BuildStatusCard';

// ==================== 示例 1: 基本用法 ====================
export function BasicExample() {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">远程构建状态监控</h2>
      <BuildStatusCard 
        owner="your-github-username"
        repo="FolderSizeMonitor"
      />
    </div>
  );
}

// ==================== 示例 2: 带认证令牌 ====================
export function AuthenticatedExample() {
  // 从环境变量获取 Token（推荐方式）
  const token = import.meta.env.VITE_GITHUB_TOKEN;
  
  return (
    <BuildStatusCard 
      owner="your-github-username"
      repo="FolderSizeMonitor"
      token={token}
      refreshInterval={30000} // 30秒刷新一次
    />
  );
}

// ==================== 示例 3: 在 Dashboard 中集成 ====================
export function DashboardWithBuildStatus() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
      {/* 其他监控卡片 */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4">系统监控</h3>
        {/* ... 其他监控内容 ... */}
      </div>
      
      {/* 构建状态卡片 */}
      <BuildStatusCard 
        owner="your-github-username"
        repo="FolderSizeMonitor"
        token={import.meta.env.VITE_GITHUB_TOKEN}
      />
    </div>
  );
}

// ==================== 示例 4: 多仓库监控 ====================
export function MultiRepoMonitor() {
  const repos = [
    { owner: 'org1', repo: 'project-a' },
    { owner: 'org1', repo: 'project-b' },
    { owner: 'org2', repo: 'project-c' },
  ];

  return (
    <div className="space-y-6 p-6">
      <h2 className="text-2xl font-bold text-white">多仓库构建状态</h2>
      {repos.map(({ owner, repo }) => (
        <BuildStatusCard 
          key={`${owner}/${repo}`}
          owner={owner}
          repo={repo}
          token={import.meta.env.VITE_GITHUB_TOKEN}
          refreshInterval={120000} // 2分钟刷新
        />
      ))}
    </div>
  );
}

// ==================== 示例 5: 自定义样式 ====================
export function CustomStyledExample() {
  return (
    <div className="custom-build-monitor">
      <BuildStatusCard 
        owner="your-github-username"
        repo="FolderSizeMonitor"
        token={import.meta.env.VITE_GITHUB_TOKEN}
      />
      
      <style>{`
        .custom-build-monitor {
          /* 自定义样式 */
        }
      `}</style>
    </div>
  );
}

// ==================== 配置说明 ====================
/*
 * 环境变量配置 (.env 文件):
 * 
 * VITE_GITHUB_TOKEN=ghp_your_personal_access_token
 * VITE_GITHUB_OWNER=your-username
 * VITE_GITHUB_REPO=FolderSizeMonitor
 * 
 * 注意:
 * 1. .env 文件不应提交到版本控制
 * 2. 使用 .env.example 提供模板
 * 3. Token 需要 repo 和 workflow 权限
 */

// ==================== 在 App.tsx 中集成 ====================
/*
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import BuildStatusCard from './components/BuildStatus/BuildStatusCard';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/build-status" element={
            <BuildStatusCard 
              owner={import.meta.env.VITE_GITHUB_OWNER}
              repo={import.meta.env.VITE_GITHUB_REPO}
              token={import.meta.env.VITE_GITHUB_TOKEN}
            />
          } />
        </Routes>
      </div>
    </Router>
  );
}
*/

// ==================== 高级用法：自定义 Hook ====================
/*
import { useState, useEffect } from 'react';
import { GitHubBuildMonitor } from '../services/githubBuildMonitor';

export function useBuildStatus(owner: string, repo: string, token?: string) {
  const [monitor] = useState(() => new GitHubBuildMonitor(owner, repo, token));
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const data = await monitor.getBuildStatusSummary();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 60000);
    return () => clearInterval(interval);
  }, [monitor]);

  return { status, loading, error, refresh: () => monitor.getBuildStatusSummary() };
}

// 使用自定义 Hook
function MyComponent() {
  const { status, loading, error } = useBuildStatus('owner', 'repo', token);
  
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  
  return (
    <div>
      <p>成功率: {status?.successRate}%</p>
      <p>正在运行: {status?.currentStatus.length}</p>
    </div>
  );
}
*/

export default BasicExample;
