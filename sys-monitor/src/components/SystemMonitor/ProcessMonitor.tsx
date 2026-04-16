import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Card } from '../common/Card';

interface ProcessInfo {
  pid: number;
  name: string;
  cpu_usage: number;
  memory: number;
  memory_percent: number;
}

type SortField = 'cpu' | 'memory';

export function ProcessMonitor() {
  const [processes, setProcesses] = useState<ProcessInfo[]>([]);
  const [sortField, setSortField] = useState<SortField>('cpu');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProcesses = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<ProcessInfo[]>('get_process_list', {
        limit: 20,
        sortBy: sortField,
      });
      setProcesses(result);
    } catch (err) {
      console.error('Failed to fetch process list:', err);
      setError('获取进程列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchProcesses();

    // Poll every 3 seconds
    const interval = setInterval(fetchProcesses, 3000);
    return () => clearInterval(interval);
  }, [sortField]);

  const formatMemory = (bytes: number): string => {
    if (bytes >= 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    } else if (bytes >= 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    } else if (bytes >= 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${bytes} B`;
  };

  const toggleSort = () => {
    setSortField((prev) => (prev === 'cpu' ? 'memory' : 'cpu'));
  };

  return (
    <Card title="Process Monitor">
      <div className="mb-3 flex justify-between items-center">
        <button
          onClick={toggleSort}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Sort by: {sortField === 'cpu' ? 'CPU ↑' : 'Memory ↑'}
        </button>
        <span className="text-xs text-gray-500">Auto-refresh: 3s</span>
      </div>

      {loading && processes.length === 0 && (
        <div className="text-center py-4 text-gray-500">Loading...</div>
      )}

      {error && <div className="text-center py-4 text-red-500">{error}</div>}

      {!loading && !error && processes.length === 0 && (
        <div className="text-center py-4 text-gray-500">No processes found</div>
      )}

      {!loading && !error && processes.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PID
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPU %
                </th>
                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Memory
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {processes.map((proc) => (
                <tr key={proc.pid} className="hover:bg-gray-50">
                  <td className="px-3 py-2 whitespace-nowrap text-gray-600">
                    {proc.pid}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap font-medium text-gray-900 truncate max-w-[200px]">
                    {proc.name}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-right">
                    <span
                      className={`font-mono ${
                        proc.cpu_usage > 50
                          ? 'text-red-600'
                          : proc.cpu_usage > 20
                          ? 'text-orange-500'
                          : 'text-green-600'
                      }`}
                    >
                      {proc.cpu_usage.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-right text-gray-600 font-mono">
                    {formatMemory(proc.memory)}
                    <span className="text-xs text-gray-400 ml-1">
                      ({proc.memory_percent.toFixed(1)}%)
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
