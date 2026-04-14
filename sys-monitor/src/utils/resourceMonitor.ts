import * as Sentry from "@sentry/react";
import { getMetricsCollector } from './metricsCollector';

// 资源使用指标接口
export interface ResourceMetrics {
  timestamp: number;
  memory: MemoryMetrics;
  cpu: CpuMetrics;
  network: NetworkMetrics;
  storage: StorageMetrics;
  battery?: BatteryMetrics;
}

export interface MemoryMetrics {
  used: number; // MB
  total: number; // MB
  usage: number; // 百分比
  heapUsed?: number; // JS 堆使用量 (MB)
  heapTotal?: number; // JS 堆总量 (MB)
}

export interface CpuMetrics {
  usage: number; // 百分比
  cores: number;
  loadAverage?: number[]; // 负载平均值
}

export interface NetworkMetrics {
  downlink: number; // Mbps
  effectiveType: string;
  rtt: number; // 毫秒
  connectionType?: string;
}

export interface StorageMetrics {
  used: number; // MB
  total: number; // MB
  usage: number; // 百分比
  quota?: number; // 存储配额 (MB)
}

export interface BatteryMetrics {
  level: number; // 百分比
  charging: boolean;
  chargingTime?: number; // 充电时间 (秒)
  dischargingTime?: number; // 放电时间 (秒)
}

// 监控频率配置
export interface MonitoringFrequencyConfig {
  baseInterval: number; // 基础监控间隔 (ms)
  minInterval: number; // 最小监控间隔
  maxInterval: number; // 最大监控间隔
  adaptiveEnabled: boolean; // 是否启用自适应频率
  cpuThreshold: number; // CPU 阈值 (%)
  memoryThreshold: number; // 内存阈值 (MB)
  batteryLowThreshold: number; // 低电量阈值 (%)
}

// 默认监控频率配置
const DEFAULT_FREQUENCY_CONFIG: MonitoringFrequencyConfig = {
  baseInterval: 30000, // 30 秒基础间隔
  minInterval: 5000, // 最小 5 秒（高负载时）
  maxInterval: 60000, // 最大 60 秒（低负载时）
  adaptiveEnabled: true, // 启用自适应频率
  cpuThreshold: 70,
  memoryThreshold: 500,
  batteryLowThreshold: 20
};

// 资源监控器 - 支持自适应监控频率
export class ResourceMonitor {
  private metrics: ResourceMetrics;
  private monitoringInterval: number | null = null;
  private isMonitoring = false;
  
  // 自适应频率相关
  private frequencyConfig: MonitoringFrequencyConfig;
  private currentInterval: number;
  private systemLoadLevel: 'low' | 'medium' | 'high' = 'low';
  
  // 历史指标用于趋势分析
  private metricsHistory: ResourceMetrics[] = [];
  private maxHistorySize: number = 60; // 保留 60 个历史数据点
  
  // 回调函数
  private onCriticalResourceAlert?: (type: string, value: number, threshold: number) => void;

  constructor(frequencyConfig?: Partial<MonitoringFrequencyConfig>) {
    this.frequencyConfig = { ...DEFAULT_FREQUENCY_CONFIG, ...frequencyConfig };
    this.currentInterval = this.frequencyConfig.baseInterval;
    
    this.metrics = {
      timestamp: Date.now(),
      memory: { used: 0, total: 0, usage: 0 },
      cpu: { usage: 0, cores: navigator.hardwareConcurrency || 1 },
      network: { downlink: 0, effectiveType: 'unknown', rtt: 0 },
      storage: { used: 0, total: 0, usage: 0 }
    };

    this.setupResourceMonitoring();
  }
  
  /**
   * 设置关键资源警报回调
   */
  public setCriticalAlertCallback(
    callback: (type: string, value: number, threshold: number) => void
  ): void {
    this.onCriticalResourceAlert = callback;
  }

  // ==================== 自适应监控频率相关 ====================
  
