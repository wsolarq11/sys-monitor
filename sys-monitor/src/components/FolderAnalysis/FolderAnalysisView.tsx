import { formatSize } from '../../utils/format';
import { formatTimestamp } from '../../utils/time';

/**
 * 扫描结果数据
 */
export interface ScanResultData {
  total_size: number;
  file_count: number;
  folder_count: number;
  scan_duration_ms: number;
}

/**
 * 扫描历史记录
 */
export interface FolderScan {
  id: number;
  path: string;
  scan_timestamp: number;
  total_size: number;
  file_count: number;
  folder_count: number;
  scan_duration_ms: number | null;
}

/**
 * FolderAnalysisView 组件的 Props
 */
export interface FolderAnalysisViewProps {
  /** 当前选中的路径 */
  selectedPath: string;
  /** 路径输入框变化回调 */
  onPathChange: (path: string) => void;
  /** 选择文件夹按钮点击回调 */
  onSelectFolder: () => void;
  /** 扫描按钮点击回调 */
  onScan: () => void;
  /** 是否正在扫描中 */
  isScanning: boolean;
  /** 错误信息 */
  error: string | null;
  /** 扫描进度/状态信息 */
  scanProgress: string | null;
  /** 扫描结果 */
  scanResult: ScanResultData | null;
  /** 扫描历史记录 */
  scans: FolderScan[];
}

/**
 * FolderAnalysisView - Presentational 组件
 * 负责接收 props 并渲染 UI，不包含任何业务逻辑
 */
export function FolderAnalysisView({
  selectedPath,
  onPathChange,
  onSelectFolder,
  onScan,
  isScanning,
  error,
  scanProgress,
  scanResult,
  scans
}: FolderAnalysisViewProps) {
  return (
    <div className="p-6 space-y-6">
      {/* 路径输入和扫描控制区 */}
      <div className="flex items-center gap-4">
        <input
          type="text"
          value={selectedPath}
          onChange={(e) => onPathChange(e.target.value)}
          placeholder="输入文件夹路径"
          className="flex-1 px-4 py-2 border rounded-lg text-gray-900 bg-white"
        />
        <button
          onClick={onSelectFolder}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          浏览...
        </button>
        <button
          onClick={onScan}
          disabled={isScanning}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg disabled:bg-gray-400"
        >
          {isScanning ? '扫描中...' : '扫描文件夹'}
        </button>
      </div>

      {/* 错误信息 */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* 扫描进度 */}
      {scanProgress && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-700">{scanProgress}</p>
        </div>
      )}

      {/* 扫描结果 */}
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

      {/* 扫描历史 */}
      {scans.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-2">扫描历史</h3>
          <div className="space-y-2">
            {scans.map((scan) => (
              <div key={scan.id} className="p-3 bg-gray-50 rounded-lg border">
                <p className="font-medium truncate">{scan.path}</p>
                <p className="text-sm text-gray-600">
                  {formatTimestamp(scan.scan_timestamp)} - 
                  {formatSize(scan.total_size)} - 
                  {scan.file_count} 个文件，{scan.folder_count} 个文件夹
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
