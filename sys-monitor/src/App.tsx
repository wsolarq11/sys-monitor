import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { FolderAnalysisContainer } from './components/FolderAnalysis/FolderAnalysisContainer';
import { AdvancedToolsContainer } from './components/AdvancedTools/AdvancedToolsContainer';
import { Dashboard } from './components/Dashboard/Dashboard';
import { PerformanceMonitor } from './components/PerformanceMonitor';
import { MonitorProvider, useMonitor } from './contexts/MonitorContext';
import { getMetricsCollector } from './utils/metricsCollector';
import { getUserBehaviorAnalyzer } from './utils/userBehaviorAnalyzer';
import { getAlertManager } from './utils/alertManager';
import { useFolderWatcher } from './hooks/useFolderWatcher';

// App 内容组件（使用 Monitor Context）
function AppContent() {
  // 启用文件夹实时监控
  useFolderWatcher();
  
  // 从 Context 获取监控器实例
  const { resourceMonitor, anomalyDetector, chaosManager } = useMonitor();
  
  // 获取其他管理器（保持原有逻辑）
  const metricsCollector = getMetricsCollector();
  const userBehaviorAnalyzer = getUserBehaviorAnalyzer();
  const alertManager = getAlertManager();

  // 记录应用启动
  React.useEffect(() => {
    metricsCollector.recordUserAction('app_start', undefined, true, {
      userAgent: navigator.userAgent,
      viewport: `${window.innerWidth}x${window.innerHeight}`
    });

    // 设置用户 ID（如果有的话）
    // userBehaviorAnalyzer.setUserId('user123'); // 在实际应用中从认证系统获取

    // 记录初始资源状态
    const initialResources = resourceMonitor.getCurrentMetrics();
    alertManager.triggerManualAlert(
      'resource_usage' as any, 
      'info' as any, 
      '应用启动 - 资源状态', 
      'SysMonitor 应用启动时的系统资源状态', 
      initialResources
    );

    // 启动机器学习异常检测
    anomalyDetector.trainModel().then(() => {
      alertManager.triggerManualAlert(
        'ml_anomaly' as any,
        'info' as any,
        'ML 异常检测启动',
        '机器学习异常检测模型已训练完成并开始监控',
        { timestamp: Date.now() }
      );
    });

    // 启动混沌测试（仅在开发环境或特定条件下）
    if (import.meta.env.DEV || window.location.search.includes('chaos=true')) {
      chaosManager.startChaosTesting();
      alertManager.triggerManualAlert(
        'chaos_testing' as any,
        'info' as any,
        '混沌测试启动',
        '混沌测试已启动，将随机模拟各种故障场景',
        { timestamp: Date.now() }
      );
    }

    // 设置定期异常检测
    const anomalyDetectionInterval = setInterval(() => {
      const resources = resourceMonitor.getCurrentMetrics();
      
      // 检测资源使用异常
      anomalyDetector.addDataPoint('memory_usage', resources.memory.usage / 100);
      anomalyDetector.addDataPoint('cpu_usage', resources.cpu.usage / 100);
      
      // 检测性能异常（使用模拟数据）
      const simulatedResponseTime = Math.random() * 5000; // 模拟响应时间
      anomalyDetector.addDataPoint('response_time', simulatedResponseTime);
      
      const simulatedErrorRate = Math.random() * 0.2; // 模拟错误率
      anomalyDetector.addDataPoint('error_rate', simulatedErrorRate);
      
    }, 30000); // 每 30 秒检测一次

    // 页面卸载时发送性能报告和结束会话
    return () => {
      clearInterval(anomalyDetectionInterval);
      metricsCollector.sendPerformanceReport();
      userBehaviorAnalyzer.endSession();
      chaosManager.stopChaosTesting();
      
      // 记录最终资源状态
      const finalResources = resourceMonitor.getCurrentMetrics();
      alertManager.triggerManualAlert(
        'resource_usage' as any, 
        'info' as any, 
        '应用关闭 - 资源状态', 
        'SysMonitor 应用关闭时的系统资源状态', 
        finalResources
      );

      // 记录混沌测试结果
      if (chaosManager.isTestingActive()) {
        const chaosStats = chaosManager.getTestStats();
        alertManager.triggerManualAlert(
          'chaos_testing' as any,
          'info' as any,
          '混沌测试结束',
          '混沌测试已完成，查看测试统计',
          chaosStats
        );
      }

      // 记录异常检测统计
      const anomalyStats = anomalyDetector.getDetectionStats();
      alertManager.triggerManualAlert(
        'ml_anomaly' as any,
        'info' as any,
        'ML 异常检测结束',
        '机器学习异常检测已完成，查看检测统计',
        anomalyStats
      );
    };
  }, [metricsCollector, userBehaviorAnalyzer, alertManager, resourceMonitor, chaosManager, anomalyDetector]);

  return (
    <BrowserRouter>
      <PerformanceMonitor 
        onMetricsReport={(metrics) => {
          // 实时性能指标监控
          console.log('Performance Metrics:', metrics);
          
          // 记录到性能收集器
          metricsCollector.recordUserAction('performance_report', undefined, true, metrics);
        }}
      />
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold">SysMonitor</h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link to="/" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Dashboard
                  </Link>
                  <Link to="/folder-analysis" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Folder Analysis
                  </Link>
                  <Link to="/tools" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    高级工具
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/folder-analysis" element={<FolderAnalysisContainer />} />
            <Route path="/tools" element={<AdvancedToolsContainer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

// 主 App 组件 - 提供 MonitorContext
function App() {
  return (
    <MonitorProvider syncInterval={30000}>
      <AppContent />
    </MonitorProvider>
  );
}

export default App;
