/**
 * 统一错误处理工具
 * 
 * 提供一致的错误处理策略和用户体验
 */

import { isUserCancelled } from '../services/folderAnalysisApi';

/**
 * 错误处理选项
 */
export interface ErrorHandlerOptions {
  /** 上下文描述（用于日志） */
  context?: string;
  
  /** 是否设置组件错误状态 */
  setError?: (error: string | null) => void;
  
  /** 是否显示Toast通知 */
  showToast?: (message: string, description?: string) => void;
  
  /** 是否静默处理用户取消操作 */
  silentOnCancel?: boolean;
  
  /** 自定义错误消息前缀 */
  errorMessagePrefix?: string;
}

/**
 * 统一的 Tauri 错误处理器
 * 
 * @param error - 捕获的错误对象
 * @param options - 错误处理选项
 * 
 * @example
 * ```typescript
 * try {
 *   const path = await selectFolder();
 *   setSelectedPath(path);
 * } catch (error) {
 *   handleTauriError(error, {
 *     context: '选择文件夹',
 *     setError,
 *     showToast,
 *   });
 * }
 * ```
 */
export function handleTauriError(
  error: unknown,
  options: ErrorHandlerOptions = {}
): void {
  const {
    context = '操作',
    setError,
    showToast,
    silentOnCancel = true,
    errorMessagePrefix,
  } = options;

  // 检查是否为用户取消操作
  if (silentOnCancel && isUserCancelled(error)) {
    console.debug(`[ErrorHandler] ${context}: 用户取消操作`);
    return; // 静默处理，不显示错误
  }

  // 格式化错误消息
  const errorMsg = String(error);
  const prefix = errorMessagePrefix || `${context}失败`;
  const fullMessage = `${prefix}：${errorMsg}`;

  // 记录错误日志
  console.error(`[ErrorHandler] ${context}:`, error);

  // 设置组件错误状态
  if (setError) {
    setError(fullMessage);
  }

  // 显示 Toast 通知
  if (showToast) {
    showToast(`${context}失败`, errorMsg);
  }
}

/**
 * 清除错误状态
 * 
 * @param setError - 设置错误的函数
 */
export function clearError(setError: (error: string | null) => void): void {
  setError(null);
}

/**
 * 验证并处理错误
 * 
 * @param condition - 验证条件
 * @param errorMessage - 验证失败时的错误消息
 * @param setError - 设置错误的函数
 * @returns 验证是否通过
 * 
 * @example
 * ```typescript
 * if (!validateCondition(selectedPath !== '', '路径不能为空', setError)) {
 *   return;
 * }
 * ```
 */
export function validateCondition(
  condition: boolean,
  errorMessage: string,
  setError: (error: string | null) => void
): boolean {
  if (!condition) {
    setError(errorMessage);
    return false;
  }
  return true;
}

/**
 * 异步操作包装器 - 自动处理错误和加载状态
 * 
 * @param operation - 要执行的异步操作
 * @param options - 配置选项
 * @returns 操作结果或 null（如果失败）
 * 
 * @example
 * ```typescript
 * const result = await withErrorHandling(
 *   () => scanFolder(path, dbPath),
 *   {
 *     context: '扫描文件夹',
 *     setLoading: setIsScanning,
 *     setError,
 *     showToast,
 *   }
 * );
 * ```
 */
export async function withErrorHandling<T>(
  operation: () => Promise<T>,
  options: ErrorHandlerOptions & {
    setLoading?: (loading: boolean) => void;
    onSuccess?: (result: T) => void;
  }
): Promise<T | null> {
  const { setLoading, onSuccess, ...errorOptions } = options;

  try {
    // 设置加载状态
    if (setLoading) {
      setLoading(true);
    }

    // 执行操作
    const result = await operation();

    // 成功回调
    if (onSuccess) {
      onSuccess(result);
    }

    return result;
  } catch (error) {
    // 错误处理
    handleTauriError(error, errorOptions);
    return null;
  } finally {
    // 清除加载状态
    if (setLoading) {
      setLoading(false);
    }
  }
}

/**
 * 乐观更新包装器 - 支持回滚
 * 
 * @param updateFn - 乐观更新函数
 * @param rollbackFn - 回滚函数
 * @param apiCall - API 调用函数
 * @param options - 错误处理选项
 * @returns API 调用结果或 null
 * 
 * @example
 * ```typescript
 * await optimisticUpdate(
 *   () => toggleFolderInUI(id),
 *   () => toggleFolderInUI(id), // 再次调用以回滚
 *   () => toggleWatchedFolderActive(id, newState, dbPath),
 *   { context: '切换监控状态', setError }
 * );
 * ```
 */
export async function optimisticUpdate<T>(
  updateFn: () => void,
  rollbackFn: () => void,
  apiCall: () => Promise<T>,
  options: ErrorHandlerOptions
): Promise<T | null> {
  try {
    // 1. 执行乐观更新
    updateFn();

    // 2. 调用 API
    const result = await apiCall();

    // 3. 成功，返回结果
    return result;
  } catch (error) {
    // 4. 失败，回滚
    console.warn('[ErrorHandler] 回滚乐观更新');
    rollbackFn();

    // 5. 处理错误
    handleTauriError(error, options);
    return null;
  }
}
