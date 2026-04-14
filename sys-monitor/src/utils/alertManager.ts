import * as Sentry from "@sentry/react";

// 警报级别
export enum AlertLevel {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

// 警报类型
export enum AlertType {
  PERFORMANCE = 'performance',
  ERROR_RATE = 'error_rate',
  RESOURCE_USAGE = 'resource_usage',
  USER_BEHAVIOR = 'user_behavior',
  SECURITY = 'security',
  BUSINESS = 'business'
}

// 警报接口
export interface Alert {
  id: string;
  type: AlertType;
  level: AlertLevel;
  title: string;
  message: string;
  timestamp: number;
  data: any;
  resolved?: boolean;
  resolvedAt?: number;
  acknowledged?: boolean;
  acknowledgedAt?: number;
}

// 警报规则接口
export interface AlertRule {
  id: string;
  name: string;
  type: AlertType;
  level: AlertLevel;
  condition: (data: any) => boolean;
  threshold: number;
  cooldown: number; // 冷却时间（毫秒）
  lastTriggered?: number;
  enabled: boolean;
}

// 警报管理器
export class AlertManager {
  private alerts: Alert[] = [];
  private rules: AlertRule[] = [];
  private alertHistory: Alert[] = [];
  private maxHistorySize = 1000;
  private isMonitoring = false;

  constructor() {
    this.setupDefaultRules();
    this.startMonitoring();
  }

  // 设置默认警报规则
  private setupDefaultRules() {
    this.addRule({
      id: 'high_error_rate',
      name: '高错误率警报',
      type: AlertType.ERROR_RATE,
      level: AlertLevel.WARNING,
      condition: (data) => data.errorRate > 0.1,
      threshold: 0.1,
      cooldown: 300000, // 5分钟
      enabled: true
    });

    this.addRule({
      id: 'slow_performance',
      name: '性能下降警报',
      type: AlertType.PERFORMANCE,
      level: AlertLevel.WARNING,
      condition: (data) => data.pageLoadTime > 3000 || data.lcp > 2500,
      threshold: 3000,
      cooldown: 600000, // 10分钟
      enabled: true
    });

    this.addRule({
      id: 'high_memory_usage',
      name: '高内存使用警报',
      type: AlertType.RESOURCE_USAGE,
      level: AlertLevel.WARNING,
      condition: (data) => data.memoryUsage > 80,
      threshold: 80,
      cooldown: 300000, // 5分钟
      enabled: true
    });

    this.addRule({
      id: 'user_session_anomaly',
      name: '用户会话异常警报',
      type: AlertType.USER_BEHAVIOR,
      level: AlertLevel.WARNING,
      condition: (data) => data.sessionDuration < 1000 || data.errorCount > 10,
      threshold: 10,
      cooldown: 900000, // 15分钟
      enabled: true
    });

    this.addRule({
      id: 'critical_error',
      name: '严重错误警报',
      type: AlertType.ERROR_RATE,
      level: AlertLevel.CRITICAL,
      condition: (data) => data.errorRate > 0.5 || data.unhandledExceptions > 0,
      threshold: 0.5,
      cooldown: 60000, // 1分钟
      enabled: true
    });
  }

  // 添加警报规则
  public addRule(rule: AlertRule) {
    this.rules.push(rule);
  }

  // 开始监控
  public startMonitoring() {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    
    // 定期检查警报规则
    setInterval(() => {
      this.checkRules();
    }, 30000); // 每30秒检查一次

    // 定期清理过期警报
    setInterval(() => {
      this.cleanupOldAlerts();
    }, 3600000); // 每小时清理一次
  }

  // 检查警报规则
  private checkRules() {
    // 获取当前系统状态数据
    const systemData = this.getSystemData();
    
    // 检查每个规则
    this.rules.forEach(rule => {
      if (!rule.enabled) return;
      
      // 检查冷却时间
      if (rule.lastTriggered && Date.now() - rule.lastTriggered < rule.cooldown) {
        return;
      }
      
      // 检查条件
      if (rule.condition(systemData)) {
        this.triggerAlert(rule, systemData);
        rule.lastTriggered = Date.now();
      }
    });
  }

  // 获取系统数据
  private getSystemData(): any {
    // 这里可以集成从各种监控系统获取的数据
    // 目前使用模拟数据
    return {
      errorRate: Math.random() * 0.2, // 模拟错误率 0-20%
      pageLoadTime: Math.random() * 5000, // 模拟页面加载时间 0-5秒
      lcp: Math.random() * 4000, // 模拟LCP 0-4秒
      memoryUsage: Math.random() * 100, // 模拟内存使用率 0-100%
      sessionDuration: Math.random() * 60000, // 模拟会话时长 0-60秒
      errorCount: Math.floor(Math.random() * 20), // 模拟错误数量 0-20
      unhandledExceptions: Math.floor(Math.random() * 5) // 模拟未处理异常 0-5
    };
  }

