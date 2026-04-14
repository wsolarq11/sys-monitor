/**
 * 第七阶段：Store 状态管理单元测试
 * 测试范围：metricsStore 状态转换、并发安全性
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useMetricsStore, type SystemMetric } from './metricsStore';

// 内部函数的测试通过 store 的 calculateStats action 间接测试

describe('useMetricsStore', () => {
  beforeEach(() => {
    // 重置 store 状态
    useMetricsStore.setState({
      currentMetrics: null,
      historicalMetrics: [],
      loading: false,
      error: null,
      stats: null,
    });
  });

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const state = useMetricsStore.getState();
      expect(state.currentMetrics).toBeNull();
      expect(state.historicalMetrics).toEqual([]);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.stats).toBeNull();
    });
  });

  describe('setCurrentMetrics', () => {
    it('应该设置当前指标', () => {
      const metric: SystemMetric = {
        id: 1,
        timestamp: Date.now(),
        cpu_usage: 45.5,
        memory_usage: 60.2,
        disk_usage: 50.0,
      };

      useMetricsStore.getState().setCurrentMetrics(metric);

      const state = useMetricsStore.getState();
      expect(state.currentMetrics).toEqual(metric);
    });

    it('应该覆盖之前的指标', () => {
      const metric1: SystemMetric = {
        id: 1,
        timestamp: 1000,
        cpu_usage: 40.0,
        memory_usage: 50.0,
      };

      const metric2: SystemMetric = {
        id: 2,
        timestamp: 2000,
        cpu_usage: 60.0,
        memory_usage: 70.0,
      };

      useMetricsStore.getState().setCurrentMetrics(metric1);
      useMetricsStore.getState().setCurrentMetrics(metric2);

      const state = useMetricsStore.getState();
      expect(state.currentMetrics).toEqual(metric2);
    });
  });

  describe('addHistoricalMetric', () => {
    it('应该添加指标到历史记录', () => {
      const metric: SystemMetric = {
        id: 1,
        timestamp: Date.now(),
        cpu_usage: 50.0,
        memory_usage: 60.0,
      };

      useMetricsStore.getState().addHistoricalMetric(metric);

      const state = useMetricsStore.getState();
      expect(state.historicalMetrics).toHaveLength(1);
      expect(state.historicalMetrics[0]).toEqual(metric);
    });

    it('应该保持最新的 100 条记录', () => {
      // 添加 101 条记录
      for (let i = 0; i < 101; i++) {
        useMetricsStore.getState().addHistoricalMetric({
          id: i,
          timestamp: i,
          cpu_usage: i,
          memory_usage: i,
        });
      }

      const state = useMetricsStore.getState();
      expect(state.historicalMetrics).toHaveLength(100);
      expect(state.historicalMetrics[0].id).toBe(100); // 最新的在前面
    });

    it('应该保持时间顺序（最新的在前）', () => {
      useMetricsStore.getState().addHistoricalMetric({
        id: 1,
        timestamp: 1000,
        cpu_usage: 40.0,
        memory_usage: 50.0,
      });

      useMetricsStore.getState().addHistoricalMetric({
        id: 2,
        timestamp: 2000,
        cpu_usage: 60.0,
        memory_usage: 70.0,
      });

      const state = useMetricsStore.getState();
      expect(state.historicalMetrics[0].timestamp).toBe(2000);
      expect(state.historicalMetrics[1].timestamp).toBe(1000);
    });
  });

  describe('clearHistoricalMetrics', () => {
    it('应该清空历史记录和统计', () => {
      // 先添加一些数据
      useMetricsStore.getState().addHistoricalMetric({
        id: 1,
        timestamp: Date.now(),
        cpu_usage: 50.0,
        memory_usage: 60.0,
      });

      useMetricsStore.getState().calculateStats();

      // 清空
      useMetricsStore.getState().clearHistoricalMetrics();

      const state = useMetricsStore.getState();
      expect(state.historicalMetrics).toHaveLength(0);
      expect(state.stats).toBeNull();
    });
  });

  describe('setLoading', () => {
    it('应该设置加载状态', () => {
      useMetricsStore.getState().setLoading(true);
      expect(useMetricsStore.getState().loading).toBe(true);

      useMetricsStore.getState().setLoading(false);
      expect(useMetricsStore.getState().loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('应该设置错误状态', () => {
      useMetricsStore.getState().setError('Test error');
      expect(useMetricsStore.getState().error).toBe('Test error');

      useMetricsStore.getState().setError(null);
      expect(useMetricsStore.getState().error).toBeNull();
    });
  });

  describe('calculateStats', () => {
    it('应该计算历史指标的统计', () => {
      // 添加测试数据
      const metrics: SystemMetric[] = [
        { id: 1, timestamp: 1000, cpu_usage: 40.0, memory_usage: 50.0, disk_usage: 60.0 },
        { id: 2, timestamp: 2000, cpu_usage: 60.0, memory_usage: 70.0, disk_usage: 80.0 },
        { id: 3, timestamp: 3000, cpu_usage: 50.0, memory_usage: 60.0, disk_usage: 70.0 },
      ];

      metrics.forEach(m => useMetricsStore.getState().addHistoricalMetric(m));
      useMetricsStore.getState().calculateStats();

      const state = useMetricsStore.getState();
      expect(state.stats).not.toBeNull();
      expect(state.stats!.avgCpu).toBeCloseTo(50.0, 1);
      expect(state.stats!.peakCpu).toBe(60.0);
    });

    it('应该在空历史记录时计算零值统计', () => {
      useMetricsStore.getState().clearHistoricalMetrics();
      useMetricsStore.getState().calculateStats();

      const state = useMetricsStore.getState();
      expect(state.stats).toEqual({
        avgCpu: 0,
        avgMemory: 0,
        avgDisk: 0,
        peakCpu: 0,
        peakMemory: 0,
        peakDisk: 0,
      });
    });
  });

  describe('状态转换场景', () => {
    it('应该正确处理完整的状态转换流程', () => {
      // 1. 初始状态
      let state = useMetricsStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();

      // 2. 开始加载
      useMetricsStore.getState().setLoading(true);
      state = useMetricsStore.getState();
      expect(state.loading).toBe(true);

      // 3. 加载完成，设置指标
      const metric: SystemMetric = {
        id: 1,
        timestamp: Date.now(),
        cpu_usage: 55.0,
        memory_usage: 65.0,
        disk_usage: 45.0,
      };
      useMetricsStore.getState().setCurrentMetrics(metric);
      useMetricsStore.getState().addHistoricalMetric(metric);

      // 4. 计算统计
      useMetricsStore.getState().calculateStats();

      // 5. 加载完成
      useMetricsStore.getState().setLoading(false);

      state = useMetricsStore.getState();
      expect(state.loading).toBe(false);
      expect(state.currentMetrics).toEqual(metric);
      expect(state.historicalMetrics).toHaveLength(1);
      expect(state.stats).not.toBeNull();
    });

    it('应该正确处理错误状态', () => {
      // 1. 开始加载
      useMetricsStore.getState().setLoading(true);

      // 2. 发生错误
      useMetricsStore.getState().setError('Network error');
      useMetricsStore.getState().setLoading(false);

      const state = useMetricsStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Network error');
    });
  });

  describe('并发安全性', () => {
    it('应该正确处理快速连续的更新', () => {
      // 模拟快速连续的指标更新
      for (let i = 0; i < 10; i++) {
        useMetricsStore.getState().setCurrentMetrics({
          id: i,
          timestamp: i,
          cpu_usage: i * 10,
          memory_usage: i * 5,
        });
      }

      const state = useMetricsStore.getState();
      expect(state.currentMetrics!.id).toBe(9);
      expect(state.currentMetrics!.cpu_usage).toBe(90);
    });

    it('应该在并发添加历史记录时保持数据完整性', () => {
      // 模拟并发添加（在 JavaScript 中是异步的）
      const promises = Array.from({ length: 10 }, (_, i) =>
        Promise.resolve().then(() => {
          useMetricsStore.getState().addHistoricalMetric({
            id: i,
            timestamp: i,
            cpu_usage: i,
            memory_usage: i,
          });
        })
      );

      // 等待所有"并发"操作完成
      Promise.all(promises).then(() => {
        const state = useMetricsStore.getState();
        expect(state.historicalMetrics).toHaveLength(10);
      });
    });
  });
});

describe('MetricsStore 集成场景', () => {
  beforeEach(() => {
    useMetricsStore.setState({
      currentMetrics: null,
      historicalMetrics: [],
      loading: false,
      error: null,
      stats: null,
    });
  });

  it('应该支持完整的监控周期', () => {
    // 场景：模拟一个完整的监控周期
    
    // 1. 开始监控
    useMetricsStore.getState().setLoading(true);
    
    // 2. 接收第一组数据
    const metric1: SystemMetric = {
      id: 1,
      timestamp: 1000,
      cpu_usage: 45.0,
      memory_usage: 55.0,
      disk_usage: 65.0,
    };
    useMetricsStore.getState().setCurrentMetrics(metric1);
    useMetricsStore.getState().addHistoricalMetric(metric1);
    
    // 3. 接收第二组数据
    const metric2: SystemMetric = {
      id: 2,
      timestamp: 2000,
      cpu_usage: 50.0,
      memory_usage: 60.0,
      disk_usage: 70.0,
    };
    useMetricsStore.getState().setCurrentMetrics(metric2);
    useMetricsStore.getState().addHistoricalMetric(metric2);
    
    // 4. 计算统计
    useMetricsStore.getState().calculateStats();
    
    // 5. 完成加载
    useMetricsStore.getState().setLoading(false);
    
    // 验证状态
    const state = useMetricsStore.getState();
    expect(state.loading).toBe(false);
    expect(state.currentMetrics).toEqual(metric2); // 当前是最新的
    expect(state.historicalMetrics).toHaveLength(2);
    expect(state.stats!.avgCpu).toBeCloseTo(47.5, 1);
    expect(state.stats!.peakCpu).toBe(50.0);
  });

  it('应该支持错误恢复', () => {
    // 1. 发生错误
    useMetricsStore.getState().setError('Connection failed');
    
    // 2. 清除错误
    useMetricsStore.getState().setError(null);
    
    // 3. 恢复正常操作
    const metric: SystemMetric = {
      id: 1,
      timestamp: Date.now(),
      cpu_usage: 50.0,
      memory_usage: 60.0,
    };
    useMetricsStore.getState().setCurrentMetrics(metric);
    
    const state = useMetricsStore.getState();
    expect(state.error).toBeNull();
    expect(state.currentMetrics).toEqual(metric);
  });
});
