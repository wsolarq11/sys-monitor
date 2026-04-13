import { create } from 'zustand';

interface SystemMetric {
  id?: number;
  timestamp: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage?: number;
}

interface MetricsState {
  currentMetrics: SystemMetric | null;
  historicalMetrics: SystemMetric[];
  loading: boolean;
  error: string | null;
  
  // Actions
  setCurrentMetrics: (metrics: SystemMetric) => void;
  addHistoricalMetric: (metric: SystemMetric) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useMetricsStore = create<MetricsState>((set) => ({
  currentMetrics: null,
  historicalMetrics: [],
  loading: false,
  error: null,
  
  setCurrentMetrics: (metrics) => set({ currentMetrics: metrics }),
  addHistoricalMetric: (metric) => set((state) => ({
    historicalMetrics: [metric, ...state.historicalMetrics].slice(0, 100)
  })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
