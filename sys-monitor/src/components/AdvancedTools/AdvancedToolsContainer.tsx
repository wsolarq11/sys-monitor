import { useState, useEffect } from 'react';
import { useMonitor } from '../../contexts/MonitorContext';
import type { ChaosTestResult } from '../../utils/chaosManager';
import type { ResourceMetrics } from '../../utils/resourceMonitor';

type ToolTab = 'chaos' | 'anomaly' | 'resource';

export function AdvancedToolsContainer() {
  const [activeTab, setActiveTab] = useState<ToolTab>('chaos');
  const { resourceMonitor, anomalyDetector, chaosManager } = useMonitor();

  // Chaos Engineering 状态
  const [chaosResults, setChaosResults] = useState<ChaosTestResult[]>([]);
  const [isChaosActive, setIsChaosActive] = useState(false);

  // ML 异常检测状态
  const [anomalyStats, setAnomalyStats] = useState<any>({});

  // 资源监控状态
  const [currentMetrics, setCurrentMetrics] = useState<ResourceMetrics | null>(null);
  const [resourceStats, setResourceStats] = useState<any>({});
  const [suggestions, setSuggestions] = useState<string[]>([]);

  // 初始化混沌测试列表
  useEffect(() => {
    setIsChaosActive(chaosManager.isTestingActive());
    
    // 获取测试结果
    const results = chaosManager.getTestResults(10);
    setChaosResults(results);
  }, [chaosManager]);

  // 定期更新资源指标
  useEffect(() => {
    const updateMetrics = () => {
      const metrics = resourceMonitor.getCurrentMetrics();
      setCurrentMetrics(metrics);
      
      const stats = resourceMonitor.getResourceStats();
      setResourceStats(stats);
      
      const opts = resourceMonitor.getOptimizationSuggestions();
      setSuggestions(opts);
    };

    updateMetrics();
    const interval = setInterval(updateMetrics, 5000);
    return () => clearInterval(interval);
  }, [resourceMonitor]);

  // 定期更新异常检测统计
  useEffect(() => {
    const updateAnomalyStats = () => {
      const stats = anomalyDetector.getDetectionStats();
      setAnomalyStats(stats);
    };

    updateAnomalyStats();
    const interval = setInterval(updateAnomalyStats, 10000);
    return () => clearInterval(interval);
  }, [anomalyDetector]);

  // 切换混沌测试状态
  const handleToggleChaosTesting = () => {
    if (isChaosActive) {
      chaosManager.stopChaosTesting();
      setIsChaosActive(false);
    } else {
      chaosManager.startChaosTesting();
      setIsChaosActive(true);
    }
  };

  // 渲染标签页内容
  const renderTabContent = () => {
    switch (activeTab) {
      case 'chaos':
        return renderChaosEngineering();
      case 'anomaly':
        return renderMLAnomalyDetection();
      case 'resource':
        return renderResourceMonitoring();
      default:
        return null;
    }
  };

  // 混沌工程面板
  const renderChaosEngineering = () => {
    const stats = chaosManager.getTestStats();
    
    return (
      <div className="space-y-6">
        {/* 控制卡片 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">混沌工程控制</h3>
            <button
              onClick={handleToggleChaosTesting}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                isChaosActive
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isChaosActive ? '停止测试' : '启动测试'}
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-xs text-gray-500">总测试数</p>
              <p className="text-xl font-bold text-gray-900">{stats.totalTests || 0}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-xs text-gray-500">成功数</p>
              <p className="text-xl font-bold text-green-600">{stats.successfulTests || 0}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-xs text-gray-500">失败数</p>
              <p className="text-xl font-bold text-red-600">{stats.failedTests || 0}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-xs text-gray-500">成功率</p>
              <p className="text-xl font-bold text-blue-600">
                {(stats.successRate || 0).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        {/* 测试结果列表 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">最近测试结果</h3>
          {chaosResults.length === 0 ? (
            <p className="text-gray-500 text-center py-8">暂无测试结果</p>
          ) : (
            <div className="space-y-3">
              {chaosResults.map((result, index) => (
                <div
                  key={index}
                  className={`p-3 rounded border ${
                    result.success
                      ? 'border-green-200 bg-green-50'
                      : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{result.type}</span>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        result.impact === 'high'
                          ? 'bg-red-100 text-red-800'
                          : result.impact === 'medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {result.impact}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(result.timestamp).toLocaleTimeString()} - 
                    耗时: {result.duration}ms
                  </p>
                  {result.error && (
                    <p className="text-xs text-red-600 mt-1">{result.error}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // ML 异常检测面板
  const renderMLAnomalyDetection = () => {
    return (
      <div className="space-y-6">
        {/* 检测统计卡片 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">异常检测统计</h3>
          {Object.keys(anomalyStats).length === 0 ? (
            <p className="text-gray-500 text-center py-8">等待数据收集中...</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(anomalyStats).map(([metric, data]: [string, any]) => (
                <div key={metric} className="bg-gray-50 p-4 rounded">
                  <h4 className="font-medium text-gray-900 capitalize mb-2">{metric}</h4>
                  <div className="space-y-1 text-sm">
                    <p className="text-gray-600">
                      当前值: <span className="font-mono">{data.currentValue?.toFixed(2)}</span>
                    </p>
                    <p className="text-gray-600">
                      平均值: <span className="font-mono">{data.mean?.toFixed(2)}</span>
                    </p>
                    <p className="text-gray-600">
                      标准差: <span className="font-mono">{data.std?.toFixed(2)}</span>
                    </p>
                    <p className="text-gray-600">
                      阈值: <span className="font-mono">{data.threshold}</span>
                    </p>
                    <p className="text-gray-600">
                      数据点: <span className="font-mono">{data.dataPoints}</span>
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 模型训练状态 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">模型状态</h3>
          <div className="flex items-center space-x-4">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '100%' }}></div>
            </div>
            <span className="text-sm text-gray-600">已训练</span>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            ML 异常检测模型正在运行，持续监控系统指标异常
          </p>
        </div>
      </div>
    );
  };

  // 资源监控面板
  const renderResourceMonitoring = () => {
    if (!currentMetrics) {
      return (
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-center py-8">加载中...</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* 实时指标卡片 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">实时资源指标</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* CPU */}
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="text-sm font-medium text-gray-600 mb-2">CPU 使用率</h4>
              <div className="flex items-end space-x-2">
                <span className="text-3xl font-bold text-gray-900">
                  {currentMetrics.cpu.usage.toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500">
                  ({currentMetrics.cpu.cores} 核心)
                </span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    currentMetrics.cpu.usage > 90
                      ? 'bg-red-600'
                      : currentMetrics.cpu.usage > 70
                      ? 'bg-yellow-600'
                      : 'bg-green-600'
                  }`}
                  style={{ width: `${Math.min(currentMetrics.cpu.usage, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* 内存 */}
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="text-sm font-medium text-gray-600 mb-2">内存使用率</h4>
              <div className="flex items-end space-x-2">
                <span className="text-3xl font-bold text-gray-900">
                  {currentMetrics.memory.usage.toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500">
                  ({(currentMetrics.memory.used / 1024).toFixed(1)} GB / {(currentMetrics.memory.total / 1024).toFixed(1)} GB)
                </span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    currentMetrics.memory.usage > 80
                      ? 'bg-red-600'
                      : currentMetrics.memory.usage > 60
                      ? 'bg-yellow-600'
                      : 'bg-green-600'
                  }`}
                  style={{ width: `${Math.min(currentMetrics.memory.usage, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* 存储 */}
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="text-sm font-medium text-gray-600 mb-2">存储使用率</h4>
              <div className="flex items-end space-x-2">
                <span className="text-3xl font-bold text-gray-900">
                  {currentMetrics.storage.usage.toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500">
                  ({(currentMetrics.storage.used / 1024).toFixed(1)} GB / {(currentMetrics.storage.total / 1024).toFixed(1)} GB)
                </span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    currentMetrics.storage.usage > 85
                      ? 'bg-red-600'
                      : currentMetrics.storage.usage > 70
                      ? 'bg-yellow-600'
                      : 'bg-green-600'
                  }`}
                  style={{ width: `${Math.min(currentMetrics.storage.usage, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* 网络和电池信息 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="text-sm font-medium text-gray-600 mb-2">网络状态</h4>
              <p className="text-sm text-gray-900">
                类型: <span className="font-mono">{currentMetrics.network.effectiveType}</span>
              </p>
              <p className="text-sm text-gray-900">
                下行速度: <span className="font-mono">{currentMetrics.network.downlink} Mbps</span>
              </p>
              <p className="text-sm text-gray-900">
                RTT: <span className="font-mono">{currentMetrics.network.rtt} ms</span>
              </p>
            </div>

            {currentMetrics.battery && (
              <div className="bg-gray-50 p-4 rounded">
                <h4 className="text-sm font-medium text-gray-600 mb-2">电池状态</h4>
                <p className="text-sm text-gray-900">
                  电量: <span className="font-mono">{currentMetrics.battery.level.toFixed(0)}%</span>
                </p>
                <p className="text-sm text-gray-900">
                  状态: <span className="font-mono">
                    {currentMetrics.battery.charging ? '充电中' : '放电中'}
                  </span>
                </p>
              </div>
            )}
          </div>
        </div>

        {/* 历史统计 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">历史统计</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="text-sm font-medium text-gray-600 mb-2">CPU</h4>
              <p className="text-xs text-gray-500">平均: {resourceStats.cpu?.average?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">最高: {resourceStats.cpu?.max?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">最低: {resourceStats.cpu?.min?.toFixed(1)}%</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="text-sm font-medium text-gray-600 mb-2">内存</h4>
              <p className="text-xs text-gray-500">平均: {resourceStats.memory?.average?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">最高: {resourceStats.memory?.max?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">最低: {resourceStats.memory?.min?.toFixed(1)}%</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="text-sm font-medium text-gray-600 mb-2">存储</h4>
              <p className="text-xs text-gray-500">平均: {resourceStats.storage?.average?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">最高: {resourceStats.storage?.max?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">最低: {resourceStats.storage?.min?.toFixed(1)}%</p>
            </div>
          </div>
        </div>

        {/* 优化建议 */}
        {suggestions.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">优化建议</h3>
            <ul className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <svg
                    className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm text-gray-700">{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">高级监控工具</h2>
        <p className="text-sm text-gray-500 mt-1">
          混沌工程、ML 异常检测和系统资源监控
        </p>
      </div>

      {/* 标签页导航 */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('chaos')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'chaos'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            混沌工程
          </button>
          <button
            onClick={() => setActiveTab('anomaly')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'anomaly'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            ML 异常检测
          </button>
          <button
            onClick={() => setActiveTab('resource')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'resource'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            资源监控
          </button>
        </nav>
      </div>

      {/* 标签页内容 */}
      {renderTabContent()}
    </div>
  );
}
