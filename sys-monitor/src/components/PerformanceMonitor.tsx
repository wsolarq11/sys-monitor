import React, { useEffect, useRef } from 'react';
import { onCLS, onFCP, onLCP, onTTFB, onINP, Metric } from 'web-vitals';
import * as Sentry from "@sentry/react";

interface PerformanceMetrics {
  cls: number;
  fid: number;
  fcp: number;
  lcp: number;
  ttfb: number;
  customMetrics: Record<string, number>;
}

interface PerformanceMonitorProps {
  onMetricsReport?: (metrics: PerformanceMetrics) => void;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({ onMetricsReport }) => {
  const metricsRef = useRef<PerformanceMetrics>({
    cls: 0,
    fid: 0,
    fcp: 0,
    lcp: 0,
    ttfb: 0,
    customMetrics: {}
  });

  // 用户行为追踪
  const trackUserInteraction = (action: string, details?: any) => {
    Sentry.addBreadcrumb({
      category: 'user.interaction',
      message: `User performed: ${action}`,
      level: 'info',
      data: details
    });
  };

  // 错误上下文增强
  const enhanceErrorContext = () => {
    Sentry.setContext('performance_metrics', {
      current_metrics: metricsRef.current,
      timestamp: Date.now(),
      user_agent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    });
  };

  // 全局错误处理器
  const setupGlobalErrorHandlers = () => {
    // 捕获未处理的Promise拒绝
    window.addEventListener('unhandledrejection', (event) => {
      enhanceErrorContext();
      trackUserInteraction('unhandled_rejection', { reason: event.reason });
      Sentry.captureException(event.reason);
    });

    // 捕获全局错误
    window.addEventListener('error', (event) => {
      enhanceErrorContext();
      trackUserInteraction('global_error', { 
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      });
      Sentry.captureException(event.error);
    });
  };

  // 报告Web Vitals指标
  const reportWebVitals = (metric: Metric) => {
    console.log(`Web Vitals: ${metric.name} = ${metric.value}`);
    
    // 更新指标
    switch (metric.name) {
      case 'CLS':
        metricsRef.current.cls = metric.value;
        break;
      case 'FCP':
        metricsRef.current.fcp = metric.value;
        break;
      case 'LCP':
        metricsRef.current.lcp = metric.value;
        break;
      case 'TTFB':
        metricsRef.current.ttfb = metric.value;
        break;
      case 'INP': // 新的Web Vitals指标
        metricsRef.current.fid = metric.value; // 使用INP作为FID的替代
        break;
    }

    // 发送详细性能指标到Sentry
    Sentry.captureMessage(`Web Vitals: ${metric.name}`, {
      level: 'info',
      extra: { 
        value: metric.value,
        rating: metric.rating,
        delta: metric.delta,
        id: metric.id,
        navigationType: metric.navigationType
      }
    });
    
    // 触发性能警报
    if (metric.name === 'CLS' && metric.value > 0.1) {
      Sentry.captureMessage('High Cumulative Layout Shift detected', {
        level: 'warning',
        extra: { 
          cls: metric.value,
          threshold: 0.1,
          impact: '用户体验受损'
        }
      });
    }

    // LCP性能警报
    if (metric.name === 'LCP' && metric.value > 2500) {
      Sentry.captureMessage('Slow Largest Contentful Paint', {
        level: 'warning',
        extra: { 
          lcp: metric.value,
          threshold: 2500,
          impact: '页面加载缓慢'
        }
      });
    }

    // INP性能警报
    if (metric.name === 'INP' && metric.value > 200) {
      Sentry.captureMessage('High Interaction to Next Paint', {
        level: 'warning',
        extra: { 
          inp: metric.value,
          threshold: 200,
          impact: '交互响应延迟'
        }
      });
    }

    // 回调通知
    if (onMetricsReport) {
      onMetricsReport(metricsRef.current);
    }
  };

  // 自定义性能指标
  const measureCustomMetrics = () => {
    // 页面加载时间
    const navigationTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigationTiming && navigationTiming.activationStart) {
      const loadTime = navigationTiming.loadEventEnd - navigationTiming.activationStart;
      metricsRef.current.customMetrics.pageLoadTime = loadTime;
      // Sentry metrics API已变更，使用captureMessage替代
      Sentry.captureMessage('Page load time measured', {
        level: 'info',
        extra: { page_load_time: loadTime }
      });
    }

    // 内存使用情况
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      if (memory) {
        const usedMemory = memory.usedJSHeapSize / 1024 / 1024; // MB
        metricsRef.current.customMetrics.memoryUsage = usedMemory;
        Sentry.metrics.distribution('memory_usage_mb', usedMemory);
      }
    }