  // 触发警报
  private triggerAlert(rule: AlertRule, data: any) {
    const alert: Alert = {
      id: this.generateAlertId(),
      type: rule.type,
      level: rule.level,
      title: `${rule.name} - 阈值: ${rule.threshold}`,
      message: `检测到异常情况: ${JSON.stringify(data)}`,
      timestamp: Date.now(),
      data,
      resolved: false,
      acknowledged: false
    };

    this.alerts.push(alert);
    this.alertHistory.push(alert);

    // 限制历史记录大小
    if (this.alertHistory.length > this.maxHistorySize) {
      this.alertHistory = this.alertHistory.slice(-this.maxHistorySize);
    }

    // 发送到Sentry
    this.sendToSentry(alert);

    // 发送到外部系统（可以扩展）
    this.sendToExternalSystems(alert);

    console.log(`警报触发: ${alert.title}`, alert);
  }

  // 生成警报ID
  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 发送到Sentry
  private sendToSentry(alert: Alert) {
    const sentryLevel = this.mapAlertLevelToSentryLevel(alert.level);
    
    Sentry.captureMessage(alert.title, {
      level: sentryLevel,
      extra: {
        alertId: alert.id,
        alertType: alert.type,
        alertData: alert.data,
        timestamp: alert.timestamp
      }
    });

    // 设置警报上下文
    Sentry.withScope(scope => {
      scope.setTag('alert_type', alert.type);
      scope.setTag('alert_level', alert.level);
      scope.setExtra('alert_data', alert.data);
    });
  }

  // 映射警报级别到Sentry级别
  private mapAlertLevelToSentryLevel(level: AlertLevel): Sentry.SeverityLevel {
    switch (level) {
      case AlertLevel.INFO: return 'info';
      case AlertLevel.WARNING: return 'warning';
      case AlertLevel.ERROR: return 'error';
      case AlertLevel.CRITICAL: return 'fatal';
      default: return 'error';
    }
  }

  // 发送到外部系统
  private sendToExternalSystems(alert: Alert) {
    // 这里可以集成到外部系统，如：
    // - Slack/Teams通知
    // - 邮件通知
    // - 短信通知
    // - Webhook调用
    
    // 示例：发送到控制台
    console.log(`发送警报到外部系统: ${alert.title}`);
  }

  // 手动触发警报
  public triggerManualAlert(type: AlertType, level: AlertLevel, title: string, message: string, data: any) {
    const alert: Alert = {
      id: this.generateAlertId(),
      type,
      level,
      title,
      message,
      timestamp: Date.now(),
      data,
      resolved: false,
      acknowledged: false
    };

    this.alerts.push(alert);
    this.alertHistory.push(alert);

    this.sendToSentry(alert);
    
    return alert;
  }

  // 获取当前活跃警报
  public getActiveAlerts(): Alert[] {
    return this.alerts.filter(alert => !alert.resolved);
  }

  // 获取警报历史
  public getAlertHistory(limit?: number): Alert[] {
    const history = [...this.alertHistory].reverse();
    return limit ? history.slice(0, limit) : history;
  }

  // 解决警报
  public resolveAlert(alertId: string) {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      alert.resolvedAt = Date.now();
      
      // 发送解决通知
      Sentry.captureMessage(`警报已解决: ${alert.title}`, {
        level: 'info',
        extra: {
          alertId: alert.id,
          resolvedAt: alert.resolvedAt
        }
      });
    }
  }

  // 确认警报
  public acknowledgeAlert(alertId: string) {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedAt = Date.now();
    }
  }

  // 清理过期警报
  private cleanupOldAlerts() {
    const now = Date.now();
    const oneDayAgo = now - 24 * 60 * 60 * 1000; // 24小时前
    
    this.alerts = this.alerts.filter(alert => 
      !alert.resolved || (alert.resolvedAt && alert.resolvedAt > oneDayAgo)
    );
  }

  // 获取警报统计
  public getAlertStats() {
    const totalAlerts = this.alertHistory.length;
    const activeAlerts = this.getActiveAlerts().length;
    const resolvedAlerts = this.alertHistory.filter(a => a.resolved).length;
    
    const alertsByLevel = this.alertHistory.reduce((acc, alert) => {
      acc[alert.level] = (acc[alert.level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const alertsByType = this.alertHistory.reduce((acc, alert) => {
      acc[alert.type] = (acc[alert.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalAlerts,
      activeAlerts,
      resolvedAlerts,
      alertsByLevel,
      alertsByType
    };
  }

  // 停止监控
  public stopMonitoring() {
    this.isMonitoring = false;
  }

  // 销毁管理器
  public destroy() {
    this.stopMonitoring();
    this.alerts = [];
    this.alertHistory = [];
    this.rules = [];
  }
}

// 全局警报管理器实例
let globalAlertManager: AlertManager | null = null;

export function getAlertManager(): AlertManager {
  if (!globalAlertManager) {
    globalAlertManager = new AlertManager();
  }
  return globalAlertManager;
}

export function destroyAlertManager() {
  if (globalAlertManager) {
    globalAlertManager.destroy();
    globalAlertManager = null;
  }
}