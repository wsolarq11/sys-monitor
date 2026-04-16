/**
 * 路径验证函数单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { isValidPath, isValidPathFormat, getPathValidationError } from './validation';

describe('isValidPath', () => {
  describe('有效路径', () => {
    it('应该接受非空字符串', () => {
      expect(isValidPath('C:\\\\test')).toBe(true);
      expect(isValidPath('/home/user')).toBe(true);
      expect(isValidPath('relative/path')).toBe(true);
    });
  });

  describe('无效路径', () => {
    it('应该拒绝空字符串', () => {
      expect(isValidPath('')).toBe(false);
    });

    it('应该拒绝纯空白字符串', () => {
      expect(isValidPath('   ')).toBe(false);
    });

    it('应该拒绝非字符串类型', () => {
      // @ts-ignore
      expect(isValidPath(null)).toBe(false);
      // @ts-ignore
      expect(isValidPath(undefined)).toBe(false);
      // @ts-ignore
      expect(isValidPath(123)).toBe(false);
    });
  });
});

describe('isValidPathFormat', () => {
  describe('Windows 路径格式', () => {
    beforeEach(() => {
      vi.stubGlobal('process', { platform: 'win32' });
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it('应该接受标准的 Windows 盘符路径', () => {
      expect(isValidPathFormat('C:\\\\')).toBe(true);
      expect(isValidPathFormat('D:\\\\folder')).toBe(true);
    });

    it('应该接受 UNC 路径', () => {
      expect(isValidPathFormat('\\\\\\\\server\\\\share')).toBe(true);
    });

    it('应该拒绝无效的 Windows 路径', () => {
      expect(isValidPathFormat('C:/')).toBe(false);
      expect(isValidPathFormat('/unix/path')).toBe(false);
    });
  });

  describe('Unix 路径格式', () => {
    beforeEach(() => {
      vi.stubGlobal('process', { platform: 'linux' });
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it('应该接受绝对 Unix 路径', () => {
      expect(isValidPathFormat('/')).toBe(true);
      expect(isValidPathFormat('/home')).toBe(true);
    });

    it('应该拒绝相对路径', () => {
      expect(isValidPathFormat('home/user')).toBe(false);
    });
  });
});

describe('getPathValidationError', () => {
  describe('成功验证', () => {
    beforeEach(() => {
      vi.stubGlobal('process', { platform: 'win32' });
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it('应该对有效Windows路径返回空字符串', () => {
      expect(getPathValidationError('C:\\\\test')).toBe('');
    });
  });

  describe('空路径错误', () => {
    it('应该对空路径返回正确的错误信息', () => {
      expect(getPathValidationError('')).toBe('路径不能为空');
      expect(getPathValidationError('   ')).toBe('路径不能为空');
    });
  });

  describe('格式错误', () => {
    beforeEach(() => {
      vi.stubGlobal('process', { platform: 'win32' });
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it('应该对格式错误的路径返回正确的错误信息', () => {
      expect(getPathValidationError('invalid-path')).toBe('路径格式不正确');
    });
  });
});
