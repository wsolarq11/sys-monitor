import React, { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts';

interface DiskData {
  mount_point: string;
  total_bytes: number;
  available_bytes: number;
  used_bytes: number;
  usage_percent: number;
  disk_type: string;
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export const DiskUsageCard: React.FC = () => {
  const [disks, setDisks] = useState<DiskData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDiskInfo = async () => {
      try {
        const result = await invoke<any>('get_disk_info');
        setDisks(result.disks || []);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch disk information');
        setLoading(false);
      }
    };

    fetchDiskInfo();
  }, []);

  if (loading) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <div className="text-gray-500">Loading disk data...</div>
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

  const chartData = disks.map((disk) => ({
    name: disk.mount_point,
    used: Math.round(disk.usage_percent),
    free: Math.round(100 - disk.usage_percent),
    total: formatBytes(disk.total_bytes),
    type: disk.disk_type,
  }));

  return (
    <div className="w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
        Disk Usage
      </h3>

      {disks.length === 0 ? (
        <div className="text-gray-500 text-center py-8">No disks found</div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 12 }} />
              <YAxis
                domain={[0, 100]}
                stroke="#6b7280"
                tick={{ fontSize: 12 }}
                label={{ value: 'Usage %', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '0.5rem',
                }}
                labelStyle={{ color: '#f3f4f6' }}
                formatter={(value: number, name: string) => {
                  if (name === 'used' || name === 'free') {
                    return [`${value}%`, name === 'used' ? 'Used' : 'Free'];
                  }
                  return [value, name];
                }}
              />
              <Legend />
              <Bar dataKey="used" name="Used" stackId="a" fill="#3b82f6">
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Bar>
              <Bar dataKey="free" name="Free" stackId="a" fill="#9ca3af" />
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {disks.map((disk, index) => (
              <div
                key={index}
                className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3"
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-800 dark:text-gray-200">
                    {disk.mount_point}
                  </span>
                  <span className="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                    {disk.disk_type}
                  </span>
                </div>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex justify-between">
                    <span>Used:</span>
                    <span className="font-medium">
                      {formatBytes(disk.used_bytes)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Free:</span>
                    <span className="font-medium">
                      {formatBytes(disk.available_bytes)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total:</span>
                    <span className="font-medium">
                      {formatBytes(disk.total_bytes)}
                    </span>
                  </div>
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${disk.usage_percent}%` }}
                      />
                    </div>
                    <div className="text-right text-xs mt-1 text-gray-500 dark:text-gray-400">
                      {disk.usage_percent.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