    // 首次内容绘制后的交互时间
    const firstInteractiveTime = performance.now();
    metricsRef.current.customMetrics.firstInteractive = firstInteractiveTime;
    Sentry.metrics.distribution('first_interactive_ms', firstInteractiveTime);
  };

  // 监控React组件渲染性能
  const monitorReactPerformance = () => {
    // 使用Performance API监控关键组件渲染
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'measure') {
          // 发送性能指标到Sentry
          Sentry.captureMessage(`React performance: ${entry.name}`, {
            level: 'info',
            extra: { 
              duration: entry.duration,
              entryType: entry.entryType,
              timestamp: entry.startTime
            }
          });
          
          // 如果渲染时间过长，发出警告
          if (entry.duration > 100) {
            Sentry.captureMessage(`Slow React component: ${entry.name}`, {
              level: 'warning',
              extra: { 
                duration: entry.duration,
                threshold: 100
              }
            });
          }
        }
      });
    });

    observer.observe({ entryTypes: ['measure'] });
    return observer;
  };

  useEffect(() => {
    // 初始化Web Vitals监控
    onCLS(reportWebVitals);
    onFCP(reportWebVitals);
    onLCP(reportWebVitals);
    onTTFB(reportWebVitals);
    onINP(reportWebVitals);

    // 设置全局错误处理器
    setupGlobalErrorHandlers();

    // 监控自定义指标
    const measureInterval = setInterval(measureCustomMetrics, 10000); // 每10秒测量一次
    
    // 监控React性能
    const performanceObserver = monitorReactPerformance();

    // 页面卸载时报告最终指标
    const handleBeforeUnload = () => {
      // Sentry metrics API已变更，使用captureMessage替代
      Sentry.captureMessage('Page unload detected', {
        level: 'info',
        extra: { session_duration: performance.now() }
      });
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      clearInterval(measureInterval);
      performanceObserver.disconnect();
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [onMetricsReport]);

  // 手动性能测量函数
  const startMeasurement = (name: string) => {
    performance.mark(`${name}-start`);
  };

  const endMeasurement = (name: string) => {
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    const measures = performance.getEntriesByName(name);
    if (measures.length > 0) {
      const duration = measures[0].duration;
      Sentry.metrics.distribution(`custom_${name}`, duration);
      
      // 记录到自定义指标
      metricsRef.current.customMetrics[name] = duration;
      
      if (onMetricsReport) {
        onMetricsReport(metricsRef.current);
      }
    }
  };

  // 导出测量函数供其他组件使用
  React.useImperativeHandle(React.createRef(), () => ({
    startMeasurement,
    endMeasurement,
    getCurrentMetrics: () => metricsRef.current
  }));

  return null; // 这个组件不渲染任何内容
};

// 性能监控HOC
export const withPerformanceMonitor = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName: string
) => {
  return (props: P) => {
    const startTimeRef = React.useRef(performance.now());

    useEffect(() => {
      const renderTime = performance.now() - startTimeRef.current;
      Sentry.metrics.distribution(`component_${componentName}_render`, renderTime);
      
      // 如果渲染时间过长，发出警告
      if (renderTime > 100) { // 超过100ms
        Sentry.captureMessage(`Slow component render: ${componentName}`, {
          level: 'warning',
          extra: { renderTime, componentName }
        });
      }
    }, []);

    return <WrappedComponent {...props} />;
  };
};

export default PerformanceMonitor;