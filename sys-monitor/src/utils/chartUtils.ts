/**
 * 图表工具函数模块
 * 
 * 提供数据采样、环形缓冲区、性能优化等工具函数
 */

// ==================== 数据采样 ====================

/**
 * 数据点接口
 */
export interface DataPoint {
  time: string;
  [key: string]: number | string;
}

/**
 * 简单降采样 - 均匀间隔采样
 * @param data 原始数据数组
 * @param maxPoints 最大数据点数
 * @returns 采样后的数据
 */
export function simpleSampling(data: DataPoint[], maxPoints: number = 100): DataPoint[] {
  if (data.length <= maxPoints) {
    return data;
  }

  const step = Math.ceil(data.length / maxPoints);
  const sampled: DataPoint[] = [];

  for (let i = 0; i < data.length; i += step) {
    sampled.push(data[i]);
  }

  // 确保包含最后一个点
  if (sampled[sampled.length - 1] !== data[data.length - 1]) {
    sampled.push(data[data.length - 1]);
  }

  return sampled;
}

/**
 * LTTB (Largest-Triangle-Three-Buckets) 降采样算法
 * 保持数据趋势特征，减少视觉失真
 * 
 * @param data 原始数据数组
 * @param maxPoints 最大数据点数
 * @param valueKey 数值字段名（默认 'value'）
 * @returns 采样后的数据
 */
export function lttbSampling(
  data: DataPoint[],
  maxPoints: number = 100,
  valueKey: string = 'value'
): DataPoint[] {
  if (data.length <= maxPoints) {
    return data;
  }

  const sampled: DataPoint[] = [data[0]]; // 始终包含第一个点
  const bucketSize = (data.length - 2) / (maxPoints - 2);

  let prevAvgX = 0;
  let prevAvgY = 0;

  for (let i = 0; i < maxPoints - 2; i++) {
    const bucketStart = Math.floor((i + 0) * bucketSize) + 1;
    const bucketEnd = Math.floor((i + 1) * bucketSize) + 1;

    // 计算下一个 bucket 的平均值
    let nextAvgX = 0;
    let nextAvgY = 0;
    const nextBucketStart = Math.floor((i + 1) * bucketSize) + 1;
    const nextBucketEnd = Math.floor((i + 2) * bucketSize) + 1;

    for (let j = nextBucketStart; j < nextBucketEnd && j < data.length; j++) {
      nextAvgX += j;
      nextAvgY += getNumericValue(data[j], valueKey);
    }
    const nextCount = Math.min(nextBucketEnd, data.length) - nextBucketStart;
    if (nextCount > 0) {
      nextAvgX /= nextCount;
      nextAvgY /= nextCount;
    }

    // 在当前 bucket 中找到使三角形面积最大的点
    let maxArea = -1;
    let maxIndex = bucketStart;

    for (let j = bucketStart; j < bucketEnd && j < data.length; j++) {
      const area = Math.abs(
        (prevAvgX - nextAvgX) * (getNumericValue(data[j], valueKey) - prevAvgY) -
        (prevAvgX - j) * (nextAvgY - prevAvgY)
      );

      if (area > maxArea) {
        maxArea = area;
        maxIndex = j;
      }
    }

    sampled.push(data[maxIndex]);
    prevAvgX = maxIndex;
    prevAvgY = getNumericValue(data[maxIndex], valueKey);
  }

  sampled.push(data[data.length - 1]); // 始终包含最后一个点
  return sampled;
}

/**
 * 获取数据点的数值
 */
function getNumericValue(point: DataPoint, key: string): number {
  const value = point[key];
  return typeof value === 'number' ? value : 0;
}

// ==================== 环形缓冲区 ====================

/**
 * 环形缓冲区实现
 * 固定容量，新数据覆盖旧数据
 */
export class RingBuffer<T> {
  private buffer: (T | undefined)[];
  private head: number = 0;
  private count: number = 0;
  private capacity: number;

  /**
   * 创建环形缓冲区
   * @param capacity 缓冲区容量
   */
  constructor(capacity: number) {
    this.capacity = capacity;
    this.buffer = new Array(capacity);
  }

  /**
   * 添加元素
   * @param item 要添加的元素
   */
  push(item: T): void {
    this.buffer[this.head] = item;
    this.head = (this.head + 1) % this.capacity;
    if (this.count < this.capacity) {
      this.count++;
    }
  }

  /**
   * 转换为数组（按插入顺序）
   * @returns 有序数组
   */
  toArray(): T[] {
    if (this.count < this.capacity) {
      return this.buffer.slice(0, this.count).filter((x): x is T => x !== undefined);
    }

    // 缓冲区已满，需要重新排列
    const result: T[] = [];
    for (let i = 0; i < this.capacity; i++) {
      const index = (this.head + i) % this.capacity;
      const item = this.buffer[index];
      if (item !== undefined) {
        result.push(item);
      }
    }
    return result;
  }

