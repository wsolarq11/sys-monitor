import { create } from 'zustand';

/**
 * 扫描进度信息
 */
export interface ScanProgress {
  current: number;      // 当前已扫描项数
  total: number;        // 预计总项数
  percentage: number;   // 完成百分比
  currentFile?: string; // 当前正在扫描的文件路径
}

/**
 * 扫描结果项
 */
export interface ScanResult {
  path: string;
  size: number;
  fileCount: number;
  folderCount: number;
  timestamp: number;
}

/**
 * 扫描历史记录项
 */
export interface ScanHistoryItem {
  id: string;
  path: string;
  timestamp: number;
  duration: number;     // 扫描耗时 (ms)
  result: ScanResult;
}

/**
 * 扫描错误信息
 */
export interface ScanError {
  message: string;
  code?: string;
  path?: string;
  timestamp: number;
}

interface ScanState {
  // 状态
  selectedPath: string | null;          // 当前选择的扫描路径
  isScanning: boolean;                  // 是否正在扫描
  scanProgress: ScanProgress | null;    // 扫描进度
  currentScan: ScanResult | null;       // 当前扫描结果
  scanHistory: ScanHistoryItem[];       // 扫描历史
  error: ScanError | null;              // 错误信息
  dbPath: string | null;                // 数据库路径
  
  // Actions - 路径管理
  setSelectedPath: (path: string | null) => void;
  setDbPath: (path: string | null) => void;
  
  // Actions - 扫描控制
  startScan: () => void;
  completeScan: (result: ScanResult, duration: number) => void;
  cancelScan: () => void;
  updateProgress: (progress: ScanProgress) => void;
  
  // Actions - 错误处理
  setError: (error: ScanError | null) => void;
  clearError: () => void;
  
  // Actions - 历史管理
  addToHistory: (item: ScanHistoryItem) => void;
  clearHistory: () => void;
  removeHistoryItem: (id: string) => void;
  
  // Actions - 重置
  reset: () => void;
}

const SCAN_HISTORY_LIMIT = 50;

export const useScanStore = create<ScanState>((set) => ({
  // 初始状态
  selectedPath: null,
  isScanning: false,
  scanProgress: null,
  currentScan: null,
  scanHistory: [],
  error: null,
  dbPath: null,
  
  // Actions - 路径管理
  setSelectedPath: (path) => set({ selectedPath: path }),
  setDbPath: (path) => set({ dbPath: path }),
  
  // Actions - 扫描控制
  startScan: () => set({
    isScanning: true,
    scanProgress: { current: 0, total: 0, percentage: 0 },
    error: null,
  }),
  
  completeScan: (result, duration) => set((state) => {
    const historyItem: ScanHistoryItem = {
      id: crypto.randomUUID(),
      path: result.path,
      timestamp: Date.now(),
      duration,
      result,
    };
    
    return {
      isScanning: false,
      scanProgress: { current: result.fileCount, total: result.fileCount, percentage: 100 },
      currentScan: result,
      scanHistory: [historyItem, ...state.scanHistory].slice(0, SCAN_HISTORY_LIMIT),
    };
  }),
  
  cancelScan: () => set({
    isScanning: false,
    scanProgress: null,
  }),
  
  updateProgress: (progress) => set({ scanProgress: progress }),
  
  // Actions - 错误处理
  setError: (error) => set({ error, isScanning: false }),
  clearError: () => set({ error: null }),
  
  // Actions - 历史管理
  addToHistory: (item) => set((state) => ({
    scanHistory: [item, ...state.scanHistory].slice(0, SCAN_HISTORY_LIMIT),
  })),
  
  clearHistory: () => set({ scanHistory: [] }),
  removeHistoryItem: (id) => set((state) => ({
    scanHistory: state.scanHistory.filter(item => item.id !== id),
  })),
  
  // Actions - 重置
  reset: () => set({
    selectedPath: null,
    isScanning: false,
    scanProgress: null,
    currentScan: null,
    error: null,
  }),
}));
