import { useEffect, useState, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { BaseChart } from '../common/BaseChart';
import { RingBuffer, type DataPoint } from '../../utils/chartUtils';

// 创建环形缓冲区，最多保存 100 个数据点
const memoryBuffer = new RingBuffer<DataPoint>(100);

export const MemoryGraph: React.FC = () => {
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
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

      // 使用环形缓冲区添加新数据
      memoryBuffer.push(newDataPoint);
      
      // 更新状态
      setData(memoryBuffer.toArray());
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch memory metrics');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchMetrics();

    // Poll every second
    const interval = setInterval(fetchMetrics, 1000);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

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
      maxDataPoints={100}
    />
  );
};
