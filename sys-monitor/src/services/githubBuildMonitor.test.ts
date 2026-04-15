import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GitHubBuildMonitor } from './githubBuildMonitor';

// Mock fetch
const mockFetch = vi.fn();
(globalThis as any).fetch = mockFetch;

describe('GitHubBuildMonitor', () => {
  let monitor: GitHubBuildMonitor;

  beforeEach(() => {
    monitor = new GitHubBuildMonitor('test-owner', 'test-repo', 'test-token');
    vi.clearAllMocks();
  });

  describe('getRecentWorkflowRuns', () => {
    it('应该正确获取工作流运行列表', async () => {
      const mockResponse = {
        workflow_runs: [
          {
            id: 123,
            name: 'CI/CD Multi-Platform Tests',
            status: 'completed',
            conclusion: 'success',
            created_at: '2026-04-15T10:00:00Z',
            updated_at: '2026-04-15T10:05:00Z',
            run_number: 42,
            event: 'push',
            head_branch: 'main',
            head_sha: 'abc123',
            html_url: 'https://github.com/test-owner/test-repo/actions/runs/123',
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const runs = await monitor.getRecentWorkflowRuns(1);

      expect(runs).toHaveLength(1);
      expect(runs[0].id).toBe(123);
      expect(runs[0].status).toBe('completed');
      expect(runs[0].conclusion).toBe('success');
      expect(runs[0].duration_ms).toBe(300000); // 5分钟
    });

    it('应该在 API 错误时抛出异常', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
      });

      await expect(monitor.getRecentWorkflowRuns()).rejects.toThrow('GitHub API error: 403');
    });
  });

  describe('getBuildStatusSummary', () => {
    it('应该正确计算构建统计信息', async () => {
      const mockResponse = {
        workflow_runs: [
          {
            id: 1,
            name: 'CI',
            status: 'completed',
            conclusion: 'success',
            created_at: '2026-04-15T10:00:00Z',
            updated_at: '2026-04-15T10:05:00Z',
            run_number: 1,
            event: 'push',
            head_branch: 'main',
            head_sha: 'abc123',
            html_url: 'https://github.com/test-owner/test-repo/actions/runs/1',
          },
          {
            id: 2,
            name: 'CI',
            status: 'completed',
            conclusion: 'failure',
            created_at: '2026-04-15T09:00:00Z',
            updated_at: '2026-04-15T09:03:00Z',
            run_number: 2,
            event: 'push',
            head_branch: 'develop',
            head_sha: 'def456',
            html_url: 'https://github.com/test-owner/test-repo/actions/runs/2',
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const summary = await monitor.getBuildStatusSummary();

      expect(summary.totalRuns).toBe(2);
      expect(summary.successRate).toBe(50); // 1成功 / 2总计
      expect(summary.averageDuration).toBe(240000); // 平均4分钟
    });
  });

  describe('formatDuration', () => {
    it('应该正确格式化持续时间', () => {
      expect(GitHubBuildMonitor.formatDuration(1000)).toBe('1s');
      expect(GitHubBuildMonitor.formatDuration(60000)).toBe('1m 0s');
      expect(GitHubBuildMonitor.formatDuration(3600000)).toBe('1h 0m');
      expect(GitHubBuildMonitor.formatDuration(3661000)).toBe('1h 1m');
    });
  });

  describe('getStatusText', () => {
    it('应该返回正确的状态文本', () => {
      expect(GitHubBuildMonitor.getStatusText('completed', 'success')).toBe('✅ 成功');
      expect(GitHubBuildMonitor.getStatusText('completed', 'failure')).toBe('❌ 失败');
      expect(GitHubBuildMonitor.getStatusText('in_progress', null)).toBe('🔄 构建中');
      expect(GitHubBuildMonitor.getStatusText('queued', null)).toBe('⏳ 排队中');
    });
  });

  describe('getStatusColor', () => {
    it('应该返回正确的状态颜色', () => {
      expect(GitHubBuildMonitor.getStatusColor('completed', 'success')).toBe('#10b981');
      expect(GitHubBuildMonitor.getStatusColor('completed', 'failure')).toBe('#ef4444');
      expect(GitHubBuildMonitor.getStatusColor('in_progress', null)).toBe('#3b82f6');
    });
  });

  describe('triggerWorkflow', () => {
    it('应该能够触发工作流', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      });

      const result = await monitor.triggerWorkflow('ci.yml', 'main');

      expect(result).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/actions/workflows/ci.yml/dispatches'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ ref: 'main' }),
        })
      );
    });
  });
});
