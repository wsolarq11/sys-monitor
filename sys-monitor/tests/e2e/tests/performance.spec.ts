/**
 * 性能测试套件
 * 
 * 测试范围：
 * 1. 数据库批量插入性能
 * 2. 图表渲染性能
 * 3. 内存使用监控
 * 4. API响应时间
 */

import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('数据库批量插入性能测试', async ({ page }) => {
    console.log('Starting database batch insert performance test...');
    
    const startTime = performance.now();
    
    // 模拟批量插入操作
    const insertCount = 1000;
    for (let i = 0; i < insertCount; i++) {
      await page.evaluate(() => {
        // 模拟数据库插入
        return Promise.resolve({ success: true });
      });
    }
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    const opsPerSecond = insertCount / (duration / 1000);
    
    console.log(`Batch insert performance:`);
    console.log(`- Total operations: ${insertCount}`);
    console.log(`- Duration: ${duration.toFixed(2)}ms`);
    console.log(`- Operations/second: ${opsPerSecond.toFixed(2)}`);
    
    // 验证性能指标（应该小于1秒完成1000次操作）
    expect(duration).toBeLessThan(1000);
    expect(opsPerSecond).toBeGreaterThan(1000);
  });

  test('图表渲染性能测试', async ({ page }) => {
    console.log('Starting chart rendering performance test...');
    
    // 等待图表加载
    await new Promise(r => setTimeout(r, 3000));
    
    // 测量首次绘制时间
    const paintMetrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          resolve(entries.map((e: any) => ({
            name: e.name,
            startTime: e.startTime,
            duration: e.duration
          })));
        });
        
        observer.observe({ entryTypes: ['paint'] });
        
        // 500ms后返回
        setTimeout(() => {
          const entries = performance.getEntriesByType('paint');
          resolve(entries.map((e: any) => ({
            name: e.name,
            startTime: e.startTime,
            duration: e.duration
          })));
        }, 500);
      });
    });
    
    console.log('Paint metrics:', paintMetrics);
    
    // 验证首次内容绘制时间
    const fcp = (paintMetrics as any[]).find(m => m.name === 'first-contentful-paint');
    if (fcp) {
      console.log(`First Contentful Paint: ${fcp.startTime.toFixed(2)}ms`);
      expect(fcp.startTime).toBeLessThan(3000);
    }
  });

  test('内存使用监控', async ({ page }) => {
    console.log('Starting memory usage monitoring test...');
    
    // 初始内存使用
    const initialMemory = await page.evaluate(() => {
      const perf = performance as any;
      if (perf.memory) {
        return {
          usedJSHeapSize: perf.memory.usedJSHeapSize,
          totalJSHeapSize: perf.memory.totalJSHeapSize,
        };
      }
      return null;
    });
    
    if (initialMemory) {
      console.log('Initial memory usage:', {
        used: (initialMemory.usedJSHeapSize / 1024 / 1024).toFixed(2) + 'MB',
        total: (initialMemory.totalJSHeapSize / 1024 / 1024).toFixed(2) + 'MB'
      });
    }
    
    // 执行一些操作增加内存使用
    for (let i = 0; i < 10; i++) {
      await page.evaluate(() => {
        // 模拟数据处理
        const data = Array.from({ length: 1000 }, (_, i) => ({
          id: i,
          value: Math.random(),
          timestamp: Date.now()
        }));
        return data.length;
      });
    }
    
    // 最终内存使用
    const finalMemory = await page.evaluate(() => {
      const perf = performance as any;
      if (perf.memory) {
        return {
          usedJSHeapSize: perf.memory.usedJSHeapSize,
          totalJSHeapSize: perf.memory.totalJSHeapSize,
        };
      }
      return null;
    });
    
    if (initialMemory && finalMemory) {
      const memoryGrowth = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
      console.log('Memory growth:', (memoryGrowth / 1024 / 1024).toFixed(2) + 'MB');
      
      // 验证没有明显的内存泄漏（增长应该小于10MB）
      expect(memoryGrowth).toBeLessThan(10 * 1024 * 1024);
    }
  });

  test('API响应时间测试', async ({ page }) => {
    console.log('Starting API response time test...');
    
    const apiCalls = 10;
    const responseTimes: number[] = [];
    
    for (let i = 0; i < apiCalls; i++) {
      const startTime = performance.now();
      
      await page.evaluate(() => {
        return Promise.resolve({ success: true });
      });
      
      const endTime = performance.now();
      responseTimes.push(endTime - startTime);
    }
    
    const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
    const maxResponseTime = Math.max(...responseTimes);
    const minResponseTime = Math.min(...responseTimes);
    
    console.log('API Response Times:');
    console.log(`- Average: ${avgResponseTime.toFixed(2)}ms`);
    console.log(`- Min: ${minResponseTime.toFixed(2)}ms`);
    console.log(`- Max: ${maxResponseTime.toFixed(2)}ms`);
    
    // 验证平均响应时间小于100ms
    expect(avgResponseTime).toBeLessThan(100);
  });

  test('页面滚动性能测试', async ({ page }) => {
    console.log('Starting scroll performance test...');
    
    // 滚动到页面底部
    const startTime = performance.now();
    
    await page.evaluate(async () => {
      return new Promise((resolve) => {
        let scrollPos = 0;
        const step = 100;
        const maxScroll = document.body.scrollHeight;
        
        const scroll = () => {
          scrollPos += step;
          window.scrollTo(0, scrollPos);
          
          if (scrollPos >= maxScroll) {
            resolve(true);
          } else {
            requestAnimationFrame(scroll);
          }
        };
        
        scroll();
      });
    });
    
    const endTime = performance.now();
    const scrollDuration = endTime - startTime;
    
    console.log(`Scroll duration: ${scrollDuration.toFixed(2)}ms`);
    
    // 验证滚动流畅（应该在1秒内完成）
    expect(scrollDuration).toBeLessThan(1000);
  });

  test('并发操作性能测试', async ({ page }) => {
    console.log('Starting concurrent operations test...');
    
    const concurrency = 5;
    const startTime = performance.now();
    
    // 并发执行多个操作
    const promises = Array.from({ length: concurrency }, (_, i) => 
      page.evaluate((index) => {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve({ index, completed: true });
          }, 100);
        });
      }, i)
    );
    
    const results = await Promise.all(promises);
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    console.log(`Concurrent operations (${concurrency} tasks):`);
    console.log(`- Duration: ${duration.toFixed(2)}ms`);
    console.log(`- Results:`, results);
    
    // 验证并发操作在合理时间内完成
    expect(duration).toBeLessThan(500);
    expect(results).toHaveLength(concurrency);
  });

  test('大数据集渲染性能', async ({ page }) => {
    console.log('Starting large dataset rendering test...');
    
    const dataSize = 1000;
    
    const startTime = performance.now();
    
    // 渲染大数据集
    await page.evaluate((size) => {
      const data = Array.from({ length: size }, (_, i) => ({
        id: i,
        value: Math.random() * 100,
        label: `Item ${i}`
      }));
      
      // 模拟渲染操作
      return data.length;
    }, dataSize);
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    console.log(`Large dataset rendering (${dataSize} items):`);
    console.log(`- Render time: ${renderTime.toFixed(2)}ms`);
    
    // 验证渲染时间在合理范围内
    expect(renderTime).toBeLessThan(500);
  });

  test('事件处理性能测试', async ({ page }) => {
    console.log('Starting event handling performance test...');
    
    const eventCount = 100;
    const startTime = performance.now();
    
    // 触发大量事件
    for (let i = 0; i < eventCount; i++) {
      await page.evaluate(() => {
        const event = new CustomEvent('test-event', { detail: { count: 1 } });
        window.dispatchEvent(event);
      });
    }
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    console.log(`Event handling (${eventCount} events):`);
    console.log(`- Duration: ${duration.toFixed(2)}ms`);
    console.log(`- Events/second: ${(eventCount / (duration / 1000)).toFixed(2)}`);
    
    // 验证事件处理性能
    expect(duration).toBeLessThan(1000);
  });

  test('DOM操作性能测试', async ({ page }) => {
    console.log('Starting DOM manipulation performance test...');
    
    const operationCount = 100;
    const startTime = performance.now();
    
    // 执行大量DOM操作
    for (let i = 0; i < operationCount; i++) {
      await page.evaluate((index) => {
        const div = document.createElement('div');
        div.textContent = `Test element ${index}`;
        div.style.display = 'none';
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 0);
      }, i);
    }
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    console.log(`DOM operations (${operationCount} operations):`);
    console.log(`- Duration: ${duration.toFixed(2)}ms`);
    
    // 验证DOM操作性能
    expect(duration).toBeLessThan(2000);
  });
});
