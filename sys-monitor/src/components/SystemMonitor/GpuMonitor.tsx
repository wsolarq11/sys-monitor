import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Card } from '../common/Card';

interface GpuInfo {
  vendor: string;
  model: string;
  usage_percent: number;
  memory_used: number;  // MB
  memory_total: number; // MB
  temperature?: number; // Celsius
}

export function GpuMonitor() {
  const [gpuInfo, setGpuInfo] = useState<GpuInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notSupported, setNotSupported] = useState(false);

  const fetchGpuInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<GpuInfo | null>('get_gpu_info');
      if (result) {
        setGpuInfo(result);
        setNotSupported(false);
      } else {
        setNotSupported(true);
        setGpuInfo(null);
      }
    } catch (err) {
      console.error('Failed to fetch GPU info:', err);
      setError('获取GPU信息失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchGpuInfo();

    // Poll every 5 seconds (GPU monitoring is less critical)
    const interval = setInterval(fetchGpuInfo, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatMemory = (mb: number): string => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(2)} GB`;
    }
    return `${mb} MB`;
  };

  if (loading && !gpuInfo) {
    return (
      <Card title="GPU Monitor">
        <div className="text-center py-4 text-gray-500">Loading...</div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="GPU Monitor">
        <div className="text-center py-4 text-red-500">{error}</div>
      </Card>
    );
  }

  if (notSupported) {
    return (
      <Card title="GPU Monitor">
        <div className="text-center py-4 text-gray-500">
          <div className="text-lg mb-2">⚠️ GPU Monitoring Not Available</div>
          <div className="text-sm">
            GPU monitoring is currently only supported for NVIDIA GPUs with nvidia-smi installed.
          </div>
          <div className="text-xs mt-2 text-gray-400">
            AMD/Intel GPU support is planned for future releases.
          </div>
        </div>
      </Card>
    );
  }

  if (!gpuInfo) {
    return null;
  }

  const memoryUsagePercent = gpuInfo.memory_total > 0
    ? (gpuInfo.memory_used / gpuInfo.memory_total) * 100
    : 0;

  return (
    <Card title="GPU Monitor">
      <div className="space-y-4">
        {/* GPU Model */}
        <div>
          <div className="text-sm text-gray-500 mb-1">GPU Model</div>
          <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {gpuInfo.model}
          </div>
          <div className="text-xs text-gray-400">{gpuInfo.vendor}</div>
        </div>

        {/* Usage Metrics */}
        <div className="grid grid-cols-2 gap-4">
          {/* GPU Usage */}
          <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">GPU Usage</div>
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 font-mono">
              {gpuInfo.usage_percent.toFixed(1)}%
            </div>
            <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-600 transition-all duration-500"
                style={{ width: `${Math.min(gpuInfo.usage_percent, 100)}%` }}
              />
            </div>
          </div>

          {/* Memory Usage */}
          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">VRAM Usage</div>
            <div className="text-xl font-bold text-blue-600 dark:text-blue-400 font-mono">
              {formatMemory(gpuInfo.memory_used)}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500">
              / {formatMemory(gpuInfo.memory_total)} ({memoryUsagePercent.toFixed(1)}%)
            </div>
            <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-500"
                style={{ width: `${Math.min(memoryUsagePercent, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Temperature (if available) */}
        {gpuInfo.temperature !== undefined && (
          <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Temperature</div>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400 font-mono">
                {gpuInfo.temperature}°C
              </div>
              <div className="text-xs text-gray-500">
                {gpuInfo.temperature > 80
                  ? '🔥 High'
                  : gpuInfo.temperature > 60
                  ? '⚠️ Warm'
                  : '✅ Normal'}
              </div>
            </div>
            <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  gpuInfo.temperature > 80
                    ? 'bg-red-600'
                    : gpuInfo.temperature > 60
                    ? 'bg-orange-500'
                    : 'bg-green-600'
                }`}
                style={{ width: `${Math.min((gpuInfo.temperature / 100) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Status indicator */}
        <div className="flex items-center justify-between text-xs text-gray-500 border-t pt-3">
          <span>Auto-refresh: 5s</span>
          <span className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
            Monitoring Active
          </span>
        </div>
      </div>
    </Card>
  );
}
