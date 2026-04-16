/**
 * 实时趋势图组件
 * 
 * 支持 CPU/内存/磁盘多指标实时监控
 * 使用环形缓冲区管理数据，自动滚动显示最新数据
 */

import React, { useMemo, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { RingBuffer, type DataPoint, formatTime } from '../../utils/chartUtils';

export type MetricType = 'cpu' | 'memory' | 'disk';

interface RealTimeChartProps {
  /** 图表标题 */
  title?: string;
  /** 指标类型 */
  metric: MetricType;
  /** 数据缓冲区（由父组件管理） */
  buffer: RingBuffer<DataPoint>;
  /** 线条颜色 */
  color?: string;
  /** Y轴标签 */
  yAxisLabel?: string;
  /** Y轴范围 */
  yAxisDomain?: [number, number];
  /** 图表高度 */
  height?: number;
  /** 是否显示网格线 */
  showGrid?: boolean;
  /** 是否显示图例 */
  showLegend?: boolean;
}

export const RealTimeChart: React.FC<RealTimeChartProps> = ({
  title,
  metric,
  buffer,
  color = '#3b82f6',
  yAxisLabel = 'Usage %',
  yAxisDomain = [0, 100],
  height = 300,
  showGrid = true,
  showLegend = false,
}) => {
  // 从缓冲区获取数据
  const data = useMemo(() => {
    return buffer.toArray();
  }, [buffer.size]); // 当缓冲区大小变化时重新计算

  // 格式化时间显示
  const timeFormatter = useCallback((value: string) => {
    return formatTime(value);
  }, []);

  // 自定义提示框
  const CustomTooltip = useCallback(({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-200 text-sm mb-1">{formatTime(payload[0].payload.time)}</p>
          <p className="text-white font-semibold">
            {`${yAxisLabel}: ${payload[0].value.toFixed(1)}%`}
          </p>
        </div>
      );
    }
    return null;
  }, [yAxisLabel]);

  return (
    <div className="w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      {title && (
        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
          {title}
        </h3>
      )}
      
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          {showGrid && (
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          )}
          <XAxis
            dataKey="time"
            stroke="#6b7280"
            tick={{ fontSize: 11 }}
            tickFormatter={timeFormatter}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={yAxisDomain}
            stroke="#6b7280"
            tick={{ fontSize: 11 }}
            label={
              yAxisLabel
                ? { value: yAxisLabel, angle: -90, position: 'insideLeft', style: { fontSize: 12 } }
                : undefined
            }
          />
          <Tooltip content={CustomTooltip} />
          {showLegend && <Legend />}
          <Line
            type="monotone"
            dataKey={metric}
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* 数据统计信息 */}
      <div className="mt-3 flex justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>数据点: {data.length}</span>
        <span>最新值: {data.length > 0 ? `${(data[data.length - 1][metric] as number).toFixed(1)}%` : '--'}</span>
      </div>
    </div>
  );
};
