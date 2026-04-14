import * as Sentry from "@sentry/react";

// 性能指标接口
export interface PerformanceMetrics {
  timestamp: number;
  pageLoadTime?: number;
  firstContentfulPaint?: number;
  largestContentfulPaint?: number;
  cumulativeLayoutShift?: number;
  interactionToNextPaint?: number;
  memoryUsage?: number;
  cpuUsage?: number;
  networkLatency?: number;
  userActions: UserAction[];
}

export interface UserAction {
  type: string;
  timestamp: number;
  duration?: number;
  success: boolean;
  details?: any;
}

// 指标缓冲区接口
export interface MetricsBufferItem {
  metrics: PerformanceMetrics;
  priority: 'critical' | 'normal' | 'low';
  timestamp: number;
}

// 自适应采样配置
export interface SamplingConfig {
  baseSampleRate: number; // 基础采样率 (0-1)
  minSampleRate: number; // 最低采样率
  maxSampleRate: number; // 最高采样率
  cpuThreshold: number; // CPU 阈值 (%)
  memoryThreshold: number; // 内存阈值 (MB)
  adjustmentFactor: number; // 调整因子
}

// 默认采样配置
const DEFAULT_SAMPLING_CONFIG: SamplingConfig = {
  baseSampleRate: 0.5, // 50% 基础采样率
  minSampleRate: 0.1, // 最低 10%
  maxSampleRate: 1.0, // 最高 100%
  cpuThreshold: 70, // CPU 70% 阈值
  memoryThreshold: 500, // 内存 500MB 阈值
  adjustmentFactor: 0.2 // 每次调整 20%
};

// 性能指标收集器 - 支持自适应采样和批量发送
export class MetricsCollector {
  private metrics: PerformanceMetrics;
  private userActions: UserAction[] = [];
  
  // 自适应采样相关
  private samplingConfig: SamplingConfig;
  private currentSampleRate: number;
  private systemLoad: { cpu: number; memory: number } = { cpu: 0, memory: 0 };
  
  // 批量发送相关
  private metricsBuffer: MetricsBufferItem[] = [];
  private bufferFlushInterval: number = 30000; // 30 秒刷新一次
  private maxBufferSize: number = 100; // 最大缓冲区大小
  private flushTimer: number | null = null;
  
  // 关键指标立即发送队列
  private criticalQueue: MetricsBufferItem[] = [];
  private isFlushingCritical = false;

  constructor(samplingConfig?: Partial<SamplingConfig>) {
    this.samplingConfig = { ...DEFAULT_SAMPLING_CONFIG, ...samplingConfig };
    this.currentSampleRate = this.samplingConfig.baseSampleRate;
    
    this.metrics = {
      timestamp: Date.now(),
      userActions: []
    };
    
    this.setupPerformanceObservers();
    this.setupResourceMonitoring();
    this.startBufferFlushTimer();
  }

  // ==================== 自适应采样相关 ====================
  
  /**
   * 根据系统负载动态调整采样率
   * 系统负载高时降低采样率，负载低时提高采样率
   */
  public updateSamplingRate(cpuUsage: number, memoryUsageMB: number): void {
    this.systemLoad = { cpu: cpuUsage, memory: memoryUsageMB };
    
    let targetSampleRate = this.samplingConfig.baseSampleRate;
    
    // CPU 负载过高时降低采样率
    if (cpuUsage > this.samplingConfig.cpuThreshold) {
      const cpuFactor = (cpuUsage - this.samplingConfig.cpuThreshold) / 100;
      targetSampleRate -= cpuFactor * this.samplingConfig.adjustmentFactor;
    }
    
    // 内存使用过高时降低采样率
    if (memoryUsageMB > this.samplingConfig.memoryThreshold) {
      const memoryFactor = (memoryUsageMB - this.samplingConfig.memoryThreshold) / 1000;
      targetSampleRate -= memoryFactor * this.samplingConfig.adjustmentFactor;
    }
    
    // 限制采样率在合理范围内
    this.currentSampleRate = Math.max(
      this.samplingConfig.minSampleRate,
      Math.min(this.samplingConfig.maxSampleRate, targetSampleRate)
    );
    
    // 记录采样率调整
    if (Math.abs(this.currentSampleRate - targetSampleRate) > 0.05) {
      this.logSamplingAdjustment(cpuUsage, memoryUsageMB, targetSampleRate);
    }
  }
  
  /**
   * 判断当前指标是否应该被采样
   * @ts-ignore - 预留方法，用于未来动态采样功能
   */
  // @ts-ignore - 预留方法
  private shouldSample(): boolean {
    return Math.random() <= this.currentSampleRate;
  }
  
