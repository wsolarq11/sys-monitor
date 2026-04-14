/**
 * 第七阶段：前端工具函数单元测试
 * 测试范围：formatBytes, formatPercent, formatSize
 */

import { describe, it, expect } from 'vitest';
import { formatBytes, formatPercent, formatSize } from './format';

describe('formatBytes', () => {
  describe('零值处理', () => {
    it('应该正确处理 0 字节', () => {
      expect(formatBytes(0)).toBe('0 B');
    });
  });

  describe('字节级别', () => {
    it('应该显示原始字节数（小于 1KB）', () => {
      expect(formatBytes(1)).toBe('1 B');
      expect(formatBytes(500)).toBe('500 B');
      expect(formatBytes(1023)).toBe('1023 B');
    });
  });

  describe('KB 级别', () => {
    it('应该正确转换为 KB', () => {
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1536)).toBe('1.5 KB');
      expect(formatBytes(2048)).toBe('2 KB');
      expect(formatBytes(10240)).toBe('10 KB');
    });
  });

  describe('MB 级别', () => {
    it('应该正确转换为 MB', () => {
      expect(formatBytes(1048576)).toBe('1 MB');
      expect(formatBytes(1572864)).toBe('1.5 MB');
      expect(formatBytes(5242880)).toBe('5 MB');
      expect(formatBytes(10485760)).toBe('10 MB');
    });
  });

  describe('GB 级别', () => {
    it('应该正确转换为 GB', () => {
      expect(formatBytes(1073741824)).toBe('1 GB');
      expect(formatBytes(1610612736)).toBe('1.5 GB');
      expect(formatBytes(5368709120)).toBe('5 GB');
      expect(formatBytes(10737418240)).toBe('10 GB');
    });
  });

  describe('TB 级别', () => {
    it('应该正确转换为 TB', () => {
      expect(formatBytes(1099511627776)).toBe('1 TB');
      expect(formatBytes(2199023255552)).toBe('2 TB');
    });
  });

  describe('精度测试', () => {
    it('应该保留两位小数', () => {
      expect(formatBytes(1234)).toBe('1.21 KB');
      expect(formatBytes(12345)).toBe('12.06 KB');
      expect(formatBytes(123456)).toBe('120.56 KB');
    });
  });

  describe('边界条件', () => {
    it('应该正确处理边界值', () => {
      expect(formatBytes(1023)).toBe('1023 B');
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1048575)).toBe('1024 KB');
      expect(formatBytes(1048576)).toBe('1 MB');
    });
  });
});

describe('formatPercent', () => {
  describe('基本百分比', () => {
    it('应该正确格式化 0%', () => {
      expect(formatPercent(0)).toBe('0.0%');
    });

    it('应该正确格式化 50%', () => {
      expect(formatPercent(50)).toBe('50.0%');
    });

    it('应该正确格式化 100%', () => {
      expect(formatPercent(100)).toBe('100.0%');
    });
  });

  describe('小数值', () => {
    it('应该保留一位小数', () => {
      expect(formatPercent(45.67)).toBe('45.7%');
      expect(formatPercent(99.99)).toBe('100.0%');
      expect(formatPercent(0.123)).toBe('0.1%');
    });
  });

  describe('负数值', () => {
    it('应该正确处理负数', () => {
      expect(formatPercent(-10)).toBe('-10.0%');
      expect(formatPercent(-0.5)).toBe('-0.5%');
    });
  });

  describe('边界值', () => {
    it('应该正确处理极小值', () => {
      expect(formatPercent(0.01)).toBe('0.0%');
      expect(formatPercent(0.05)).toBe('0.1%');
    });
  });
});

describe('formatSize', () => {
  describe('字节级别', () => {
    it('应该显示原始字节数（小于 1KB）', () => {
      expect(formatSize(0)).toBe('0 B');
      expect(formatSize(100)).toBe('100 B');
      expect(formatSize(1023)).toBe('1023 B');
    });
  });

  describe('KB 级别', () => {
    it('应该正确转换为 KB（保留两位小数）', () => {
      expect(formatSize(1024)).toBe('1.00 KB');
      expect(formatSize(2048)).toBe('2.00 KB');
      expect(formatSize(1536)).toBe('1.50 KB');
    });
  });

  describe('MB 级别', () => {
    it('应该正确转换为 MB（保留两位小数）', () => {
      expect(formatSize(1048576)).toBe('1.00 MB');
      expect(formatSize(5242880)).toBe('5.00 MB');
      expect(formatSize(10485760)).toBe('10.00 MB');
    });
  });

  describe('GB 级别', () => {
    it('应该正确转换为 GB（保留两位小数）', () => {
      expect(formatSize(1073741824)).toBe('1.00 GB');
      expect(formatSize(5368709120)).toBe('5.00 GB');
      expect(formatSize(10737418240)).toBe('10.00 GB');
    });
  });

  describe('边界条件', () => {
    it('应该正确处理边界值', () => {
      expect(formatSize(1023)).toBe('1023 B');
      expect(formatSize(1024)).toBe('1.00 KB');
      expect(formatSize(1048575)).toBe('1024.00 KB');
      expect(formatSize(1048576)).toBe('1.00 MB');
    });
  });
});

describe('formatBytes vs formatSize 对比', () => {
  it('应该在 KB 级别有相同的单位但不同精度', () => {
    const bytes1024 = 1024;
    expect(formatBytes(bytes1024)).toBe('1 KB');
    expect(formatSize(bytes1024)).toBe('1.00 KB');
  });

  it('应该在字节级别有不同表现', () => {
    const bytes500 = 500;
    expect(formatBytes(bytes500)).toBe('500 B');
    expect(formatSize(bytes500)).toBe('500 B');
  });
});
