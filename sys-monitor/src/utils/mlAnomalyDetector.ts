import * as Sentry from "@sentry/react";

// 异常检测结果接口
export interface AnomalyDetectionResult {
  timestamp: number;
  metric: string;
  value: number;
  predictedValue?: number;
  anomalyScore: number; // 0-1 异常分数
  isAnomaly: boolean;
  confidence: number; // 0-1 置信度
  severity: 'low' | 'medium' | 'high' | 'critical';
  explanation?: string;
}

// 异常检测配置接口
export interface AnomalyDetectionConfig {
  metric: string;
  threshold: number; // 异常阈值
  windowSize: number; // 时间窗口大小
  minSamples: number; // 最小样本数
  sensitivity: number; // 灵敏度 0-1
}

// 时间序列数据点
export interface TimeSeriesPoint {
  timestamp: number;
  value: number;
}

// 机器学习异常检测器
export class MLAnomalyDetector {
  private configs: Map<string, AnomalyDetectionConfig> = new Map();
  private dataHistory: Map<string, TimeSeriesPoint[]> = new Map();
  private maxHistorySize = 1000;
  private isTraining = false;

  constructor() {
    this.setupDefaultConfigs();
  }

  // 设置默认配置
  private setupDefaultConfigs() {
    this.addConfig({
      metric: 'memory_usage',
      threshold: 0.8,
      windowSize: 10,
      minSamples: 5,
      sensitivity: 0.7
    });

    this.addConfig({
      metric: 'cpu_usage',
      threshold: 0.85,
      windowSize: 10,
      minSamples: 5,
      sensitivity: 0.6
    });

    this.addConfig({
      metric: 'response_time',
      threshold: 3000, // 3秒
      windowSize: 15,
      minSamples: 8,
      sensitivity: 0.8
    });

    this.addConfig({
      metric: 'error_rate',
      threshold: 0.1, // 10%
      windowSize: 20,
      minSamples: 10,
      sensitivity: 0.9
    });
  }

  // 添加检测配置
  public addConfig(config: AnomalyDetectionConfig) {
    this.configs.set(config.metric, config);
    this.dataHistory.set(config.metric, []);
  }

  // 添加数据点
  public addDataPoint(metric: string, value: number, timestamp: number = Date.now()) {
    const dataPoint: TimeSeriesPoint = { timestamp, value };
    
    if (!this.dataHistory.has(metric)) {
      this.dataHistory.set(metric, []);
    }
    
    const history = this.dataHistory.get(metric)!;
    history.push(dataPoint);
    
    // 限制历史数据大小
    if (history.length > this.maxHistorySize) {
      this.dataHistory.set(metric, history.slice(-this.maxHistorySize));
    }

    // 检测异常
    return this.detectAnomaly(metric, value, timestamp);
  }

  // 检测异常
  private detectAnomaly(metric: string, value: number, timestamp: number): AnomalyDetectionResult | null {
    const config = this.configs.get(metric);
    if (!config) return null;

    const history = this.dataHistory.get(metric)!;
    
    // 确保有足够的数据
    if (history.length < config.minSamples) {
      return null;
    }

    // 计算异常分数
    const anomalyScore = this.calculateAnomalyScore(metric, value, config);
    const isAnomaly = anomalyScore > config.threshold;
    
    if (!isAnomaly) return null;

    // 计算置信度
    const confidence = this.calculateConfidence(metric, value, config);
    
    // 确定严重程度
    const severity = this.determineSeverity(anomalyScore, config);
    
    // 生成解释
    const explanation = this.generateExplanation(metric, value, anomalyScore, severity);

    const result: AnomalyDetectionResult = {
      timestamp,
      metric,
      value,
      anomalyScore,
      isAnomaly,
      confidence,
      severity,
      explanation
    };

    // 发送异常警报
    this.sendAnomalyAlert(result);

    return result;
  }

  // 计算异常分数
  private calculateAnomalyScore(metric: string, currentValue: number, config: AnomalyDetectionConfig): number {
    const history = this.dataHistory.get(metric)!;
    const recentData = history.slice(-config.windowSize);
    
    if (recentData.length === 0) return 0;

    // 计算统计特征
    const values = recentData.map(d => d.value);
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const std = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length);
    
    // 处理标准差为0的情况
    if (std === 0) {
      return currentValue === mean ? 0 : 1;
    }

