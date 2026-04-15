import { createContext, useContext, useRef, useState, useEffect, useCallback, ReactNode } from 'react';
import { ResourceMonitor, getResourceMonitor, type ResourceMetrics } from '../utils/resourceMonitor';
import { MLAnomalyDetector, getAnomalyDetector, type AnomalyDetectionResult } from '../utils/mlAnomalyDetector';
import { ChaosManager, getChaosManager, type ChaosTestResult } from '../utils/chaosManager';
import { useMetricsStore } from '../stores/metricsStore';

// MonitorContext 接口定义
interface MonitorContextType {
  resourceMonitor: ResourceMonitor;
  anomalyDetector: MLAnomalyDetector;
  chaosManager: ChaosManager;
  getCurrentMetrics: () => ResourceMetrics;
  getAnomalyResults: (limit?: number) => AnomalyDetectionResult[];
  getChaosResults: (limit?: number) => ChaosTestResult[];
}

// 创建 Context
const MonitorContext = createContext<MonitorContextType | null>(null);

// Context Provider 属性
interface MonitorProviderProps {
  children: ReactNode;
  syncInterval?: number; // 同步到 Zustand 的时间间隔（毫秒）
}

// Monitor Provider 组件
export function MonitorProvider({ children, syncInterval = 30000 }: MonitorProviderProps) {
  // 使用 useRef 保存单例实例
  const resourceMonitorRef = useRef<ResourceMonitor | null>(null);
  const anomalyDetectorRef = useRef<MLAnomalyDetector | null>(null);
  const chaosManagerRef = useRef<ChaosManager | null>(null);
  const [isReady, setIsReady] = useState(false);

  // Zustand store
  const setCurrentMetrics = useMetricsStore(state => state.setCurrentMetrics);
  const addHistoricalMetric = useMetricsStore(state => state.addHistoricalMetric);

  // 初始化监控器实例（仅在组件挂载时执行一次）
  useEffect(() => {
    // 获取单例实例
    resourceMonitorRef.current = getResourceMonitor();
    anomalyDetectorRef.current = getAnomalyDetector();
    chaosManagerRef.current = getChaosManager();
    setIsReady(true);

    // 启动机器学习模型训练
    anomalyDetectorRef.current.trainModel().catch(error => {
      console.error('ML 模型训练失败:', error);
    });

    // 在开发环境或特定条件下启动混沌测试
    if (import.meta.env.DEV || window.location.search.includes('chaos=true')) {
      chaosManagerRef.current.startChaosTesting();
    }

    // 清理函数
    return () => {
      // 停止混沌测试
      if (chaosManagerRef.current) {
        chaosManagerRef.current.stopChaosTesting();
      }
      
      // 销毁实例（注意：这里不销毁全局单例，只清理引用）
      resourceMonitorRef.current = null;
      anomalyDetectorRef.current = null;
      chaosManagerRef.current = null;
    };
  }, []);

  // 定期同步数据到 Zustand Store
  useEffect(() => {
    if (!resourceMonitorRef.current || !anomalyDetectorRef.current) {
      return;
    }

    // 立即同步一次
    syncMetricsToStore();

    // 设置定期同步
    const intervalId = setInterval(syncMetricsToStore, syncInterval);

    return () => {
      clearInterval(intervalId);
    };
  }, [syncInterval, setCurrentMetrics, addHistoricalMetric]);

  // 同步指标到 Store 的函数
  const syncMetricsToStore = useCallback(() => {
    if (!resourceMonitorRef.current) return;

    const resources = resourceMonitorRef.current.getCurrentMetrics();
    
    // 转换为 Zustand Store 格式
    const systemMetric = {
      timestamp: resources.timestamp,
      cpu_usage: resources.cpu.usage,
      memory_usage: resources.memory.usage,
      disk_usage: resources.storage.usage
    };

    // 更新当前指标
    setCurrentMetrics(systemMetric);
    
    // 添加历史指标
    addHistoricalMetric(systemMetric);

    // 同步异常检测数据
    if (anomalyDetectorRef.current) {
      anomalyDetectorRef.current.addDataPoint('memory_usage', resources.memory.usage / 100);
      anomalyDetectorRef.current.addDataPoint('cpu_usage', resources.cpu.usage / 100);
    }
  }, [setCurrentMetrics, addHistoricalMetric]);

  // 获取当前资源指标
  const getCurrentMetrics = useCallback((): ResourceMetrics => {
    if (!resourceMonitorRef.current) {
      throw new Error('ResourceMonitor not initialized');
    }
    return resourceMonitorRef.current.getCurrentMetrics();
  }, []);

  // 获取异常检测结果
  const getAnomalyResults = useCallback((): AnomalyDetectionResult[] => {
    // MLAnomalyDetector 目前没有直接获取历史结果的方法
    // 这里返回 null 数组作为占位，实际应用中可以扩展 MLAnomalyDetector
    return [];
  }, []);

  // 获取混沌测试结果
  const getChaosResults = useCallback((limit?: number): ChaosTestResult[] => {
    if (!chaosManagerRef.current) {
      return [];
    }
    return chaosManagerRef.current.getTestResults(limit);
  }, []);

  // Context 值
  if (!isReady) {
    return null; // 等待初始化完成后再渲染子组件
  }

  const contextValue: MonitorContextType = {
    resourceMonitor: resourceMonitorRef.current!,
    anomalyDetector: anomalyDetectorRef.current!,
    chaosManager: chaosManagerRef.current!,
    getCurrentMetrics,
    getAnomalyResults,
    getChaosResults
  };

  return (
    <MonitorContext.Provider value={contextValue}>
      {children}
    </MonitorContext.Provider>
  );
}

// 自定义 Hook - useMonitor
export function useMonitor(): MonitorContextType {
  const context = useContext(MonitorContext);
  
  if (context === null) {
    throw new Error(
      'useMonitor must be used within a MonitorProvider. ' +
      'Wrap your component tree with <MonitorProvider>.'
    );
  }
  
  return context;
}

// 可选：导出一个简化的 Hook，用于只访问特定监控器
export function useResourceMonitor(): ResourceMonitor {
  const { resourceMonitor } = useMonitor();
  return resourceMonitor;
}

export function useAnomalyDetector(): MLAnomalyDetector {
  const { anomalyDetector } = useMonitor();
  return anomalyDetector;
}

export function useChaosManager(): ChaosManager {
  const { chaosManager } = useMonitor();
  return chaosManager;
}
