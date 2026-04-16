import { useState, useEffect, useCallback } from 'react';
import { FolderAnalysisView, type FolderScan, type ScanResultData } from './FolderAnalysisView';
import { WatchedFoldersList } from './WatchedFoldersList';
import { getPathValidationError } from '../../utils/validation';
import {
  selectFolder,
  getDbPath,
  scanFolder,
  getFolderScans,
} from '../../services/folderAnalysisApi';
import { handleTauriError, clearError } from '../../utils/errorHandler';

/**
 * FolderAnalysisContainer - Container 组件
 * 负责管理状态、调用 Tauri 命令、处理业务逻辑
 */
export function FolderAnalysisContainer() {
  // 状态管理
  const [selectedPath, setSelectedPath] = useState('');
  const [scans, setScans] = useState<FolderScan[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResultData | null>(null);
  const [dbPath, setDbPath] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [scanProgress, setScanProgress] = useState<string | null>(null);

  // 初始化时获取数据库路径
  useEffect(() => {
    const fetchDbPath = async () => {
      try {
        const path = await getDbPath();
        setDbPath(path);
      } catch (error) {
        console.error('Failed to get database path:', error);
        setDbPath('data.db'); // 降级值
      }
    };
    fetchDbPath();
  }, []);

  // 处理选择文件夹
  const handleSelectFolder = useCallback(async () => {
    try {
      const path = await selectFolder();
      if (!path) {
        // 用户取消操作，静默处理
        return;
      }
      setSelectedPath(path);
      clearError(setError);
    } catch (error) {
      handleTauriError(error, {
        context: '选择文件夹',
        setError,
        silentOnCancel: true,
      });
    }
  }, []);

  // 处理路径输入变化
  const handlePathChange = useCallback((path: string) => {
    setSelectedPath(path);
    setError(null);
  }, []);

  // 处理扫描
  const handleScan = useCallback(async () => {
    // 验证路径
    const validationError = getPathValidationError(selectedPath);
    if (validationError) {
      setError(validationError);
      return;
    }

    // 检查 dbPath 是否已加载
    if (!dbPath) {
      setError('系统初始化中，请稍后重试');
      return;
    }

    setIsScanning(true);
    setScanResult(null);
    clearError(setError);
    setScanProgress('正在初始化扫描...');

    try {
      setScanProgress('正在扫描文件夹...');

      // 并行执行扫描和获取历史（优化性能）
      const [result, historyScans] = await Promise.all([
        scanFolder(selectedPath, dbPath),
        getFolderScans(selectedPath, dbPath, 10),
      ]);

      setScanResult(result);
      setScans(historyScans);
      setScanProgress(null);
    } catch (error) {
      handleTauriError(error, {
        context: '扫描文件夹',
        setError,
        errorMessagePrefix: '扫描失败',
      });
      setScanProgress('扫描失败');
    } finally {
      setIsScanning(false);
    }
  }, [selectedPath, dbPath]);

  return (
    <div className="space-y-6">
      {/* 监控文件夹列表 */}
      <WatchedFoldersList />
      
      {/* 单次扫描UI */}
      <FolderAnalysisView
        selectedPath={selectedPath}
        onPathChange={handlePathChange}
        onSelectFolder={handleSelectFolder}
        onScan={handleScan}
        isScanning={isScanning}
        error={error}
        scanProgress={scanProgress}
        scanResult={scanResult}
        scans={scans}
      />
    </div>
  );
}
