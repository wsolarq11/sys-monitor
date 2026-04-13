import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { BaseChart, type DataPoint } from '../common/BaseChart';

export const CPUGraph: React.FC = () => {
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const metrics = await invoke<any>('get_system_metrics');
        const newDataPoint: DataPoint = {
          time: new Date().toISOString(),
          cpu: metrics.cpu_usage,
        };

        setData((prev) => {
          const updated = [...prev, newDataPoint];
          // Keep last 60 data points (1 minute at 1 second intervals)
          return updated.slice(-60);
        });

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch CPU metrics');
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
        <div className="text-gray-500">Loading CPU data...</div>
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
      title="CPU Usage"
      data={data}
      dataKeys={['cpu']}
      colors={['#3b82f6']}
      yAxisDomain={[0, 100]}
      yAxisLabel="Usage %"
      height={250}
    />
  );
};