  /**
   * 获取当前元素数量
   */
  get size(): number {
    return this.count;
  }

  /**
   * 获取缓冲区容量
   */
  get maxSize(): number {
    return this.capacity;
  }

  /**
   * 清空缓冲区
   */
  clear(): void {
    this.buffer = new Array(this.capacity);
    this.head = 0;
    this.count = 0;
  }

  /**
   * 检查是否为空
   */
  isEmpty(): boolean {
    return this.count === 0;
  }

  /**
   * 检查是否已满
   */
  isFull(): boolean {
    return this.count === this.capacity;
  }
}

// ==================== 性能优化工具 ====================

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param delay 延迟时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, delay);
  };
}

/**
 * 节流函数
 * @param func 要节流的函数
 * @param interval 间隔时间（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  interval: number
): (...args: Parameters<T>) => void {
  let lastTime = 0;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    const now = Date.now();
    const remaining = interval - (now - lastTime);

    if (remaining <= 0) {
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
      lastTime = now;
      func(...args);
    } else if (!timeoutId) {
      timeoutId = setTimeout(() => {
        lastTime = Date.now();
        timeoutId = null;
        func(...args);
      }, remaining);
    }
  };
}

/**
 * 格式化字节数为可读字符串
 * @param bytes 字节数
 * @param decimals 小数位数
 * @returns 格式化后的字符串
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
}

/**
 * 格式化百分比
 * @param value 数值（0-100）
 * @param decimals 小数位数
 * @returns 格式化后的字符串
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * 格式化时间戳为本地时间字符串
 * @param timestamp ISO 时间戳
 * @returns 格式化后的时间字符串
 */
export function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * 计算数组平均值
 * @param arr 数值数组
 * @returns 平均值
 */
export function average(arr: number[]): number {
  if (arr.length === 0) return 0;
  return arr.reduce((sum, val) => sum + val, 0) / arr.length;
}

/**
 * 计算数组标准差
 * @param arr 数值数组
 * @returns 标准差
 */
export function standardDeviation(arr: number[]): number {
  if (arr.length === 0) return 0;
  const avg = average(arr);
  const squareDiffs = arr.map(val => Math.pow(val - avg, 2));
  const avgSquareDiff = average(squareDiffs);
  return Math.sqrt(avgSquareDiff);
}

/**
 * 检测异常值（基于标准差）
 * @param arr 数值数组
 * @param threshold 阈值（标准差倍数，默认 2）
 * @returns 异常值索引数组
 */
export function detectOutliers(arr: number[], threshold: number = 2): number[] {
  if (arr.length < 3) return [];

  const avg = average(arr);
  const stdDev = standardDeviation(arr);
  const outliers: number[] = [];

  arr.forEach((val, index) => {
    if (Math.abs(val - avg) > threshold * stdDev) {
      outliers.push(index);
    }
  });

  return outliers;
}

// ==================== 颜色工具 ====================

/**
 * 生成渐变色
 * @param color1 起始颜色
 * @param color2 结束颜色
 * @param steps 步数
 * @returns 颜色数组
 */
export function generateGradient(color1: string, color2: string, steps: number): string[] {
  const c1 = parseColor(color1);
  const c2 = parseColor(color2);
  const colors: string[] = [];

  for (let i = 0; i < steps; i++) {
    const ratio = i / (steps - 1);
    const r = Math.round(c1.r + (c2.r - c1.r) * ratio);
    const g = Math.round(c1.g + (c2.g - c1.g) * ratio);
    const b = Math.round(c1.b + (c2.b - c1.b) * ratio);
    colors.push(`rgb(${r}, ${g}, ${b})`);
  }

  return colors;
}

interface RGB {
  r: number;
  g: number;
  b: number;
}

/**
 * 解析颜色字符串为 RGB
 */
function parseColor(color: string): RGB {
  // 支持 #RRGGBB 格式
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    return {
      r: parseInt(hex.substr(0, 2), 16),
      g: parseInt(hex.substr(2, 2), 16),
      b: parseInt(hex.substr(4, 2), 16),
    };
  }

  // 支持 rgb(r, g, b) 格式
  const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
  if (match) {
    return {
      r: parseInt(match[1]),
      g: parseInt(match[2]),
      b: parseInt(match[3]),
    };
  }

  // 默认返回灰色
  return { r: 128, g: 128, b: 128 };
}

/**
 * 预定义颜色方案
 */
export const COLOR_SCHEMES = {
  blue: ['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'],
  green: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0'],
  orange: ['#f59e0b', '#fbbf24', '#fcd34d', '#fde68a'],
  red: ['#ef4444', '#f87171', '#fca5a5', '#fecaca'],
  purple: ['#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe'],
  mixed: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
};
