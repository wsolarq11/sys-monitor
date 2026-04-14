import * as Sentry from "@sentry/react";

// 用户行为接口
export interface UserBehavior {
  sessionId: string;
  userId?: string;
  startTime: number;
  endTime?: number;
  pageViews: PageView[];
  interactions: UserInteraction[];
  errors: UserError[];
  performance: PerformanceMetrics;
}

export interface PageView {
  path: string;
  timestamp: number;
  duration?: number;
  referrer?: string;
}

export interface UserInteraction {
  type: 'click' | 'input' | 'hover' | 'scroll' | 'keypress' | 'focus' | 'blur';
  target: string;
  timestamp: number;
  details?: any;
}

export interface UserError {
  type: 'js' | 'network' | 'resource' | 'user';
  message: string;
  timestamp: number;
  stack?: string;
  context?: any;
}

interface PerformanceMetrics {
  pageLoadTime?: number;
  domContentLoaded?: number;
  firstPaint?: number;
  firstContentfulPaint?: number;
  largestContentfulPaint?: number;
  cumulativeLayoutShift?: number;
}

// 用户行为分析器
export class UserBehaviorAnalyzer {
  private currentSession: UserBehavior;
  private sessionStartTime: number;
  private currentPageView: PageView | null = null;
  private interactionBuffer: UserInteraction[] = [];
  private errorBuffer: UserError[] = [];
  private maxBufferSize = 100;

  constructor() {
    this.sessionStartTime = Date.now();
    this.currentSession = {
      sessionId: this.generateSessionId(),
      startTime: this.sessionStartTime,
      pageViews: [],
      interactions: [],
      errors: [],
      performance: {}
    };

    this.setupEventListeners();
    this.setupPerformanceMonitoring();
    this.setupSessionTracking();
  }

