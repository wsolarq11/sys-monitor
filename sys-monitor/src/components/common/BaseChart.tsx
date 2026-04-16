import React, { useMemo } from 'react';
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
import { simpleSampling, type DataPoint } from '../../utils/chartUtils';

interface BaseChartProps {
  data: DataPoint[];
  dataKeys: string[];
  colors?: string[];
  yAxisDomain?: [number, number];
  yAxisLabel?: string;
  title?: string;
  height?: number;
  maxDataPoints?: number; // 最大数据点数，默认 100
}

export const BaseChart = React.memo<BaseChartProps>(({
  data,
  dataKeys,
  colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300'],
  yAxisDomain = [0, 100],
  yAxisLabel,
  title,
  height = 250,
  maxDataPoints = 100,
}) => {
  // 使用 useMemo 缓存采样后的数据
  const sampledData = useMemo(() => {
    return simpleSampling(data, maxDataPoints);
  }, [data, maxDataPoints]);

  // 格式化时间显示
  const timeFormatter = useMemo(() => {
    return (value: string) => {
      const date = new Date(value);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
      });
    };
  }, []);

  return (
    <div className="w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      {title && (
        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={sampledData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis
            dataKey="time"
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            tickFormatter={timeFormatter}
          />
          <YAxis
            domain={yAxisDomain}
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={
              yAxisLabel
                ? { value: yAxisLabel, angle: -90, position: 'insideLeft' }
                : undefined
            }
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '0.5rem',
            }}
            labelStyle={{ color: '#f3f4f6' }}
          />
          <Legend />
          {dataKeys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
              isAnimationActive={false} // 禁用动画以提升性能
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
});

BaseChart.displayName = 'BaseChart';