  /**
   * 根据系统负载动态调整监控频率
   * 系统负载高时提高频率（更频繁监控），负载低时降低频率
   */
  private adjustMonitoringFrequency(): void {
    if (!this.frequencyConfig.adaptiveEnabled) {
      this.currentInterval = this.frequencyConfig.baseInterval;
      return;
    }
    
    const { cpu, memory, battery } = this.metrics;
    let targetInterval = this.frequencyConfig.baseInterval;
    
    // 根据 CPU 使用率调整
    if (cpu.usage > this.frequencyConfig.cpuThreshold) {
      // CPU 高负载时提高监控频率
      const cpuFactor = (cpu.usage - this.frequencyConfig.cpuThreshold) / 100;
      targetInterval -= cpuFactor * 15000; // 最多减少 15 秒
    }
    
    // 根据内存使用率调整
    if (memory.usage > 70) {
      // 内存高使用率时提高监控频率
      const memoryFactor = (memory.usage - 70) / 100;
      targetInterval -= memoryFactor * 10000; // 最多减少 10 秒
    }
    
    // 根据电池状态调整
    if (battery && battery.level < this.frequencyConfig.batteryLowThreshold && !battery.charging) {
      // 低电量时降低监控频率以节省电量
      targetInterval = Math.min(targetInterval + 15000, this.frequencyConfig.maxInterval);
    }
    
    // 限制在合理范围内
    this.currentInterval = Math.max(
      this.frequencyConfig.minInterval,
      Math.min(this.frequencyConfig.maxInterval, targetInterval)
    );
    
    // 更新系统负载等级
    this.updateSystemLoadLevel();
    
    // 记录频率调整
    this.logFrequencyAdjustment();
  }
  
  /**
   * 更新系统负载等级
   */
  private updateSystemLoadLevel(): void {
    const { cpu, memory } = this.metrics;
    
    if (cpu.usage > 80 || memory.usage > 80) {
      this.systemLoadLevel = 'high';
    } else if (cpu.usage > 50 || memory.usage > 50) {
      this.systemLoadLevel = 'medium';
    } else {
      this.systemLoadLevel = 'low';
    }
  }
  
  /**
   * 记录频率调整日志
   */
  private logFrequencyAdjustment(): void {
    Sentry.addBreadcrumb({
      category: 'resource.frequency',
      message: 'Monitoring frequency adjusted',
      level: 'info',
      data: {
        cpuUsage: this.metrics.cpu.usage,
        memoryUsage: this.metrics.memory.usage,
        batteryLevel: this.metrics.battery?.level,
        previousInterval: this.monitoringInterval,
        newInterval: this.currentInterval,
        systemLoadLevel: this.systemLoadLevel
      }
    });
  }
  
  /**
   * 获取当前监控频率
   */
  public getCurrentInterval(): number {
    return this.currentInterval;
  }
  
  /**
   * 获取系统负载等级
   */
  public getSystemLoadLevel(): string {
    return this.systemLoadLevel;
  }
  
  /**
   * 设置监控频率配置
   */
  public setFrequencyConfig(config: Partial<MonitoringFrequencyConfig>): void {
    this.frequencyConfig = { ...this.frequencyConfig, ...config };
    
    // 重启监控以应用新配置
    if (this.isMonitoring) {
      this.stopMonitoring();
      this.startPeriodicMonitoring();
    }
  }

  // ==================== 资源监控核心功能 ====================
  
  // 设置资源监控
  private setupResourceMonitoring() {
    // 监控内存使用
    this.setupMemoryMonitoring();
    
    // 监控网络状态
    this.setupNetworkMonitoring();
    
    // 监控存储使用
    this.setupStorageMonitoring();
    
    // 监控电池状态（如果可用）
    this.setupBatteryMonitoring();
    
    // 开始定期监控
    this.startPeriodicMonitoring();
  }

