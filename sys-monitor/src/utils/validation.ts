/**
 * 验证路径是否为空
 * @param path - 待验证的路径
 * @returns 验证结果
 */
export function isValidPath(path: string): boolean {
  return typeof path === 'string' && path.trim().length > 0;
}

/**
 * 验证路径格式是否合法（基础验证）
 * @param path - 待验证的路径
 * @returns 验证结果
 */
export function isValidPathFormat(path: string): boolean {
  if (!isValidPath(path)) return false;
  
  const trimmedPath = path.trim();
  
  // Windows 路径验证
  // @ts-ignore - process 对象在浏览器环境中不存在，但在 Node.js 环境中可用
  if (typeof process !== 'undefined' && process.platform === 'win32') {
    return /^[a-zA-Z]:\\/.test(trimmedPath) || trimmedPath.startsWith('\\\\');
  }
  
  // Unix 路径验证
  return trimmedPath.startsWith('/');
}

/**
 * 获取路径验证错误信息
 * @param path - 待验证的路径
 * @returns 错误信息，如果验证通过则返回空字符串
 */
export function getPathValidationError(path: string): string {
  if (!isValidPath(path)) {
    return '路径不能为空';
  }
  
  if (!isValidPathFormat(path)) {
    return '路径格式不正确';
  }
  
  return '';
}
