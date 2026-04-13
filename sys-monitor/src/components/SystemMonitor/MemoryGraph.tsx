import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { BaseChart, type DataPoint } from '../common/BaseChart';

export const MemoryGraph: React.FC = () => {
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const metrics = await invoke<any>('get_system_metrics');
        const memoryPercent =
          metrics.memory_total > 0
            ? (metrics.memory_usage / metrics.memory_total) * 100
            : 0;

        const newDataPoint: DataPoint = {
          time: new Date().toISOString(),
          memory: memoryPercent,
        };

        setData((prev) => {
          const updated = [...prev, newDataPoint];
          // Keep last 60 data points
          return updated.slice(-60);
        });

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch memory metrics');
        setLoading(false);
      }
    };

    // Initial fetch
    fetchMetrics();

    // Poll every second
    const interval = setInterval(fetchMetrics, 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <div className="text-gray-500">Loading memory data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <BaseChart
      title="Memory Usage"
      data={data}
      dataKeys={['memory']}
      colors={['#10b981']}
      yAxisDomain={[0, 100]}
      yAxisLabel="Usage %"
      height={250}
    />
  );
};
