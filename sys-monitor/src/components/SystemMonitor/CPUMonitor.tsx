import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Card } from '../common/Card';

export function CPUMonitor() {
  const [cpuUsage, setCpuUsage] = useState<number>(0);

  useEffect(() => {
    const fetchCpuMetrics = async () => {
      try {
        const metrics = await invoke<any>('get_system_metrics');
        setCpuUsage(metrics.cpu_usage);
      } catch (error) {
        console.error('Failed to fetch CPU metrics:', error);
      }
    };

    // Initial fetch
    fetchCpuMetrics();

    // Poll every second
    const interval = setInterval(fetchCpuMetrics, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card title="CPU Usage">
      <div className="text-4xl font-bold text-blue-600">
        {cpuUsage.toFixed(1)}%
      </div>
      <div className="mt-2 text-sm text-gray-500">
        Current usage across all cores
      </div>
    </Card>
  );
}
