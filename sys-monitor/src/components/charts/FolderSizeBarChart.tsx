/**
 * 文件夹大小柱状图
 * 
 * 展示各文件夹的大小对比
 */

import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { formatBytes } from '../../utils/chartUtils';

export interface FolderSizeData {
  name: string;
  path: string;
  size: number;
  fileCount: number;
}

interface FolderSizeBarChartProps {
  /** 文件夹数据 */
  data: FolderSizeData[];
  /** 图表标题 */
  title?: string;
  /** 图表高度 */
  height?: number;
  /** 最大显示数量 */
  maxItems?: number;
  /** 是否水平显示 */
  horizontal?: boolean;
}

// 颜色渐变方案
const getBarColor = (index: number, total: number) => {
  const ratio = index / total;
  if (ratio < 0.33) return '#3b82f6'; // 蓝色 - 小
  if (ratio < 0.66) return '#f59e0b'; // 橙色 - 中
  return '#ef4444'; // 红色 - 大
};

export const FolderSizeBarChart: React.FC<FolderSizeBarChartProps> = ({
  data,
  title = '文件夹大小对比',
  height = 300,
  maxItems = 15,
  horizontal = false,
}) => {
  // 处理数据，取最大的几个文件夹
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // 按大小排序
    const sorted = [...data].sort((a, b) => b.size - a.size);
    
    // 取前 N 个
    const top = sorted.slice(0, maxItems);
    
    return top.map((item, index) => ({
      name: item.name.length > 20 ? item.name.substring(0, 20) + '...' : item.name,
      fullName: item.name,
      path: item.path,
      size: item.size,
      fileCount: item.fileCount,
      color: getBarColor(index, top.length),
    }));
  }, [data, maxItems]);

  // 自定义提示框
  const CustomTooltip = React.useCallback(({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-lg max-w-xs">
          <p className="text-white font-semibold mb-1 truncate" title={data.fullName}>
            {data.fullName}
          </p>
          <p className="text-gray-300 text-sm">大小: {formatBytes(data.size)}</p>
          <p className="text-gray-300 text-sm">文件数: {data.fileCount}</p>
          <p className="text-blue-400 text-xs mt-1 truncate" title={data.path}>
            {data.path}
          </p>
        </div>
      );
    }
    return null;
  }, []);

  // 格式化 Y 轴标签
  const formatYAxis = React.useCallback((value: number) => {
    return formatBytes(value, 1);
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
          显示前 {Math.min(maxItems, data.length)} 个文件夹
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          layout={horizontal ? 'vertical' : 'horizontal'}
          margin={horizontal ? { left: 100 } : { bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          
          {horizontal ? (
            <>
              <XAxis type="number" tickFormatter={formatYAxis} stroke="#6b7280" />
              <YAxis
                type="category"
                dataKey="name"
                stroke="#6b7280"
                tick={{ fontSize: 11 }}
                width={100}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey="name"
                stroke="#6b7280"
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis tickFormatter={formatYAxis} stroke="#6b7280" />
            </>
          )}
          
          <Tooltip content={CustomTooltip} />
          <Bar dataKey="size" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
