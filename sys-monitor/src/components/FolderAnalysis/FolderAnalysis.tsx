import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';

interface FolderScan {
  id: number;
  path: string;
  scan_timestamp: number;
  total_size: number;
  file_count: number;
  folder_count: number;
  scan_duration_ms: number | null;
}

export default function FolderAnalysis() {
  const [selectedPath, setSelectedPath] = useState('');
  const [scans, setScans] = useState<FolderScan[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);
  const [dbPath, setDbPath] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [scanProgress, setScanProgress] = useState<string>('');

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

  const handleSelectFolder = async () => {
    console.log('handleSelectFolder called');
    try {
      console.log('Calling select_folder command...');
      const path = await invoke<string>('select_folder');
      console.log('select_folder returned:', path);
      setSelectedPath(path);
      console.log('selectedPath updated to:', path);
      alert(`Selected: ${path}`);
    } catch (error) {
      console.error('Failed to select folder:', error);
      // User cancelled the dialog, this is not an error
      if (String(error).includes('No folder selected')) {
        console.log('User cancelled folder selection');
      } else {
        alert('Failed to select folder: ' + String(error));
      }
    }
  };

  const handleScan = async () => {
    if (!selectedPath) {
      setError('请选择一个文件夹路径');
      return;
    }

    console.log('=== 开始扫描流程 ===');
    console.log('扫描路径:', selectedPath);
    console.log('数据库路径:', dbPath);
    
    setIsScanning(true);
    setScanResult(null);
    setError('');
    setScanProgress('正在初始化扫描...');
    
    try {
      console.log('调用 scan_folder 命令...');
      setScanProgress('正在扫描文件夹...');
      
      const result = await invoke<any>('scan_folder', { 
        path: selectedPath, 
        db_path: dbPath 
      });
      
      console.log('扫描成功完成:', result);
      setScanResult(result);
      setScanProgress('扫描完成！');
      
      // Refresh scans
      console.log('刷新扫描历史...');
      setScanProgress('正在加载扫描历史...');
      
      const folderScans: { scans: FolderScan[] } = await invoke<any>('get_folder_scans', { 
        path: selectedPath, 
        limit: 10,
        db_path: dbPath 
      });
      
      console.log('扫描历史加载完成:', folderScans.scans?.length || 0, '条记录');
      setScans(folderScans.scans || []);
      setScanProgress('');
      
      console.log('=== 扫描流程完成 ===');
      
    } catch (error) {
      console.error('=== 扫描失败 ===');
      console.error('错误详情:', error);
      const errorMsg = String(error);
      console.error('错误消息:', errorMsg);
      setError('扫描失败: ' + errorMsg);
      setScanProgress('扫描失败');
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <input
          type="text"
          value={selectedPath}
          onChange={(e) => {
            setSelectedPath(e.target.value);
            setError('');
          }}
          placeholder="输入文件夹路径"
          className="flex-1 px-4 py-2 border rounded-lg text-gray-900 bg-white"
        />
        <button
          onClick={handleSelectFolder}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          浏览...
        </button>
        <button
          onClick={handleScan}
          disabled={isScanning}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg disabled:bg-gray-400"
        >
          {isScanning ? '扫描中...' : '扫描文件夹'}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {scanProgress && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-700">{scanProgress}</p>
        </div>
      )}

      {scanResult && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800">扫描完成</h3>
          <div className="grid grid-cols-2 gap-2 mt-2">
            <p><span className="font-medium">总大小:</span> {formatSize(scanResult.total_size)}</p>
            <p><span className="font-medium">文件数:</span> {scanResult.file_count}</p>
            <p><span className="font-medium">文件夹数:</span> {scanResult.folder_count}</p>
            <p><span className="font-medium">扫描耗时:</span> {scanResult.scan_duration_ms}ms</p>
          </div>
        </div>
      )}

      {scans.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-2">扫描历史</h3>
          <div className="space-y-2">
            {scans.map((scan) => (
              <div key={scan.id} className="p-3 bg-gray-50 rounded-lg border">
                <p className="font-medium truncate">{scan.path}</p>
                <p className="text-sm text-gray-600">
                  {new Date(scan.scan_timestamp * 1000).toLocaleString('zh-CN')} - 
                  {formatSize(scan.total_size)} - 
                  {scan.file_count} 个文件, {scan.folder_count} 个文件夹
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}