  // 设置内存监控
  private setupMemoryMonitoring() {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      if (memory) {
        this.metrics.memory.heapUsed = memory.usedJSHeapSize / 1024 / 1024;
        this.metrics.memory.heapTotal = memory.totalJSHeapSize / 1024 / 1024;
      }
    }

    // 模拟系统内存使用（在实际应用中可以从系统 API 获取）
    this.metrics.memory.total = 8192; // 8GB 模拟
    this.metrics.memory.used = Math.random() * 4096; // 随机使用量
    this.metrics.memory.usage = (this.metrics.memory.used / this.metrics.memory.total) * 100;
  }

  // 设置网络监控
  private setupNetworkMonitoring() {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      if (connection) {
        this.metrics.network = {
          downlink: connection.downlink || 0,
          effectiveType: connection.effectiveType || 'unknown',
          rtt: connection.rtt || 0,
          connectionType: connection.type || 'unknown'
        };

        // 监听网络变化
        connection.addEventListener('change', () => {
          this.handleNetworkChange(connection);
        });
      }
    }
  }

  // 设置存储监控
  private setupStorageMonitoring() {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      navigator.storage.estimate().then(estimate => {
        this.metrics.storage = {
          used: (estimate.usage || 0) / 1024 / 1024,
          total: (estimate.quota || 0) / 1024 / 1024,
          usage: estimate.quota ? ((estimate.usage || 0) / estimate.quota) * 100 : 0,
          quota: (estimate.quota || 0) / 1024 / 1024
        };
      }).catch(error => {
        console.error('Storage estimation failed:', error);
      });
    }

    // 模拟存储使用
    this.metrics.storage.total = 102400; // 100GB 模拟
    this.metrics.storage.used = Math.random() * 51200; // 随机使用量
    this.metrics.storage.usage = (this.metrics.storage.used / this.metrics.storage.total) * 100;
  }

  // 设置电池监控
  private setupBatteryMonitoring() {
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        this.updateBatteryMetrics(battery);
        
        battery.addEventListener('levelchange', () => {
          this.updateBatteryMetrics(battery);
          this.adjustMonitoringFrequency(); // 电池变化时调整频率
        });
        
        battery.addEventListener('chargingchange', () => {
          this.updateBatteryMetrics(battery);
          this.adjustMonitoringFrequency();
        });
        
        battery.addEventListener('chargingtimechange', () => {
          this.updateBatteryMetrics(battery);
        });
        
        battery.addEventListener('dischargingtimechange', () => {
          this.updateBatteryMetrics(battery);
        });
      }).catch((error: any) => {
        console.error('Battery monitoring not supported:', error);
      });
    }
  }

  // 更新电池指标
  private updateBatteryMetrics(battery: any) {
    this.metrics.battery = {
      level: battery.level * 100,
      charging: battery.charging,
      chargingTime: battery.chargingTime,
      dischargingTime: battery.dischargingTime
    };
  }

  // 处理网络变化
  private handleNetworkChange(connection: any) {
    this.metrics.network = {
      downlink: connection.downlink || 0,
      effectiveType: connection.effectiveType || 'unknown',
      rtt: connection.rtt || 0,
      connectionType: connection.type || 'unknown'
    };

    Sentry.addBreadcrumb({
      category: 'resource.network',
      message: 'Network connection changed',
      level: 'info',
      data: this.metrics.network
    });
    
    // 网络质量差时触发关键警报
    if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
      this.triggerCriticalAlert('network', connection.rtt, 500);
    }
  }

  // 开始定期监控
  private startPeriodicMonitoring() {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    
    // 使用自适应间隔进行监控
    this.monitoringInterval = window.setInterval(() => {
      this.updateMetrics();
      this.adjustMonitoringFrequency(); // 每次更新后调整频率
      this.checkResourceThresholds();
      this.sendMetricsToSentry();
      this.syncWithMetricsCollector(); // 与指标收集器同步
    }, this.currentInterval);
  }
  
  /**
   * 与 MetricsCollector 同步系统负载数据
   */
  private syncWithMetricsCollector(): void {
    const collector = getMetricsCollector();
    collector.updateSamplingRate(this.metrics.cpu.usage, this.metrics.memory.heapUsed || 0);
  }

  // 更新指标
  private updateMetrics() {
    this.metrics.timestamp = Date.now();
    
    // 更新内存使用
    this.setupMemoryMonitoring();
    
    // 更新 CPU 使用（模拟）
    this.metrics.cpu.usage = Math.random() * 100;
    
    // 更新网络状态
    this.setupNetworkMonitoring();
    
    // 更新存储使用
    this.setupStorageMonitoring();
    
    // 添加到历史记录
    this.addToHistory({ ...this.metrics });
  }
  
  /**
   * 添加指标到历史记录
   */
  private addToHistory(metrics: ResourceMetrics): void {
    this.metricsHistory.push(metrics);
    
    // 保持历史记录大小在限制内
    if (this.metricsHistory.length > this.maxHistorySize) {
      this.metricsHistory.shift();
    }
  }

  // 检查资源阈值
  private checkResourceThresholds() {
    // 内存使用过高警告
    if (this.metrics.memory.usage > 80) {
      this.triggerResourceAlert('memory', this.metrics.memory.usage, 80);
      this.triggerCriticalAlert('memory', this.metrics.memory.usage, 80);
    }
    
    // CPU 使用过高警告
    if (this.metrics.cpu.usage > 90) {
      this.triggerResourceAlert('cpu', this.metrics.cpu.usage, 90);
      this.triggerCriticalAlert('cpu', this.metrics.cpu.usage, 90);
    }
    
    // 存储使用过高警告
    if (this.metrics.storage.usage > 85) {
      this.triggerResourceAlert('storage', this.metrics.storage.usage, 85);
      this.triggerCriticalAlert('storage', this.metrics.storage.usage, 85);
    }
    
    // 网络连接质量差警告
    if (this.metrics.network.effectiveType === 'slow-2g' || this.metrics.network.effectiveType === '2g') {
      this.triggerResourceAlert('network', 0, 0, this.metrics.network.effectiveType);
    }
    
    // 电池电量低警告
    if (this.metrics.battery && this.metrics.battery.level < 20 && !this.metrics.battery.charging) {
      this.triggerResourceAlert('battery', this.metrics.battery.level, 20);
      this.triggerCriticalAlert('battery', this.metrics.battery.level, 20);
    }
  }
  
  /**
   * 触发关键资源警报（立即发送）
   */
  private triggerCriticalAlert(type: string, current: number, threshold: number): void {
    if (this.onCriticalResourceAlert) {
      this.onCriticalResourceAlert(type, current, threshold);
    }
  }

  // 触发资源警报
  private triggerResourceAlert(type: string, current: number, threshold: number, details?: string) {
    const message = details 
      ? `${type} resource issue: ${details}`
      : `${type} usage high: ${current.toFixed(1)}% (threshold: ${threshold}%)`;
    
    Sentry.captureMessage(`Resource alert: ${message}`, {
      level: 'warning',
      extra: {
        resourceType: type,
        currentValue: current,
        threshold: threshold,
        details: details
      }
    });
  }

  // 发送指标到 Sentry
  private sendMetricsToSentry() {
    Sentry.addBreadcrumb({
      category: 'resource.metrics',
      message: 'Resource metrics update',
      level: 'info',
      data: {
        memoryUsage: this.metrics.memory.usage,
        cpuUsage: this.metrics.cpu.usage,
        storageUsage: this.metrics.storage.usage,
        networkType: this.metrics.network.effectiveType,
        batteryLevel: this.metrics.battery?.level,
        monitoringInterval: this.currentInterval,
        systemLoadLevel: this.systemLoadLevel
      }
    });

    // 定期发送详细指标（10% 概率）
    if (Math.random() < 0.1) {
      Sentry.captureMessage('Resource usage report', {
        level: 'info',
        extra: {
          ...this.metrics,
          memory: this.metrics.memory.usage,
          cpu: this.metrics.cpu.usage,
          storage: this.metrics.storage.usage
        }
      });
    }
  }

  // ==================== 公开 API ====================
  
  // 获取当前资源指标
  public getCurrentMetrics(): ResourceMetrics {
    return { ...this.metrics };
  }

  // 获取资源使用趋势
  public getResourceTrends(_duration: number = 300000): ResourceMetrics[] {
    // 返回历史数据
    return [...this.metricsHistory].sort((a, b) => a.timestamp - b.timestamp);
  }

  // 获取资源使用统计
  public getResourceStats(): any {
    const trends = this.getResourceTrends();
    
    if (trends.length === 0) {
      return {
        memory: { average: 0, max: 0, min: 0 },
        cpu: { average: 0, max: 0, min: 0 },
        storage: { average: 0, max: 0, min: 0 }
      };
    }
    
    const memoryAvg = trends.reduce((sum, metric) => sum + metric.memory.usage, 0) / trends.length;
    const cpuAvg = trends.reduce((sum, metric) => sum + metric.cpu.usage, 0) / trends.length;
    const storageAvg = trends.reduce((sum, metric) => sum + metric.storage.usage, 0) / trends.length;
    
    return {
      memory: {
        average: memoryAvg,
        max: Math.max(...trends.map(m => m.memory.usage)),
        min: Math.min(...trends.map(m => m.memory.usage))
      },
      cpu: {
        average: cpuAvg,
        max: Math.max(...trends.map(m => m.cpu.usage)),
        min: Math.min(...trends.map(m => m.cpu.usage))
      },
      storage: {
        average: storageAvg,
        max: Math.max(...trends.map(m => m.storage.usage)),
        min: Math.min(...trends.map(m => m.storage.usage))
      }
    };
  }

  // 优化资源使用建议
  public getOptimizationSuggestions(): string[] {
    const suggestions: string[] = [];
    
    if (this.metrics.memory.usage > 80) {
      suggestions.push('内存使用过高，建议关闭不必要的标签页或应用程序');
    }
    
    if (this.metrics.cpu.usage > 90) {
      suggestions.push('CPU 使用过高，建议减少同时运行的任务数量');
    }
    
    if (this.metrics.storage.usage > 85) {
      suggestions.push('存储空间不足，建议清理不必要的文件');
    }
    
    if (this.metrics.network.effectiveType === 'slow-2g' || this.metrics.network.effectiveType === '2g') {
      suggestions.push('网络连接质量较差，建议切换到更稳定的网络');
    }
    
    if (this.metrics.battery && this.metrics.battery.level < 20 && !this.metrics.battery.charging) {
      suggestions.push('电池电量低，建议连接电源');
    }
    
    // 根据系统负载等级提供建议
    if (this.systemLoadLevel === 'high') {
      suggestions.push('系统负载较高，建议减少并发任务或优化资源使用');
    }
    
    return suggestions;
  }
  
  /**
   * 设置历史记录最大大小
   */
  public setMaxHistorySize(size: number): void {
    this.maxHistorySize = size;
    
    // 如果当前历史记录超出限制，截断
    if (this.metricsHistory.length > size) {
      this.metricsHistory = this.metricsHistory.slice(-size);
    }
  }
  
  /**
   * 清除历史记录
   */
  public clearHistory(): void {
    this.metricsHistory = [];
  }

  // 停止监控
  public stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
  }

  // 销毁监控器
  public destroy() {
    this.stopMonitoring();
    this.clearHistory();
  }
}

// 全局资源监控器实例
let globalResourceMonitor: ResourceMonitor | null = null;

export function getResourceMonitor(): ResourceMonitor {
  if (!globalResourceMonitor) {
    globalResourceMonitor = new ResourceMonitor();
  }
  return globalResourceMonitor;
}

export function destroyResourceMonitor() {
  if (globalResourceMonitor) {
    globalResourceMonitor.destroy();
    globalResourceMonitor = null;
  }
}
