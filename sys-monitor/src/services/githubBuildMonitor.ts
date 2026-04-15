/**
 * GitHub Actions 构建状态监控服务
 * 用于获取和监控远程 CI/CD 构建状态
 */

export interface WorkflowRun {
  id: number;
  name: string;
  status: 'queued' | 'in_progress' | 'completed' | 'waiting' | 'requested' | 'pending';
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | 'neutral' | 'timed_out' | 'action_required' | null;
  created_at: string;
  updated_at: string;
  run_number: number;
  event: 'push' | 'pull_request' | 'schedule' | 'workflow_dispatch';
  branch: string;
  commit_sha: string;
  html_url: string;
  duration_ms?: number;
}

export interface BuildStatusSummary {
  totalRuns: number;
  successRate: number;
  averageDuration: number;
  lastBuildTime: string;
  currentStatus: WorkflowRun[];
}

export class GitHubBuildMonitor {
  private owner: string;
  private repo: string;
  private token?: string;
  private baseUrl: string = 'https://api.github.com';

  constructor(owner: string, repo: string, token?: string) {
    this.owner = owner;
    this.repo = repo;
    this.token = token;
  }

  /**
   * 获取最近的工作流运行记录
   */
  async getRecentWorkflowRuns(limit: number = 10): Promise<WorkflowRun[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/repos/${this.owner}/${this.repo}/actions/runs?per_page=${limit}`,
        {
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`GitHub API error: ${response.status}`);
      }

      const data = await response.json();
      return data.workflow_runs.map((run: any) => ({
        id: run.id,
        name: run.name,
        status: run.status,
        conclusion: run.conclusion,
        created_at: run.created_at,
        updated_at: run.updated_at,
        run_number: run.run_number,
        event: run.event,
        branch: run.head_branch,
        commit_sha: run.head_sha,
        html_url: run.html_url,
        duration_ms: this.calculateDuration(run.created_at, run.updated_at),
      }));
    } catch (error) {
      console.error('Failed to fetch workflow runs:', error);
      throw error;
    }
  }

  /**
   * 获取特定工作流的运行状态
   */
  async getWorkflowRunsByName(workflowName: string, limit: number = 5): Promise<WorkflowRun[]> {
    try {
      const runs = await this.getRecentWorkflowRuns(50);
      return runs
        .filter((run) => run.name === workflowName)
        .slice(0, limit);
    } catch (error) {
      console.error(`Failed to fetch runs for workflow "${workflowName}":`, error);
      throw error;
    }
  }

  /**
   * 获取构建状态摘要
   */
  async getBuildStatusSummary(): Promise<BuildStatusSummary> {
    try {
      const runs = await this.getRecentWorkflowRuns(20);
      
      const completedRuns = runs.filter((run) => run.status === 'completed');
      const successfulRuns = completedRuns.filter((run) => run.conclusion === 'success');
      
      const totalDuration = completedRuns.reduce((sum, run) => sum + (run.duration_ms || 0), 0);
      const averageDuration = completedRuns.length > 0 ? totalDuration / completedRuns.length : 0;

      const inProgressRuns = runs.filter((run) => 
        run.status === 'in_progress' || run.status === 'queued'
      );

      return {
        totalRuns: runs.length,
        successRate: completedRuns.length > 0 
          ? (successfulRuns.length / completedRuns.length) * 100 
          : 0,
        averageDuration,
        lastBuildTime: runs[0]?.updated_at || '',
        currentStatus: inProgressRuns,
      };
    } catch (error) {
      console.error('Failed to get build status summary:', error);
      throw error;
    }
  }

  /**
   * 获取特定运行的详细日志
   */
  async getWorkflowRunLogs(runId: number): Promise<string> {
    try {
      const response = await fetch(
        `${this.baseUrl}/repos/${this.owner}/${this.repo}/actions/runs/${runId}/logs`,
        {
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch logs: ${response.status}`);
      }

      return await response.text();
    } catch (error) {
      console.error(`Failed to fetch logs for run ${runId}:`, error);
      throw error;
    }
  }

  /**
   * 重新触发工作流
   */
  async triggerWorkflow(workflowId: string, branch: string = 'main'): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/repos/${this.owner}/${this.repo}/actions/workflows/${workflowId}/dispatches`,
        {
          method: 'POST',
          headers: {
            ...this.getHeaders(),
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ ref: branch }),
        }
      );

      return response.ok;
    } catch (error) {
      console.error('Failed to trigger workflow:', error);
      throw error;
    }
  }

  /**
   * 计算构建持续时间（毫秒）
   */
  private calculateDuration(startTime: string, endTime: string): number {
    const start = new Date(startTime).getTime();
    const end = new Date(endTime).getTime();
    return end - start;
  }

  /**
   * 获取请求头
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Accept': 'application/vnd.github.v3+json',
    };

    if (this.token) {
      headers['Authorization'] = `token ${this.token}`;
    }

    return headers;
  }

  /**
   * 格式化持续时间
   */
  static formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }

  /**
   * 获取状态显示文本
   */
  static getStatusText(status: WorkflowRun['status'], conclusion: WorkflowRun['conclusion']): string {
    if (status === 'completed') {
      switch (conclusion) {
        case 'success': return '✅ 成功';
        case 'failure': return '❌ 失败';
        case 'cancelled': return '⚠️ 已取消';
        case 'skipped': return '⏭️ 已跳过';
        default: return '❓ 未知';
      }
    }
    
    switch (status) {
      case 'in_progress': return '🔄 构建中';
      case 'queued': return '⏳ 排队中';
      case 'waiting': return '⏸️ 等待中';
      default: return '❓ 未知';
    }
  }

  /**
   * 获取状态颜色
   */
  static getStatusColor(status: WorkflowRun['status'], conclusion: WorkflowRun['conclusion']): string {
    if (status === 'completed') {
      switch (conclusion) {
        case 'success': return '#10b981'; // green
        case 'failure': return '#ef4444'; // red
        case 'cancelled': return '#f59e0b'; // yellow
        default: return '#6b7280'; // gray
      }
    }
    
    return '#3b82f6'; // blue for in progress
  }
}
