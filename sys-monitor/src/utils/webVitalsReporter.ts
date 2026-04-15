/**
 * Web Vitals Reporter
 * 
 * 基于 React Performance Optimization Skill 实现
 * 参考: https://vercel.com/docs/observability/web-vitals
 * 
 * 监控核心 Web Vitals 指标:
 * - CLS (Cumulative Layout Shift): 累积布局偏移 < 0.1
 * - FCP (First Contentful Paint): 首次内容绘制 < 1.8s
 * - LCP (Largest Contentful Paint): 最大内容绘制 < 2.5s
 * - TTFB (Time to First Byte): 首字节时间 < 800ms
 * - INP (Interaction to Next Paint): 交互到下次绘制 < 200ms
 */

import { onCLS, onFCP, onLCP, onTTFB, onINP, Metric } from 'web-vitals';

export type WebVitalsMetric = Metric;
export type WebVitalsCallback = (metric: WebVitalsMetric) => void;

/**
 * 启动 Web Vitals 监控
 * 
 * @param callback - 指标回调函数
 * @param options - 配置选项
 */
export function reportWebVitals(
  callback?: WebVitalsCallback,
  options?: {
    // 是否只报告一次（默认 false，持续监控）
    reportOnce?: boolean;
    // 是否包含调试信息
    debug?: boolean;
  }
) {
  const { reportOnce = false, debug = false } = options || {};

  // 包装回调，添加额外处理
  const wrappedCallback: WebVitalsCallback = (metric) => {
    // 调试日志
    if (debug) {
      console.group(`[Web Vitals] ${metric.name}`);
      console.log('Value:', metric.value);
      console.log('Rating:', metric.rating);
      console.log('Delta:', metric.delta);
      console.log('ID:', metric.id);
      console.log('Navigation Type:', metric.navigationType);
      console.groupEnd();
    }

    // 调用用户回调
    if (callback) {
      callback(metric);
    }

    // 发送到分析平台（可选）
    sendToAnalytics(metric);
  };

  // 注册所有 Web Vitals 监听器
  // 注意: FID 已在 web-vitals v4+ 中废弃，使用 INP 替代
  onCLS(wrappedCallback);
  onFCP(wrappedCallback);
  onLCP(wrappedCallback);
  onTTFB(wrappedCallback);
  onINP(wrappedCallback);

  // 如果只需要报告一次，在首次报告后取消监听
  if (reportOnce) {
    setTimeout(() => {
      // web-vitals 库不支持手动取消，这里仅作占位
      console.log('[Web Vitals] Single report mode enabled');
    }, 5000);
  }
}

/**
 * 发送指标到分析平台
 * 
 * @param metric - Web Vitals 指标
 */
function sendToAnalytics(metric: WebVitalsMetric) {
  // 示例：发送到 Google Analytics
  // gtag('event', metric.name, {
  //   value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
  //   event_category: 'Web Vitals',
  //   event_label: metric.id,
  //   non_interaction: true,
  // });

  // 示例：发送到自定义 API
  // fetch('/api/web-vitals', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({
  //     name: metric.name,
  //     value: metric.value,
  //     rating: metric.rating,
  //     timestamp: Date.now(),
  //     url: window.location.href,
  //   }),
  // }).catch(console.error);
  
  // 预留扩展点，避免未使用变量警告
  void metric;
}

/**
 * 获取性能评级描述
 * 
 * @param rating - 评级字符串
 * @returns 中文描述
 */
export function getRatingDescription(rating: string): string {
  switch (rating) {
    case 'good':
      return '优秀';
    case 'needs-improvement':
      return '需要改进';
    case 'poor':
      return '较差';
    default:
      return '未知';
  }
}

/**
 * 检查指标是否超过阈值
 * 
 * @param metric - Web Vitals 指标
 * @returns 是否超标
 */
export function isMetricPoor(metric: WebVitalsMetric): boolean {
  return metric.rating === 'poor';
}

/**
 * 获取指标阈值
 * 
 * @param metricName - 指标名称
 * @returns 阈值对象
 */
export function getMetricThreshold(metricName: string): { good: number; poor: number } {
  const thresholds: Record<string, { good: number; poor: number }> = {
    CLS: { good: 0.1, poor: 0.25 },
    FCP: { good: 1800, poor: 3000 },
    FID: { good: 100, poor: 300 },
    LCP: { good: 2500, poor: 4000 },
    TTFB: { good: 800, poor: 1800 },
    INP: { good: 200, poor: 500 },
  };

  return thresholds[metricName] || { good: 0, poor: 0 };
}
