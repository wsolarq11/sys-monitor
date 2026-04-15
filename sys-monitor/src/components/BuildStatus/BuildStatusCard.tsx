import React, { useState, useEffect } from 'react';
import { GitHubBuildMonitor, WorkflowRun, BuildStatusSummary } from '../../services/githubBuildMonitor';

interface BuildStatusCardProps {
  owner?: string;
  repo?: string;
  token?: string;
  refreshInterval?: number; // 毫秒，默认 60000 (1分钟)
}

const BuildStatusCard: React.FC<BuildStatusCardProps> = ({
  owner = 'your-username',
  repo = 'FolderSizeMonitor',
  token,
  refreshInterval = 60000,
}) => {
  const [monitor] = useState(() => new GitHubBuildMonitor(owner, repo, token));
  const [summary, setSummary] = useState<BuildStatusSummary | null>(null);
  const [recentRuns, setRecentRuns] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [summaryData, runsData] = await Promise.all([
        monitor.getBuildStatusSummary(),
        monitor.getRecentWorkflowRuns(5),
      ]);

      setSummary(summaryData);
      setRecentRuns(runsData);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取构建状态失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // 设置定时刷新
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  if (loading && !summary) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-700 rounded w-1/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
        <h3 className="text-red-400 font-semibold mb-2">❌ 加载失败</h3>
        <p className="text-red-300 text-sm">{error}</p>
        <button
          onClick={fetchData}
          className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
        >
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg space-y-6">
      {/* 标题 */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="text-2xl">🔨</span>
          远程构建状态
        </h3>
        <button
          onClick={fetchData}
          disabled={loading}
          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white text-sm rounded transition-colors"
        >
          {loading ? '刷新中...' : '🔄 刷新'}
        </button>
      </div>

      {/* 统计摘要 */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-gray-400 text-xs mb-1">成功率</div>
            <div className="text-2xl font-bold text-green-400">
              {summary.successRate.toFixed(1)}%
            </div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-gray-400 text-xs mb-1">总构建数</div>
            <div className="text-2xl font-bold text-blue-400">
              {summary.totalRuns}
            </div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-gray-400 text-xs mb-1">平均时长</div>
            <div className="text-2xl font-bold text-yellow-400">
              {GitHubBuildMonitor.formatDuration(summary.averageDuration)}
            </div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-gray-400 text-xs mb-1">正在运行</div>
            <div className="text-2xl font-bold text-purple-400">
              {summary.currentStatus.length}
            </div>
          </div>
        </div>
      )}

      {/* 最近构建列表 */}
      <div>
        <h4 className="text-sm font-semibold text-gray-300 mb-3">最近构建</h4>
        <div className="space-y-2">
          {recentRuns.map((run) => (
            <div
              key={run.id}
              className="bg-gray-700/30 rounded-lg p-3 hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{
                      backgroundColor: GitHubBuildMonitor.getStatusColor(
                        run.status,
                        run.conclusion
                      ),
                    }}
                  ></span>
                  <span className="text-white font-medium text-sm">
                    {run.name} #{run.run_number}
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(run.updated_at).toLocaleString('zh-CN')}
                </span>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-3">
                  <span className="text-gray-400">
                    {GitHubBuildMonitor.getStatusText(run.status, run.conclusion)}
                  </span>
                  <span className="text-gray-500">|</span>
                  <span className="text-gray-400">分支: {run.branch}</span>
                  <span className="text-gray-500">|</span>
                  <span className="text-gray-400">
                    {run.duration_ms ? GitHubBuildMonitor.formatDuration(run.duration_ms) : '进行中'}
                  </span>
                </div>
                <a
                  href={run.html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 underline"
                >
                  查看详情 →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 最后更新时间 */}
      <div className="text-xs text-gray-500 text-right">
        最后更新: {lastUpdate.toLocaleTimeString('zh-CN')}
      </div>
    </div>
  );
};

export default BuildStatusCard;
