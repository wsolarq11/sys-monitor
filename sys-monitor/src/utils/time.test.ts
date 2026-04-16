/**
 * 时间处理函数单元测试
 * 测试范围: formatTimestamp, formatTimestampShort, formatDuration, formatRelativeTime
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { formatTimestamp, formatTimestampShort, formatDuration, formatRelativeTime } from './time';

describe('formatTimestamp', () => {
  it('应该正确格式化 Unix 时间戳', () => {
    const timestamp = 1700000000; // 2023-11-14 22:13:20 UTC
    const result = formatTimestamp(timestamp);
    expect(result).toBeTruthy();
    expect(typeof result).toBe('string');
  });

  it('应该处理零时间戳', () => {
    const result = formatTimestamp(0);
    expect(result).toContain('1970');
  });

  it('应该处理当前时间', () => {
    const now = Math.floor(Date.now() / 1000);
    const result = formatTimestamp(now);
    expect(result).toBeTruthy();
  });

  it('应该处理未来时间', () => {
    const future = Math.floor(Date.now() / 1000) + 86400; // 明天
    const result = formatTimestamp(future);
    expect(result).toBeTruthy();
  });
});

describe('formatTimestampShort', () => {
  it('应该返回简短格式的日期时间', () => {
    const timestamp = 1700000000;
    const result = formatTimestampShort(timestamp);
    expect(result).toBeTruthy();
    expect(typeof result).toBe('string');
  });

  it('应该只包含月、日、时、分', () => {
    const timestamp = 1700000000;
    const result = formatTimestampShort(timestamp);
    // 短格式不应包含秒和年份
    expect(result).not.toMatch(/:\d{2}:\d{2}/);
  });

  it('应该正确处理边界值', () => {
    expect(formatTimestampShort(0)).toBeTruthy();
    expect(formatTimestampShort(Math.floor(Date.now() / 1000))).toBeTruthy();
  });
});

describe('formatDuration', () => {
  describe('毫秒级别', () => {
    it('应该显示毫秒单位', () => {
      expect(formatDuration(0)).toBe('0ms');
      expect(formatDuration(1)).toBe('1ms');
      expect(formatDuration(500)).toBe('500ms');
      expect(formatDuration(999)).toBe('999ms');
    });
  });

  describe('秒级别', () => {
    it('应该转换为秒并保留两位小数', () => {
      expect(formatDuration(1000)).toBe('1.00s');
      expect(formatDuration(1500)).toBe('1.50s');
      expect(formatDuration(2000)).toBe('2.00s');
      expect(formatDuration(1234)).toBe('1.23s');
    });

    it('应该处理较大的秒数', () => {
      expect(formatDuration(60000)).toBe('60.00s');
      expect(formatDuration(3600000)).toBe('3600.00s');
    });
  });

  describe('边界情况', () => {
    it('应该处理负数（虽然不常见）', () => {
      expect(formatDuration(-100)).toBe('-100ms');
      expect(formatDuration(-1000)).toBe('-1000ms');
    });

    it('应该处理极大值', () => {
      expect(formatDuration(Number.MAX_SAFE_INTEGER)).toBeTruthy();
    });
  });
});

describe('formatRelativeTime', () => {
  let now: number;

  beforeEach(() => {
    // 固定当前时间为 2024-01-01 12:00:00
    now = 1704067200;
    vi.useFakeTimers();
    vi.setSystemTime(new Date(now * 1000));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('刚刚', () => {
    it('应该显示"刚刚"对于最近的时间', () => {
      const recent = now - 30; // 30秒前
      expect(formatRelativeTime(recent)).toBe('刚刚');
    });

    it('应该显示"刚刚"对于不到一分钟的时间', () => {
      const recent = now - 59;
      expect(formatRelativeTime(recent)).toBe('刚刚');
    });
  });

  describe('分钟前', () => {
    it('应该正确显示分钟数', () => {
      const oneMinAgo = now - 60;
      expect(formatRelativeTime(oneMinAgo)).toBe('1分钟前');

      const fiveMinAgo = now - 300;
      expect(formatRelativeTime(fiveMinAgo)).toBe('5分钟前');

      const thirtyMinAgo = now - 1800;
      expect(formatRelativeTime(thirtyMinAgo)).toBe('30分钟前');
    });
  });

  describe('小时前', () => {
    it('应该正确显示小时数', () => {
      const oneHourAgo = now - 3600;
      expect(formatRelativeTime(oneHourAgo)).toBe('1小时前');

      const threeHoursAgo = now - 10800;
      expect(formatRelativeTime(threeHoursAgo)).toBe('3小时前');

      const twelveHoursAgo = now - 43200;
      expect(formatRelativeTime(twelveHoursAgo)).toBe('12小时前');
    });
  });

  describe('天前', () => {
    it('应该正确显示天数', () => {
      const oneDayAgo = now - 86400;
      expect(formatRelativeTime(oneDayAgo)).toBe('1天前');

      const threeDaysAgo = now - 259200;
      expect(formatRelativeTime(threeDaysAgo)).toBe('3天前');

      const sevenDaysAgo = now - 604800;
      expect(formatRelativeTime(sevenDaysAgo)).toBe('7天前');
    });
  });

  describe('边界情况', () => {
    it('应该处理未来时间', () => {
      const future = now + 3600;
      const result = formatRelativeTime(future);
      expect(result).toBe('刚刚'); // 未来时间应该显示为"刚刚"
    });

    it('应该处理很久以前的时间', () => {
      const longAgo = now - 86400 * 365; // 一年前
      expect(formatRelativeTime(longAgo)).toBe('365天前');
    });
  });
});

describe('集成测试 - 时间格式化组合', () => {
  it('应该能够组合使用不同的时间格式化函数', () => {
    const timestamp = Math.floor(Date.now() / 1000);
    
    const fullFormat = formatTimestamp(timestamp);
    const shortFormat = formatTimestampShort(timestamp);
    const relativeFormat = formatRelativeTime(timestamp);
    
    expect(fullFormat).toBeTruthy();
    expect(shortFormat).toBeTruthy();
    expect(relativeFormat).toBeTruthy();
    
    // 相对时间应该是"刚刚"
    expect(relativeFormat).toBe('刚刚');
  });

  it('应该正确处理扫描耗时格式化', () => {
    const scanDurations = [
      { ms: 500, expected: '500ms' },
      { ms: 1500, expected: '1.50s' },
      { ms: 5000, expected: '5.00s' },
    ];

    scanDurations.forEach(({ ms, expected }) => {
      expect(formatDuration(ms)).toBe(expected);
    });
  });
});

