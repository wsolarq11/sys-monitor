/**
 * 格式化字节数为可读的大小字符串
 * @param bytes - 字节数
 * @returns 格式化后的大小字符串（B, KB, MB, GB, TB）
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 格式化百分比
 * @param value - 数值
 * @returns 格式化后的百分比字符串
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

/**
 * 格式化字节数为简短的可读大小（用于扫描结果）
 * @param bytes - 字节数
 * @returns 格式化后的大小字符串
 */
export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}
