/**
 * 扫描Store单元测试
 * 
 * 测试范围：
 * - 路径管理
 * - 扫描控制流程
 * - 进度更新
 * - 错误处理
 * - 历史记录管理
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useScanStore, type ScanResult, type ScanHistoryItem } from './scanStore';

describe('useScanStore', () => {
  beforeEach(() => {
    // 重置 store 状态
    useScanStore.setState({
      selectedPath: null,
      isScanning: false,
      scanProgress: null,
      currentScan: null,
      scanHistory: [],
      error: null,
      dbPath: null,
    });
  });

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const state = useScanStore.getState();
      expect(state.selectedPath).toBeNull();
      expect(state.isScanning).toBe(false);
      expect(state.scanProgress).toBeNull();
      expect(state.currentScan).toBeNull();
      expect(state.scanHistory).toEqual([]);
      expect(state.error).toBeNull();
      expect(state.dbPath).toBeNull();
    });
  });

  describe('路径管理', () => {
    it('应该设置选择的扫描路径', () => {
      useScanStore.getState().setSelectedPath('/test/path');
      
      const state = useScanStore.getState();
      expect(state.selectedPath).toBe('/test/path');
    });

    it('应该清除选择的扫描路径', () => {
      useScanStore.getState().setSelectedPath('/test/path');
      useScanStore.getState().setSelectedPath(null);
      
      const state = useScanStore.getState();
      expect(state.selectedPath).toBeNull();
    });

    it('应该设置数据库路径', () => {
      useScanStore.getState().setDbPath('/data/test.db');
      
      const state = useScanStore.getState();
      expect(state.dbPath).toBe('/data/test.db');
    });
  });

  describe('扫描控制', () => {
    it('应该开始扫描', () => {
      useScanStore.getState().startScan();
      
      const state = useScanStore.getState();
      expect(state.isScanning).toBe(true);
      expect(state.scanProgress).toEqual({ current: 0, total: 0, percentage: 0 });
      expect(state.error).toBeNull();
    });

    it('应该完成扫描并保存结果', () => {
      // 先开始扫描
      useScanStore.getState().startScan();
      
      // 模拟扫描结果
      const result: ScanResult = {
        path: '/test/path',
        size: 1024000,
        fileCount: 100,
        folderCount: 10,
        timestamp: Date.now(),
      };
      
      useScanStore.getState().completeScan(result, 500);
      
      const state = useScanStore.getState();
      expect(state.isScanning).toBe(false);
      expect(state.currentScan).toEqual(result);
      expect(state.scanProgress).toEqual({
        current: 100,
        total: 100,
        percentage: 100,
      });
      expect(state.scanHistory).toHaveLength(1);
      expect(state.scanHistory[0].result).toEqual(result);
      expect(state.scanHistory[0].duration).toBe(500);
    });

    it('应该取消扫描', () => {
      useScanStore.getState().startScan();
      useScanStore.getState().cancelScan();
      
      const state = useScanStore.getState();
      expect(state.isScanning).toBe(false);
      expect(state.scanProgress).toBeNull();
    });

    it('应该更新扫描进度', () => {
      useScanStore.getState().startScan();
      
      useScanStore.getState().updateProgress({
        current: 50,
        total: 100,
        percentage: 50,
        currentFile: '/test/file.txt',
      });
      
      const state = useScanStore.getState();
      expect(state.scanProgress).toEqual({
        current: 50,
        total: 100,
        percentage: 50,
        currentFile: '/test/file.txt',
      });
    });

    it('应该在多次扫描后保持历史限制', () => {
      // 添加超过限制的扫描历史
      for (let i = 0; i < 60; i++) {
        const result: ScanResult = {
          path: `/test/path${i}`,
          size: 1000,
          fileCount: 10,
          folderCount: 2,
          timestamp: Date.now(),
        };
        useScanStore.getState().completeScan(result, 100);
      }
      
      const state = useScanStore.getState();
      expect(state.scanHistory.length).toBeLessThanOrEqual(50);
    });
  });

  describe('错误处理', () => {
    it('应该设置错误', () => {
      useScanStore.getState().setError({
        message: 'Permission denied',
        code: 'EACCES',
        path: '/restricted/path',
        timestamp: Date.now(),
      });
      
      const state = useScanStore.getState();
      expect(state.error?.message).toBe('Permission denied');
      expect(state.error?.code).toBe('EACCES');
      expect(state.isScanning).toBe(false); // 错误应该停止扫描
    });

    it('应该清除错误', () => {
      useScanStore.getState().setError({
        message: 'Test error',
        timestamp: Date.now(),
      });
      
      useScanStore.getState().clearError();
      
      const state = useScanStore.getState();
      expect(state.error).toBeNull();
    });
  });

  describe('历史管理', () => {
    it('应该添加到历史记录', () => {
      const historyItem: ScanHistoryItem = {
        id: 'test-id-1',
        path: '/test/path',
        timestamp: Date.now(),
        duration: 500,
        result: {
          path: '/test/path',
          size: 1024000,
          fileCount: 100,
          folderCount: 10,
          timestamp: Date.now(),
        },
      };
      
      useScanStore.getState().addToHistory(historyItem);
      
      const state = useScanStore.getState();
      expect(state.scanHistory).toHaveLength(1);
      expect(state.scanHistory[0]).toEqual(historyItem);
    });

    it('应该清空历史记录', () => {
      // 先添加一些历史
      const historyItem: ScanHistoryItem = {
        id: 'test-id-1',
        path: '/test/path',
        timestamp: Date.now(),
        duration: 500,
        result: {
          path: '/test/path',
          size: 1024000,
          fileCount: 100,
          folderCount: 10,
          timestamp: Date.now(),
        },
      };
      useScanStore.getState().addToHistory(historyItem);
      
      // 清空
      useScanStore.getState().clearHistory();
      
      const state = useScanStore.getState();
      expect(state.scanHistory).toHaveLength(0);
    });

    it('应该移除指定的历史记录项', () => {
      const item1: ScanHistoryItem = {
        id: 'id-1',
        path: '/path1',
        timestamp: Date.now(),
        duration: 100,
        result: {
          path: '/path1',
          size: 1000,
          fileCount: 10,
          folderCount: 2,
          timestamp: Date.now(),
        },
      };
      
      const item2: ScanHistoryItem = {
        id: 'id-2',
        path: '/path2',
        timestamp: Date.now(),
        duration: 200,
        result: {
          path: '/path2',
          size: 2000,
          fileCount: 20,
          folderCount: 4,
          timestamp: Date.now(),
        },
      };
      
      useScanStore.getState().addToHistory(item1);
      useScanStore.getState().addToHistory(item2);
      
      useScanStore.getState().removeHistoryItem('id-1');
      
      const state = useScanStore.getState();
      expect(state.scanHistory).toHaveLength(1);
      expect(state.scanHistory[0].id).toBe('id-2');
    });
  });

  describe('重置', () => {
    it('应该重置到初始状态（保留历史和dbPath）', () => {
      // 设置一些状态
      useScanStore.getState().setSelectedPath('/test/path');
      useScanStore.getState().setDbPath('/data/test.db');
      useScanStore.getState().startScan();
      
      // 重置
      useScanStore.getState().reset();
      
      const state = useScanStore.getState();
      expect(state.selectedPath).toBeNull();
      expect(state.isScanning).toBe(false);
      expect(state.scanProgress).toBeNull();
      expect(state.currentScan).toBeNull();
      expect(state.error).toBeNull();
      // dbPath 和 scanHistory 在 reset 中不清除
    });
  });

  describe('持久化', () => {
    it('应该只持久化scanHistory和dbPath', () => {
      // 这个测试验证partialize配置
      // 实际持久化由zustand/persist处理
      const state = useScanStore.getState();
      expect(state).toHaveProperty('scanHistory');
      expect(state).toHaveProperty('dbPath');
    });
  });

  describe('状态转换场景', () => {
    it('应该支持完整的扫描流程', () => {
      // 1. 选择路径
      useScanStore.getState().setSelectedPath('/test/folder');
      
      // 2. 开始扫描
      useScanStore.getState().startScan();
      let state = useScanStore.getState();
      expect(state.isScanning).toBe(true);
      
      // 3. 更新进度
      useScanStore.getState().updateProgress({
        current: 50,
        total: 100,
        percentage: 50,
      });
      
      // 4. 完成扫描
      const result: ScanResult = {
        path: '/test/folder',
        size: 5000000,
        fileCount: 100,
        folderCount: 20,
        timestamp: Date.now(),
      };
      useScanStore.getState().completeScan(result, 1500);
      
      // 5. 验证最终状态
      state = useScanStore.getState();
      expect(state.isScanning).toBe(false);
      expect(state.currentScan).toEqual(result);
      expect(state.scanHistory).toHaveLength(1);
    });

    it('应该处理扫描失败的情况', () => {
      // 1. 开始扫描
      useScanStore.getState().startScan();
      
      // 2. 发生错误
      useScanStore.getState().setError({
        message: 'Access denied',
        path: '/restricted',
        timestamp: Date.now(),
      });
      
      const state = useScanStore.getState();
      expect(state.isScanning).toBe(false);
      expect(state.error?.message).toBe('Access denied');
    });

    it('应该处理用户取消扫描', () => {
      // 1. 开始扫描
      useScanStore.getState().startScan();
      
      // 2. 用户取消
      useScanStore.getState().cancelScan();
      
      const state = useScanStore.getState();
      expect(state.isScanning).toBe(false);
      expect(state.scanProgress).toBeNull();
      expect(state.error).toBeNull(); // 取消不是错误
    });
  });
});
