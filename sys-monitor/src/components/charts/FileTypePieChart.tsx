/**
 * 文件类型分布饼图
 * 
 * 展示不同文件类型的数量和大小分布
 */

import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { formatBytes } from '../../utils/chartUtils';

export interface FileTypeData {
  extension: string;
  count: number;
  totalSize: number;
}

interface FileTypePieChartProps {
  /** 文件类型数据 */
  data: FileTypeData[];
  /** 图表标题 */
  title?: string;
  /** 图表高度 */
  height?: number;
  /** 按数量还是大小排序 */
  sortBy?: 'count' | 'size';
}

// 预定义颜色方案
const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
  '#14b8a6', '#e11d48', '#0ea5e9', '#a855f7', '#d946ef',
];

export const FileTypePieChart: React.FC<FileTypePieChartProps> = ({
  data,
  title = '文件类型分布',
  height = 300,
  sortBy = 'size',
}) => {
  // 处理数据，合并小类别
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // 排序
    const sorted = [...data].sort((a, b) => {
      if (sortBy === 'count') {
        return b.count - a.count;
      }
      return b.totalSize - a.totalSize;
    });

    // 如果类别太多，合并小的类别
    if (sorted.length > 10) {
      const top9 = sorted.slice(0, 9);
      const others = sorted.slice(9);
      
      const othersData: FileTypeData = {
        extension: '其他',
        count: others.reduce((sum, item) => sum + item.count, 0),
        totalSize: others.reduce((sum, item) => sum + item.totalSize, 0),
      };

      return [...top9, othersData].map(item => ({
        name: item.extension,
        value: sortBy === 'count' ? item.count : item.totalSize,
        count: item.count,
        size: item.totalSize,
      }));
    }

    return sorted.map(item => ({
      name: item.extension,
      value: sortBy === 'count' ? item.count : item.totalSize,
      count: item.count,
      size: item.totalSize,
    }));
  }, [data, sortBy]);

  // 自定义提示框
  const CustomTooltip = React.useCallback(({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-white font-semibold mb-1">{data.name}</p>
          <p className="text-gray-300 text-sm">文件数: {data.count}</p>
          <p className="text-gray-300 text-sm">总大小: {formatBytes(data.size)}</p>
          <p className="text-blue-400 text-sm mt-1">
            占比: {((data.value / payload.reduce((sum: number, p: any) => sum + p.value, 0)) * 100).toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  }, []);

  if (!data || data.length === 0) {
    return (
      <div className="w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
          {title}
        </h3>
        <div className="flex items-center justify-center" style={{ height }}>
          <p className="text-gray-500">暂无数据</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          {title}
        </h3>
        <div className="text-sm text-gray-500">
          共 {data.length} 种文件类型
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={CustomTooltip} />
          <Legend
            layout="horizontal"
            verticalAlign="bottom"
            align="center"
            wrapperStyle={{ fontSize: 12 }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
