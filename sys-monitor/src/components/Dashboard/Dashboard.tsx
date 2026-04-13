import { CPUMonitor } from '../SystemMonitor/CPUMonitor';
import { MemoryMonitor } from '../SystemMonitor/MemoryMonitor';
import { CPUGraph } from '../SystemMonitor/CPUGraph';
import { MemoryGraph } from '../SystemMonitor/MemoryGraph';
import { DiskUsageCard } from '../SystemMonitor/DiskUsageCard';

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

      <div className="grid grid-cols-1 gap-6">
        <DiskUsageCard />
      </div>
    </div>
  );
}
