/**
 * 格式化 Unix 时间戳为本地日期时间字符串
 * @param timestamp - Unix 时间戳（秒）
 * @returns 格式化后的日期时间字符串
 */
export function formatTimestamp(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleString('zh-CN');
}

/**
 * 格式化 Unix 时间戳为简短的日期时间字符串
 * @param timestamp - Unix 时间戳（秒）
 * @returns 格式化后的简短日期时间字符串
 */
export function formatTimestampShort(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * 格式化毫秒数为可读的耗时字符串
 * @param ms - 毫秒数
 * @returns 格式化后的耗时字符串
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

/**
 * 格式化相对时间（多久以前）
 * @param timestamp - Unix 时间戳（秒）
 * @returns 格式化后的相对时间字符串
 */
export function formatRelativeTime(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp * 1000;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}天前`;
  if (hours > 0) return `${hours}小时前`;
  if (minutes > 0) return `${minutes}分钟前`;
  return '刚刚';
}