    // 使用Z-score方法
    const zScore = Math.abs((currentValue - mean) / std);
    
    // 使用移动平均方法
    const movingAvg = this.calculateMovingAverage(history, config.windowSize);
    const movingAvgDiff = Math.abs(currentValue - movingAvg) / (movingAvg || 1);
    
    // 结合多种方法
    const combinedScore = (zScore * 0.6 + movingAvgDiff * 0.4) * config.sensitivity;
    
    return Math.min(combinedScore, 1);
  }

  // 计算移动平均
  private calculateMovingAverage(history: TimeSeriesPoint[], windowSize: number): number {
    if (history.length === 0) return 0;
    
    const recentData = history.slice(-windowSize);
    const sum = recentData.reduce((total, point) => total + point.value, 0);
    return sum / recentData.length;
  }

  // 计算置信度
  private calculateConfidence(metric: string, currentValue: number, config: AnomalyDetectionConfig): number {
    const history = this.dataHistory.get(metric)!;
    
    // 基于数据量计算置信度
    const dataCountConfidence = Math.min(history.length / config.minSamples, 1);
    
    // 基于数据稳定性计算置信度
    const stabilityConfidence = this.calculateStabilityConfidence(history, config.windowSize);
    
    // 基于异常模式计算置信度
    const patternConfidence = this.calculatePatternConfidence(metric, currentValue);
    
    return (dataCountConfidence * 0.4 + stabilityConfidence * 0.4 + patternConfidence * 0.2);
  }

  // 计算稳定性置信度
  private calculateStabilityConfidence(history: TimeSeriesPoint[], windowSize: number): number {
    if (history.length < 2) return 0;
    
    const recentData = history.slice(-windowSize);
    const values = recentData.map(d => d.value);
    
    // 计算变异系数
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const std = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length);
    
    const coefficientOfVariation = std / (mean || 1);
    
    // 变异系数越小，稳定性越高
    return Math.max(0, 1 - coefficientOfVariation);
  }

  // 计算模式置信度
  private calculatePatternConfidence(metric: string, currentValue: number): number {
    // 这里可以实现更复杂的模式识别
    // 目前使用简单的季节性模式检测
    
    const history = this.dataHistory.get(metric)!;
    if (history.length < 24) return 0.5; // 数据不足，返回中等置信度
    
    // 检查最近的值是否与历史模式一致
    const recentPattern = this.analyzeRecentPattern(history);
    const isConsistent = this.checkPatternConsistency(currentValue, recentPattern);
    
    return isConsistent ? 0.8 : 0.3;
  }

  // 分析最近模式
  private analyzeRecentPattern(history: TimeSeriesPoint[]): any {
    // 简单的模式分析：计算最近几个时间点的趋势
    const recentData = history.slice(-6); // 最近6个点
    const values = recentData.map(d => d.value);
    
    // 计算趋势（简单线性回归斜率）
    const n = values.length;
    const x = Array.from({length: n}, (_, i) => i);
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = values.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((a, _, i) => a + i * values[i], 0);
    const sumX2 = x.reduce((a, b) => a + b * b, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    
    return {
      trend: slope > 0 ? 'increasing' : slope < 0 ? 'decreasing' : 'stable',
      magnitude: Math.abs(slope)
    };
  }

  // 检查模式一致性
  private checkPatternConsistency(_currentValue: number, _pattern: any): boolean {
    // 简单的模式一致性检查
    // 在实际应用中可以实现更复杂的逻辑
    
    return true; // 暂时返回true
  }

  // 确定严重程度
  private determineSeverity(anomalyScore: number, config: AnomalyDetectionConfig): 'low' | 'medium' | 'high' | 'critical' {
    const normalizedScore = anomalyScore / config.threshold;
    
    if (normalizedScore < 1.2) return 'low';
    if (normalizedScore < 1.5) return 'medium';
    if (normalizedScore < 2.0) return 'high';
    return 'critical';
  }

  // 生成解释
  private generateExplanation(metric: string, value: number, anomalyScore: number, severity: string): string {
    const explanations: Record<string, string> = {
      'memory_usage': `内存使用异常：当前使用率 ${(value * 100).toFixed(1)}%，超出正常范围`,
      'cpu_usage': `CPU使用异常：当前使用率 ${(value * 100).toFixed(1)}%，超出正常范围`,
      'response_time': `响应时间异常：当前响应时间 ${value.toFixed(0)}ms，超出正常范围`,
      'error_rate': `错误率异常：当前错误率 ${(value * 100).toFixed(1)}%，超出正常范围`
    };

    return explanations[metric] || `检测到 ${metric} 指标异常，异常分数：${anomalyScore.toFixed(3)}，严重程度：${severity}`;
  }

  // 发送异常警报
  private sendAnomalyAlert(result: AnomalyDetectionResult) {
    const sentryLevel = this.mapSeverityToSentryLevel(result.severity);
    
    Sentry.captureMessage(`ML异常检测警报: ${result.metric}`, {
      level: sentryLevel,
      extra: {
        ...result,
        timestamp: new Date(result.timestamp).toISOString()
      }
    });

    // 设置异常上下文
    Sentry.withScope(scope => {
      scope.setTag('anomaly_metric', result.metric);
      scope.setTag('anomaly_severity', result.severity);
      scope.setExtra('anomaly_score', result.anomalyScore);
      scope.setExtra('confidence', result.confidence);
    });
  }

  // 映射严重程度到Sentry级别
  private mapSeverityToSentryLevel(severity: string): Sentry.SeverityLevel {
    switch (severity) {
      case 'low': return 'info';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'fatal';
      default: return 'error';
    }
  }

  // 批量检测异常
  public batchDetectAnomalies(metrics: Array<{metric: string, value: number}>): AnomalyDetectionResult[] {
    const results: AnomalyDetectionResult[] = [];
    
    for (const item of metrics) {
      const result = this.addDataPoint(item.metric, item.value);
      if (result) {
        results.push(result);
      }
    }
    
    return results;
  }

  // 获取历史数据
  public getHistory(metric: string, limit?: number): TimeSeriesPoint[] {
    const history = this.dataHistory.get(metric) || [];
    return limit ? history.slice(-limit) : [...history];
  }

  // 获取检测统计
  public getDetectionStats(): any {
    const stats: any = {};
    
    for (const [metric, history] of this.dataHistory) {
      const config = this.configs.get(metric);
      if (!config) continue;
      
      const recentData = history.slice(-config.windowSize);
      const values = recentData.map(d => d.value);
      
      if (values.length === 0) continue;
      
      const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
      const std = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length);
      
      stats[metric] = {
        dataPoints: history.length,
        currentValue: values[values.length - 1],
        mean: mean,
        std: std,
        threshold: config.threshold
      };
    }
    
    return stats;
  }

  // 训练模型（占位方法）
  public async trainModel(): Promise<void> {
    if (this.isTraining) return;
    
    this.isTraining = true;
    
    try {
      // 在实际应用中，这里会实现真正的模型训练逻辑
      // 目前只是模拟训练过程
      
      Sentry.captureMessage('ML模型训练开始', {
        level: 'info',
        extra: { metrics: Array.from(this.configs.keys()) }
      });
      
      // 模拟训练时间
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Sentry.captureMessage('ML模型训练完成', {
        level: 'info',
        extra: { trainedMetrics: Array.from(this.configs.keys()) }
      });
      
    } finally {
      this.isTraining = false;
    }
  }

  // 预测未来值（占位方法）
  public predict(metric: string, steps: number = 1): number[] {
    const history = this.dataHistory.get(metric);
    if (!history || history.length === 0) {
      return Array(steps).fill(0);
    }
    
    // 简单的预测：使用最近值的移动平均
    const recentValues = history.slice(-5).map(d => d.value);
    const avg = recentValues.reduce((sum, val) => sum + val, 0) / recentValues.length;
    
    return Array(steps).fill(avg);
  }

  // 销毁检测器
  public destroy() {
    this.configs.clear();
    this.dataHistory.clear();
  }
}

// 全局异常检测器实例
let globalAnomalyDetector: MLAnomalyDetector | null = null;

export function getAnomalyDetector(): MLAnomalyDetector {
  if (!globalAnomalyDetector) {
    globalAnomalyDetector = new MLAnomalyDetector();
  }
  return globalAnomalyDetector;
}

export function destroyAnomalyDetector() {
  if (globalAnomalyDetector) {
    globalAnomalyDetector.destroy();
    globalAnomalyDetector = null;
  }
}