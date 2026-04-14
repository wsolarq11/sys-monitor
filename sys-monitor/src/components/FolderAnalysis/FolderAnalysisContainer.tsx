import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { FolderAnalysisView, type FolderScan, type ScanResultData } from './FolderAnalysisView';
import { getPathValidationError } from '../../utils/validation';

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
        const path = await invoke<string>('get_db_path');
        setDbPath(path);
      } catch (error) {
        console.error('Failed to get database path:', error);
        setDbPath('data.db');
      }
    };
    fetchDbPath();
  }, []);

  // 处理选择文件夹
  const handleSelectFolder = useCallback(async () => {
    console.log('handleSelectFolder called');
    try {
      console.log('Calling select_folder command...');
      const path = await invoke<string>('select_folder');
      console.log('select_folder returned:', path);
      setSelectedPath(path);
      console.log('selectedPath updated to:', path);
      setError(null);
    } catch (error) {
      console.error('Failed to select folder:', error);
      if (String(error).includes('No folder selected')) {
        console.log('User cancelled folder selection');
      } else {
        setError('选择文件夹失败：' + String(error));
      }
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

    console.log('=== 开始扫描流程 ===');
    console.log('扫描路径:', selectedPath);
    console.log('数据库路径:', dbPath);
    
    setIsScanning(true);
    setScanResult(null);
    setError(null);
    setScanProgress('正在初始化扫描...');
    
    try {
      console.log('调用 scan_folder 命令...');
      setScanProgress('正在扫描文件夹...');
      
      const result = await invoke<ScanResultData>('scan_folder', { 
        path: selectedPath, 
        db_path: dbPath 
      });
      
      console.log('扫描成功完成:', result);
      setScanResult(result);
      setScanProgress('扫描完成！');
      
      // 刷新扫描历史
      console.log('刷新扫描历史...');
      setScanProgress('正在加载扫描历史...');
      
      const folderScans: { scans: FolderScan[] } = await invoke<any>('get_folder_scans', { 
        path: selectedPath, 
        limit: 10,
        db_path: dbPath 
      });
      
      console.log('扫描历史加载完成:', folderScans.scans?.length || 0, '条记录');
      setScans(folderScans.scans || []);
      setScanProgress(null);
      
      console.log('=== 扫描流程完成 ===');
      
    } catch (error) {
      console.error('=== 扫描失败 ===');
      console.error('错误详情:', error);
      const errorMsg = String(error);
      console.error('错误消息:', errorMsg);
      setError('扫描失败：' + errorMsg);
      setScanProgress('扫描失败');
    } finally {
      setIsScanning(false);
    }
  }, [selectedPath, dbPath]);

  return (
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
  );
}
