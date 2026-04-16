/**
 * 系统监控面板
 * 
 * 集成 CPU、内存、磁盘的实时监控图表
 * 支持指标切换和自动刷新
 */

import React, { useEffect, useState, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { RealTimeChart } from './RealTimeChart';
import { RingBuffer, type DataPoint } from '../../utils/chartUtils';

// 创建环形缓冲区
const cpuBuffer = new RingBuffer<DataPoint>(100);
const memoryBuffer = new RingBuffer<DataPoint>(100);
const diskBuffer = new RingBuffer<DataPoint>(100);

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  memory_total: number;
  disk_usage?: number;
}

export const SystemMonitorPanel: React.FC = () => {
  const [isRunning, setIsRunning] = useState(true);

  // 获取系统指标
  const fetchMetrics = useCallback(async () => {
    try {
      const metrics = await invoke<SystemMetrics>('get_system_metrics');
      
      const timestamp = new Date().toISOString();

      // CPU 数据
      cpuBuffer.push({
        time: timestamp,
        cpu: metrics.cpu_usage,
      });

      // 内存数据
      const memoryPercent = metrics.memory_total > 0
        ? (metrics.memory_usage / metrics.memory_total) * 100
        : 0;
      memoryBuffer.push({
        time: timestamp,
        memory: memoryPercent,
      });

      // 磁盘数据（如果有）
      if (metrics.disk_usage !== undefined) {
        diskBuffer.push({
          time: timestamp,
          disk: metrics.disk_usage,
        });
      }
    } catch (err) {
      console.error('Failed to fetch system metrics:', err);
    }
  }, []);

  useEffect(() => {
    if (!isRunning) return;

    // 初始获取
    fetchMetrics();

    // 每秒更新一次
    const interval = setInterval(fetchMetrics, 1000);
    return () => clearInterval(interval);
  }, [isRunning, fetchMetrics]);

  return (
    <div className="space-y-6">
      {/* 控制面板 */}
      <div className="flex justify-between items-center bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          系统实时监控
        </h2>
        <button
          onClick={() => setIsRunning(!isRunning)}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isRunning
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
        >
          {isRunning ? '暂停' : '继续'}
        </button>
      </div>

      {/* 监控图表 */}
      <div className="grid grid-cols-1 gap-6">
        <RealTimeChart
          title="CPU 使用率"
          metric="cpu"
          buffer={cpuBuffer}
          color="#3b82f6"
          yAxisLabel="CPU %"
        />

        <RealTimeChart
          title="内存使用率"
          metric="memory"
          buffer={memoryBuffer}
          color="#10b981"
          yAxisLabel="Memory %"
        />

        {diskBuffer.size > 0 && (
          <RealTimeChart
            title="磁盘使用率"
            metric="disk"
            buffer={diskBuffer}
            color="#f59e0b"
            yAxisLabel="Disk %"
          />
        )}
      </div>
    </div>
  );
};