  /**
   * 记录采样率调整日志
   */
  private logSamplingAdjustment(cpu: number, memory: number, targetRate: number): void {
    Sentry.addBreadcrumb({
      category: 'metrics.sampling',
      message: 'Sampling rate adjusted',
      level: 'info',
      data: {
        cpuUsage: cpu,
        memoryUsageMB: memory,
        previousRate: this.currentSampleRate,
        targetRate,
        systemLoad: this.getSystemLoadLevel()
      }
    });
  }
  
  /**
   * 获取系统负载等级
   */
  private getSystemLoadLevel(): 'low' | 'medium' | 'high' {
    const { cpu, memory } = this.systemLoad;
    
    if (cpu > 80 || memory > 800) return 'high';
    if (cpu > 50 || memory > 400) return 'medium';
    return 'low';
  }
  
  /**
   * 获取当前采样率
   */
  public getCurrentSampleRate(): number {
    return this.currentSampleRate;
  }
  
  /**
   * 获取系统负载状态
   */
  public getSystemLoad(): { cpu: number; memory: number; level: string } {
    return {
      ...this.systemLoad,
      level: this.getSystemLoadLevel()
    };
  }

  // ==================== 批量发送相关 ====================
  
  /**
   * 设置批量发送参数
   */
  public setBufferConfig(intervalMs: number, maxSize: number): void {
    this.bufferFlushInterval = intervalMs;
    this.maxBufferSize = maxSize;
    
    // 重启定时器
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    this.startBufferFlushTimer();
  }
  
  /**
   * 启动缓冲区刷新定时器
   */
  private startBufferFlushTimer(): void {
    this.flushTimer = window.setInterval(() => {
      this.flushBuffer();
    }, this.bufferFlushInterval);
  }
  
  /**
   * 添加指标到缓冲区
   */
  private addToBuffer(
    metrics: PerformanceMetrics,
    priority: 'critical' | 'normal' | 'low' = 'normal'
  ): void {
    const item: MetricsBufferItem = {
      metrics,
      priority,
      timestamp: Date.now()
    };
    
    // 关键指标立即发送
    if (priority === 'critical') {
      this.criticalQueue.push(item);
      this.flushCriticalQueue();
      return;
    }
    
    this.metricsBuffer.push(item);
    
    // 缓冲区满时触发刷新
    if (this.metricsBuffer.length >= this.maxBufferSize) {
      this.flushBuffer();
    }
  }
  
