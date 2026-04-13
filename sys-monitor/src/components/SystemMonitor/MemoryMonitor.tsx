import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Card } from '../common/Card';

function formatBytes(bytes: number): string {
  const gb = bytes / (1024 * 1024 * 1024);
  return `${gb.toFixed(2)} GB`;
}

export function MemoryMonitor() {
  const [memoryUsage, setMemoryUsage] = useState<number>(0);

  useEffect(() => {
    const fetchMemoryMetrics = async () => {
      try {
        const metrics = await invoke<any>('get_system_metrics');
        setMemoryUsage(metrics.memory_usage);
      } catch (error) {
        console.error('Failed to fetch memory metrics:', error);
      }
    };

    // Initial fetch
    fetchMemoryMetrics();

    // Poll every second
    const interval = setInterval(fetchMemoryMetrics, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card title="Memory Usage">
      <div className="text-4xl font-bold text-green-600">
        {formatBytes(memoryUsage)}
      </div>
      <div className="mt-2 text-sm text-gray-500">
        System memory in use
      </div>
    </Card>
  );
}
