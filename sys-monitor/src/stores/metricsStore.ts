import { create } from 'zustand';

export interface SystemMetric {
  id?: number;
  timestamp: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage?: number;
  network_rx?: number;
  network_tx?: number;
}

export interface MetricsStats {
  avgCpu: number;
  avgMemory: number;
  avgDisk: number;
  peakCpu: number;
  peakMemory: number;
  peakDisk: number;
}

interface MetricsState {
  // 状态
  currentMetrics: SystemMetric | null;
  historicalMetrics: SystemMetric[];
  loading: boolean;
  error: string | null;
  stats: MetricsStats | null;
  
  // Actions - 指标更新
  setCurrentMetrics: (metrics: SystemMetric) => void;
  addHistoricalMetric: (metric: SystemMetric) => void;
  clearHistoricalMetrics: () => void;
  
  // Actions - 状态管理
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Actions - 统计计算
  calculateStats: () => void;
}

const calculateMetricsStats = (metrics: SystemMetric[]): MetricsStats => {
  if (metrics.length === 0) {
    return { avgCpu: 0, avgMemory: 0, avgDisk: 0, peakCpu: 0, peakMemory: 0, peakDisk: 0 };
  }
  
  const cpuValues = metrics.map(m => m.cpu_usage);
  const memoryValues = metrics.map(m => m.memory_usage);
  const diskValues = metrics.map(m => m.disk_usage ?? 0);
  
  const sum = (arr: number[]) => arr.reduce((acc, val) => acc + val, 0);
  const max = (arr: number[]) => Math.max(...arr, 0);
  
  return {
    avgCpu: sum(cpuValues) / cpuValues.length,
    avgMemory: sum(memoryValues) / memoryValues.length,
    avgDisk: sum(diskValues) / diskValues.length,
    peakCpu: max(cpuValues),
    peakMemory: max(memoryValues),
    peakDisk: max(diskValues),
  };
};

export const useMetricsStore = create<MetricsState>((set, get) => ({
  // 初始状态
  currentMetrics: null,
  historicalMetrics: [],
  loading: false,
  error: null,
  stats: null,
  
  // Actions - 指标更新
  setCurrentMetrics: (metrics) => set({ currentMetrics: metrics }),
  
  addHistoricalMetric: (metric) => set((state) => {
    const newHistory = [metric, ...state.historicalMetrics].slice(0, 100);
    return { historicalMetrics: newHistory };
  }),
  
  clearHistoricalMetrics: () => set({ historicalMetrics: [], stats: null }),
  
  // Actions - 状态管理
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  // Actions - 统计计算
  calculateStats: () => {
    const { historicalMetrics } = get();
    const stats = calculateMetricsStats(historicalMetrics);
    set({ stats });
  },
}));