  // 生成会话ID
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 设置事件监听器
  private setupEventListeners() {
    // 点击事件监听
    document.addEventListener('click', (event) => {
      this.trackInteraction('click', event);
    }, { capture: true });

    // 输入事件监听
    document.addEventListener('input', (event) => {
      this.trackInteraction('input', event);
    }, { capture: true });

    // 滚动事件监听
    let scrollTimeout: number;
    document.addEventListener('scroll', (event) => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        this.trackInteraction('scroll', event);
      }, 100);
    }, { capture: true });

    // 键盘事件监听
    document.addEventListener('keypress', (event) => {
      this.trackInteraction('keypress', event);
    }, { capture: true });

    // 焦点事件监听
    document.addEventListener('focus', (event) => {
      this.trackInteraction('focus', event);
    }, { capture: true });

    document.addEventListener('blur', (event) => {
      this.trackInteraction('blur', event);
    }, { capture: true });

    // 页面可见性变化
    document.addEventListener('visibilitychange', () => {
      this.trackVisibilityChange();
    });

    // 页面卸载
    window.addEventListener('beforeunload', () => {
      this.endSession();
    });
  }

  // 设置性能监控
  private setupPerformanceMonitoring() {
    // 监听性能指标
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.trackPerformanceMetric(entry);
        });
      });

      observer.observe({ entryTypes: ['navigation', 'paint', 'largest-contentful-paint', 'layout-shift'] });
    }

    // 获取初始性能指标
    this.captureInitialPerformance();
  }

  // 设置会话追踪
  private setupSessionTracking() {
    // 定期发送会话数据
    setInterval(() => {
      this.flushBuffers();
    }, 30000); // 每30秒发送一次

    // 页面加载完成时记录
    window.addEventListener('load', () => {
      this.trackPageView(window.location.pathname);
    });

    // 路由变化监听（如果使用React Router）
    if (window.history && window.history.pushState) {
      const originalPushState = window.history.pushState;
      window.history.pushState = (...args) => {
        originalPushState.apply(window.history, args);
        this.trackPageView(window.location.pathname);
      };

      window.addEventListener('popstate', () => {
        this.trackPageView(window.location.pathname);
      });
    }
  }

  // 追踪用户交互
  private trackInteraction(type: UserInteraction['type'], event: Event) {
    const target = event.target as HTMLElement;
    const interaction: UserInteraction = {
      type,
      target: this.getElementPath(target),
      timestamp: Date.now(),
      details: this.getInteractionDetails(type, event, target)
    };

    this.interactionBuffer.push(interaction);

    // 缓冲区满时发送
    if (this.interactionBuffer.length >= this.maxBufferSize) {
      this.flushInteractionBuffer();
    }

    // 发送到Sentry
    Sentry.addBreadcrumb({
      category: 'user.interaction',
      message: `User ${type}: ${interaction.target}`,
      level: 'info',
      data: interaction.details
    });
  }

  // 获取元素路径
  private getElementPath(element: HTMLElement): string {
    const path: string[] = [];
    let current: HTMLElement | null = element;

    while (current && current !== document.body) {
      let selector = current.tagName.toLowerCase();
      
      if (current.id) {
        selector += `#${current.id}`;
      } else if (current.className) {
        selector += `.${current.className.split(' ')[0]}`;
      }
      
      path.unshift(selector);
      current = current.parentElement;
    }

    return path.join(' > ');
  }

  // 获取交互详情
  private getInteractionDetails(type: string, event: Event, target: HTMLElement): any {
    const details: any = {
      tagName: target.tagName,
      className: target.className,
      id: target.id,
      textContent: target.textContent?.substring(0, 100)
    };

    if (type === 'input' && 'value' in target) {
      details.value = (target as HTMLInputElement).value?.substring(0, 50);
    }

    if (type === 'keypress' && 'key' in event) {
      details.key = (event as KeyboardEvent).key;
    }

    return details;
  }

  // 追踪页面可见性变化
  private trackVisibilityChange() {
    const state = document.visibilityState;
    Sentry.addBreadcrumb({
      category: 'user.session',
      message: `Page visibility changed to ${state}`,
      level: 'info',
      data: { visibilityState: state }
    });
  }

  // 追踪页面浏览
  public trackPageView(path: string) {
    // 结束当前页面浏览
    if (this.currentPageView) {
      this.currentPageView.duration = Date.now() - this.currentPageView.timestamp;
    }

    // 开始新的页面浏览
    this.currentPageView = {
      path,
      timestamp: Date.now(),
      referrer: document.referrer
    };

    this.currentSession.pageViews.push(this.currentPageView);

    Sentry.addBreadcrumb({
      category: 'navigation',
      message: `Page view: ${path}`,
      level: 'info',
      data: {
        path,
        referrer: document.referrer
      }
    });
  }

  // 追踪性能指标
  private trackPerformanceMetric(entry: PerformanceEntry) {
    switch (entry.entryType) {
      case 'navigation':
        const navEntry = entry as PerformanceNavigationTiming;
        this.currentSession.performance.pageLoadTime = navEntry.loadEventEnd - (navEntry.activationStart || navEntry.fetchStart);
        this.currentSession.performance.domContentLoaded = navEntry.domContentLoadedEventEnd - (navEntry.activationStart || navEntry.fetchStart);
        break;

      case 'paint':
        const paintEntry = entry as PerformancePaintTiming;
        if (paintEntry.name === 'first-paint') {
          this.currentSession.performance.firstPaint = paintEntry.startTime;
        } else if (paintEntry.name === 'first-contentful-paint') {
          this.currentSession.performance.firstContentfulPaint = paintEntry.startTime;
        }
        break;

      case 'largest-contentful-paint':
        const lcpEntry = entry as PerformanceEntry;
        this.currentSession.performance.largestContentfulPaint = lcpEntry.startTime;
        break;

      case 'layout-shift':
        const lsEntry = entry as any;
        if (!lsEntry.hadRecentInput) {
          this.currentSession.performance.cumulativeLayoutShift = 
            (this.currentSession.performance.cumulativeLayoutShift || 0) + lsEntry.value;
        }
        break;
    }
  }

  // 捕获初始性能指标
  private captureInitialPerformance() {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigation) {
      this.currentSession.performance.pageLoadTime = navigation.loadEventEnd - (navigation.activationStart || navigation.fetchStart);
      this.currentSession.performance.domContentLoaded = navigation.domContentLoadedEventEnd - (navigation.activationStart || navigation.fetchStart);
    }

    const paintEntries = performance.getEntriesByType('paint');
    paintEntries.forEach(entry => {
      if (entry.name === 'first-paint') {
        this.currentSession.performance.firstPaint = entry.startTime;
      } else if (entry.name === 'first-contentful-paint') {
        this.currentSession.performance.firstContentfulPaint = entry.startTime;
      }
    });
  }

  // 追踪用户错误
  public trackUserError(type: UserError['type'], message: string, stack?: string, context?: any) {
    const error: UserError = {
      type,
      message,
      timestamp: Date.now(),
      stack,
      context
    };

    this.errorBuffer.push(error);
    this.currentSession.errors.push(error);

    Sentry.captureMessage(`User error: ${message}`, {
      level: 'error',
      extra: { type, context }
    });
  }

  // 设置用户ID
  public setUserId(userId: string) {
    this.currentSession.userId = userId;
    Sentry.setUser({ id: userId });
  }

  // 刷新缓冲区
  private flushBuffers() {
    this.flushInteractionBuffer();
    this.flushErrorBuffer();
  }

  // 刷新交互缓冲区
  private flushInteractionBuffer() {
    if (this.interactionBuffer.length > 0) {
      // 发送交互数据到监控系统
      Sentry.captureMessage('User interactions batch', {
        level: 'info',
        extra: {
          count: this.interactionBuffer.length,
          interactions: this.interactionBuffer
        }
      });

      this.interactionBuffer = [];
    }
  }

  // 刷新错误缓冲区
  private flushErrorBuffer() {
    if (this.errorBuffer.length > 0) {
      Sentry.captureMessage('User errors batch', {
        level: 'warning',
        extra: {
          count: this.errorBuffer.length,
          errors: this.errorBuffer
        }
      });

      this.errorBuffer = [];
    }
  }

  // 结束会话
  public endSession() {
    this.currentSession.endTime = Date.now();
    
    // 发送最终会话报告
    this.sendSessionReport();
    
    // 清理资源
    this.flushBuffers();
  }

  // 发送会话报告
  private sendSessionReport() {
    const sessionDuration = this.currentSession.endTime! - this.currentSession.startTime;
    
    Sentry.captureMessage('User session ended', {
      level: 'info',
      extra: {
        sessionId: this.currentSession.sessionId,
        duration: sessionDuration,
        pageViews: this.currentSession.pageViews.length,
        interactions: this.currentSession.interactions.length,
        errors: this.currentSession.errors.length,
        performance: this.currentSession.performance
      }
    });
  }

  // 获取当前会话数据
  public getCurrentSession(): UserBehavior {
    return { ...this.currentSession };
  }

  // 清理资源
  public destroy() {
    this.endSession();
    // 清理事件监听器
    // 注意：在实际应用中需要更精确的事件监听器清理
  }
}

// 全局用户行为分析器实例
let globalUserBehaviorAnalyzer: UserBehaviorAnalyzer | null = null;

export function getUserBehaviorAnalyzer(): UserBehaviorAnalyzer {
  if (!globalUserBehaviorAnalyzer) {
    globalUserBehaviorAnalyzer = new UserBehaviorAnalyzer();
  }
  return globalUserBehaviorAnalyzer;
}

export function destroyUserBehaviorAnalyzer() {
  if (globalUserBehaviorAnalyzer) {
    globalUserBehaviorAnalyzer.destroy();
    globalUserBehaviorAnalyzer = null;
  }
}