  /**
   * 刷新缓冲区 - 批量发送指标
   */
  private flushBuffer(): void {
    if (this.metricsBuffer.length === 0) return;
    
    // 按优先级排序
    const sortedBuffer = this.metricsBuffer.sort((a, b) => {
      const priorityOrder = { critical: 0, normal: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
    
    // 批量发送到 Sentry
    this.sendMetricsBatch(sortedBuffer);
    
    // 清空缓冲区
    this.metricsBuffer = [];
  }
  
  /**
   * 批量发送指标（使用 Beacon API 如果可用）
   */
  private sendMetricsBatch(batch: MetricsBufferItem[]): void {
    if (batch.length === 0) return;
    
    const payload = {
      timestamp: Date.now(),
      count: batch.length,
      sampleRate: this.currentSampleRate,
      metrics: batch.map(item => ({
        ...item.metrics,
        priority: item.priority
      }))
    };
    
    // 使用 Beacon API 发送（页面卸载时也能保证发送成功）
    if (this.shouldUseBeaconAPI()) {
      this.sendViaBeacon(payload);
    } else {
      this.sendViaFetch(payload);
    }
    
    Sentry.addBreadcrumb({
      category: 'metrics.batch',
      message: `Flushed ${batch.length} metrics`,
      level: 'info',
      data: {
        batchSize: batch.length,
        priorityDistribution: this.getPriorityDistribution(batch)
      }
    });
  }
  
  /**
   * 判断是否应该使用 Beacon API
   */
  private shouldUseBeaconAPI(): boolean {
    return 'sendBeacon' in navigator;
  }
  
  /**
   * 使用 Beacon API 发送
   */
  private sendViaBeacon(payload: any): void {
    const blob = new Blob([JSON.stringify(payload)], {
      type: 'application/json'
    });
    
    // 发送到日志收集端点（需要配置实际端点）
    const endpoint = '/api/metrics/batch';
    navigator.sendBeacon(endpoint, blob);
  }
  
  /**
   * 使用 fetch 发送
   */
  private sendViaFetch(payload: any): void {
    // 异步发送，不阻塞主线程
    fetch('/api/metrics/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true // 页面卸载时也能发送
    }).catch(error => {
      Sentry.captureException(error, {
        extra: { payload }
      });
    });
  }
  
  /**
   * 获取优先级分布统计
   */
  private getPriorityDistribution(batch: MetricsBufferItem[]): Record<string, number> {
    return batch.reduce((acc, item) => {
      acc[item.priority] = (acc[item.priority] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }
  
  /**
   * 立即刷新缓冲区
   */
  public forceFlush(): void {
    this.flushBuffer();
    this.flushCriticalQueue();
  }

  // ==================== 关键指标立即发送机制 ====================
  
  /**
   * 刷新关键指标队列
   */
  private async flushCriticalQueue(): Promise<void> {
    if (this.isFlushingCritical || this.criticalQueue.length === 0) return;
    
    this.isFlushingCritical = true;
    
    try {
      // 立即发送关键指标
      const criticalBatch = [...this.criticalQueue];
      this.criticalQueue = [];
      
      this.sendMetricsBatch(criticalBatch);
      
      Sentry.captureMessage('Critical metrics sent immediately', {
        level: 'info',
        extra: { count: criticalBatch.length }
      });
    } finally {
      this.isFlushingCritical = false;
    }
  }
  
  /**
   * 标记指标为关键并立即发送
   */
  public recordCriticalMetric(
    metricName: string,
    value: number,
    threshold: number,
    details?: any
  ): void {
    const metrics: PerformanceMetrics = {
      timestamp: Date.now(),
      userActions: []
    };
    
    // 根据指标名称设置对应的值
    (metrics as any)[metricName] = value;
    (metrics as any)[`${metricName}Threshold`] = threshold;
    
    this.addToBuffer(metrics, 'critical');
    
    // 发送 Sentry 警告
    Sentry.captureMessage(`Critical metric: ${metricName}`, {
      level: 'warning',
      extra: {
        metricName,
        value,
        threshold,
        exceeded: value > threshold,
        ...details
      }
    });
  }

  // ==================== 原有功能保留 ====================
  
  // 设置性能观察器
  private setupPerformanceObservers() {
    // 观察资源加载性能
    const resourceObserver = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'resource') {
          this.trackResourceLoad(entry as PerformanceResourceTiming);
        }
      });
    });
    resourceObserver.observe({ entryTypes: ['resource'] });

    // 观察长任务
    const longTaskObserver = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'longtask') {
          this.trackLongTask(entry);
        }
      });
    });
    longTaskObserver.observe({ entryTypes: ['longtask'] });

    // 观察布局偏移
    const layoutShiftObserver = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'layout-shift') {
          this.trackLayoutShift(entry as LayoutShift);
        }
      });
    });
    layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
  }

  // 设置资源监控
  private setupResourceMonitoring() {
    // 监控内存使用
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        if (memory) {
          this.metrics.memoryUsage = memory.usedJSHeapSize / 1024 / 1024; // MB
          
          // 更新采样率
          this.updateSamplingRate(this.systemLoad.cpu, this.metrics.memoryUsage);
          
          // 添加到缓冲区（低优先级）
          this.addToBuffer(
            { timestamp: Date.now(), memoryUsage: this.metrics.memoryUsage, userActions: [] },
            'low'
          );
          
          // 内存使用过高时立即发送
          if (this.metrics.memoryUsage > 800) { // 超过 800MB
            this.recordCriticalMetric('memoryUsage', this.metrics.memoryUsage, 800);
          }
        }
      }, 10000); // 每 10 秒检查一次
    }

    // 监控网络状态
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      if (connection) {
        this.metrics.networkLatency = connection.rtt;
        connection.addEventListener('change', () => {
          this.trackNetworkChange(connection);
        });
      }
    }
  }

  // 跟踪资源加载
  private trackResourceLoad(entry: PerformanceResourceTiming) {
    Sentry.addBreadcrumb({
      category: 'performance.resource',
      message: `Resource loaded: ${entry.name}`,
      level: 'info',
      data: {
        duration: entry.duration,
        size: entry.transferSize,
        type: entry.initiatorType
      }
    });
    
    // 慢资源加载记录（低优先级）
    if (entry.duration > 1000) {
      this.addToBuffer(
        {
          timestamp: Date.now(),
          networkLatency: entry.duration,
          userActions: []
        },
        'low'
      );
    }
  }

  // 跟踪长任务
  private trackLongTask(entry: PerformanceEntry) {
    // 长任务作为关键指标立即发送
    this.recordCriticalMetric('longTaskDuration', entry.duration, 100, {
      startTime: entry.startTime
    });
  }

  // 跟踪布局偏移
  private trackLayoutShift(entry: LayoutShift) {
    if (!entry.hadRecentInput) {
      this.metrics.cumulativeLayoutShift = (this.metrics.cumulativeLayoutShift || 0) + entry.value;
      
      // 显著布局偏移立即发送
      if (entry.value > 0.1) {
        this.recordCriticalMetric('cumulativeLayoutShift', entry.value, 0.1, {
          cumulative: this.metrics.cumulativeLayoutShift
        });
      }
    }
  }

  // 跟踪网络变化
  private trackNetworkChange(connection: any) {
    const networkData = {
      effectiveType: connection.effectiveType,
      rtt: connection.rtt,
      downlink: connection.downlink
    };
    
    Sentry.addBreadcrumb({
      category: 'performance.network',
      message: 'Network connection changed',
      level: 'info',
      data: networkData
    });
    
    // 网络质量差时立即发送
    if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
      this.recordCriticalMetric('networkRTT', connection.rtt, 500, networkData);
    }
  }

  // 记录用户操作
  public recordUserAction(type: string, duration?: number, success: boolean = true, details?: any) {
    const action: UserAction = {
      type,
      timestamp: Date.now(),
      duration,
      success,
      details
    };
    
    this.userActions.push(action);
    this.metrics.userActions = this.userActions;
    
    // 根据操作重要性决定优先级
    const priority = this.determineActionPriority(type, success);
    this.addToBuffer(
      { timestamp: Date.now(), userActions: [action] },
      priority
    );
    
    // 失败操作立即发送
    if (!success) {
      this.recordCriticalMetric('userActionFailed', 1, 0, { type, details });
    }
  }
  
  /**
   * 判断用户操作的优先级
   */
  private determineActionPriority(
    type: string,
    success: boolean
  ): 'critical' | 'normal' | 'low' {
    if (!success) return 'critical';
    
    const criticalActions = ['page_load', 'api_call', 'form_submit'];
    if (criticalActions.includes(type)) return 'normal';
    
    return 'low';
  }

  // 获取性能报告
  public getPerformanceReport(): PerformanceMetrics {
    const navigationTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigationTiming && navigationTiming.activationStart) {
      this.metrics.pageLoadTime = navigationTiming.loadEventEnd - navigationTiming.activationStart;
    }

    const paintEntries = performance.getEntriesByType('paint');
    paintEntries.forEach(entry => {
      if (entry.name === 'first-contentful-paint') {
        this.metrics.firstContentfulPaint = entry.startTime;
      }
    });

    const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
    if (lcpEntries.length > 0) {
      this.metrics.largestContentfulPaint = lcpEntries[lcpEntries.length - 1].startTime;
    }

    return { ...this.metrics };
  }

  // 发送性能报告到监控系统
  public sendPerformanceReport() {
    const report = this.getPerformanceReport();
    
    // 关键性能指标立即发送
    if (report.pageLoadTime && report.pageLoadTime > 3000) {
      this.recordCriticalMetric('pageLoadTime', report.pageLoadTime, 3000);
    }
    
    if (report.firstContentfulPaint && report.firstContentfulPaint > 2000) {
      this.recordCriticalMetric('firstContentfulPaint', report.firstContentfulPaint, 2000);
    }
    
    if (report.largestContentfulPaint && report.largestContentfulPaint > 2500) {
      this.recordCriticalMetric('largestContentfulPaint', report.largestContentfulPaint, 2500);
    }
    
    // 正常报告加入缓冲区
    this.addToBuffer(report, 'normal');
    
    return report;
  }

  // 记录关键性能指标
  // @ts-ignore - 预留方法，用于未来性能分析功能
  private recordKeyMetrics(report: PerformanceMetrics) {
    const criticalMetrics = [
      { name: 'Page Load Time', value: report.pageLoadTime, threshold: 3000 },
      { name: 'First Contentful Paint', value: report.firstContentfulPaint, threshold: 2000 },
      { name: 'Largest Contentful Paint', value: report.largestContentfulPaint, threshold: 2500 },
      { name: 'Cumulative Layout Shift', value: report.cumulativeLayoutShift, threshold: 0.1 }
    ];

    criticalMetrics.forEach(metric => {
      if (metric.value && metric.value > metric.threshold) {
        this.recordCriticalMetric(
          this.camelCase(metric.name),
          metric.value,
          metric.threshold
        );
      }
    });
  }
  
  /**
   * 将名称转换为驼峰命名
   */
  private camelCase(str: string): string {
    return str.charAt(0).toLowerCase() + str.slice(1).replace(/ [a-z]/g, c => c.toUpperCase().replace(' ', ''));
  }

  // 清理资源
  public destroy() {
    // 刷新所有缓冲区
    this.forceFlush();
    
    // 清除定时器
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
  }
}

// 全局指标收集器实例
let globalMetricsCollector: MetricsCollector | null = null;

export function getMetricsCollector(): MetricsCollector {
  if (!globalMetricsCollector) {
    globalMetricsCollector = new MetricsCollector();
  }
  return globalMetricsCollector;
}

export function destroyMetricsCollector() {
  if (globalMetricsCollector) {
    globalMetricsCollector.destroy();
    globalMetricsCollector = null;
  }
}
