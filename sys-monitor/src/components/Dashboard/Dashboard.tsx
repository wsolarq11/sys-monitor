import { CPUMonitor } from '../SystemMonitor/CPUMonitor';
import { MemoryMonitor } from '../SystemMonitor/MemoryMonitor';
import { CPUGraph } from '../SystemMonitor/CPUGraph';
import { MemoryGraph } from '../SystemMonitor/MemoryGraph';
import { DiskUsageCard } from '../SystemMonitor/DiskUsageCard';
import { ProcessMonitor } from '../SystemMonitor/ProcessMonitor';
import { NetworkMonitor } from '../SystemMonitor/NetworkMonitor';
import { GpuMonitor } from '../SystemMonitor/GpuMonitor';
import BuildStatusCard from '../BuildStatus/BuildStatusCard';

export function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">
        SysMonitor Dashboard
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <CPUMonitor />
        <MemoryMonitor />
      </div>

      <div className="grid grid-cols-1 gap-6 mb-6">
        <CPUGraph />
      </div>

      <div className="grid grid-cols-1 gap-6 mb-6">
        <MemoryGraph />
      </div>

      <div className="grid grid-cols-1 gap-6 mb-6">
        <DiskUsageCard />
      </div>

      {/* GPU 监控（条件渲染） */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        <GpuMonitor />
      </div>

      {/* 进程监控 */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        <ProcessMonitor />
      </div>

      {/* 网络监控 */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        <NetworkMonitor />
      </div>

      {/* 远程构建状态监控 */}
      <div className="grid grid-cols-1 gap-6 mt-6">
        <BuildStatusCard 
          owner={import.meta.env.VITE_GITHUB_OWNER || 'your-username'}
          repo={import.meta.env.VITE_GITHUB_REPO || 'FolderSizeMonitor'}
          token={import.meta.env.VITE_GITHUB_TOKEN}
          refreshInterval={parseInt(import.meta.env.VITE_BUILD_REFRESH_INTERVAL) || 60000}
        />
      </div>
    </div>
  );
}
