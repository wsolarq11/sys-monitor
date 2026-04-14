import * as Sentry from "@sentry/react";

// 混沌测试类型
export enum ChaosTestType {
  NETWORK_LATENCY = 'network_latency',
  NETWORK_DISCONNECT = 'network_disconnect',
  CPU_STRESS = 'cpu_stress',
  MEMORY_LEAK = 'memory_leak',
  STORAGE_FULL = 'storage_full',
  API_FAILURE = 'api_failure',
  RANDOM_ERROR = 'random_error',
  SLOW_RESPONSE = 'slow_response'
}

// 混沌测试配置接口
export interface ChaosTestConfig {
  id: string;
  type: ChaosTestType;
  name: string;
  description: string;
  probability: number; // 0-1 的概率
  duration?: number; // 持续时间（毫秒）
  intensity?: number; // 强度 0-1
  enabled: boolean;
}

// 混沌测试结果接口
export interface ChaosTestResult {
  testId: string;
  type: ChaosTestType;
  timestamp: number;
  duration: number;
  success: boolean;
  error?: string;
  impact: 'low' | 'medium' | 'high';
  metrics?: any;
}

// 混沌测试管理器
export class ChaosManager {
  private tests: ChaosTestConfig[] = [];
  private isActive = false;
  private testInterval: number | null = null;
  private testResults: ChaosTestResult[] = [];
  private maxResults = 1000;

  constructor() {
    this.setupDefaultTests();
  }

  // 设置默认混沌测试
  private setupDefaultTests() {
    this.addTest({
      id: 'network_latency_1',
      type: ChaosTestType.NETWORK_LATENCY,
      name: '网络延迟测试',
      description: '模拟网络延迟，测试应用在网络不佳环境下的表现',
      probability: 0.05, // 5%概率
      duration: 30000, // 30秒
      intensity: 0.3, // 30%强度
      enabled: true
    });

    this.addTest({
      id: 'cpu_stress_1',
      type: ChaosTestType.CPU_STRESS,
      name: 'CPU压力测试',
      description: '模拟CPU高负载，测试应用在资源紧张环境下的表现',
      probability: 0.03, // 3%概率
      duration: 15000, // 15秒
      intensity: 0.5, // 50%强度
      enabled: true
    });

    this.addTest({
      id: 'api_failure_1',
      type: ChaosTestType.API_FAILURE,
      name: 'API失败测试',
      description: '模拟API调用失败，测试应用的错误处理能力',
      probability: 0.02, // 2%概率
      duration: 10000, // 10秒
      intensity: 0.2, // 20%强度
      enabled: true
    });

    this.addTest({
      id: 'slow_response_1',
      type: ChaosTestType.SLOW_RESPONSE,
      name: '慢响应测试',
      description: '模拟慢响应，测试应用的超时处理能力',
      probability: 0.04, // 4%概率
      duration: 20000, // 20秒
      intensity: 0.4, // 40%强度
      enabled: true
    });

    this.addTest({
      id: 'random_error_1',
      type: ChaosTestType.RANDOM_ERROR,
      name: '随机错误测试',
      description: '随机触发各种错误，测试应用的容错能力',
      probability: 0.01, // 1%概率
      duration: 5000, // 5秒
      intensity: 0.1, // 10%强度
      enabled: true
    });
  }

  // 添加混沌测试
  public addTest(test: ChaosTestConfig) {
    this.tests.push(test);
  }

  // 启动混沌测试
  public startChaosTesting() {
    if (this.isActive) return;
    
    this.isActive = true;
    
    // 记录混沌测试启动
    Sentry.captureMessage('Chaos testing started', {
      level: 'info',
      extra: {
        testCount: this.tests.length,
        enabledTests: this.tests.filter(t => t.enabled).length
      }
    });

    // 定期执行混沌测试
    this.testInterval = setInterval(() => {
      this.executeRandomTest();
    }, 60000) as unknown as number; // 每分钟检查一次
  }

  // 停止混沌测试
  public stopChaosTesting() {
    if (!this.isActive) return;
    
    this.isActive = false;
    
    if (this.testInterval) {
      clearInterval(this.testInterval);
      this.testInterval = null;
    }

    // 记录混沌测试停止
    Sentry.captureMessage('Chaos testing stopped', {
      level: 'info',
      extra: {
        totalTests: this.testResults.length,
        successfulTests: this.testResults.filter(r => r.success).length
      }
    });
  }

  // 执行随机测试
  private executeRandomTest() {
    const enabledTests = this.tests.filter(test => test.enabled);
    
    if (enabledTests.length === 0) return;

    // 随机选择一个测试
    const randomTest = enabledTests[Math.floor(Math.random() * enabledTests.length)];
    
    // 根据概率决定是否执行
    if (Math.random() < randomTest.probability) {
      this.executeTest(randomTest);
    }
  }

  // 执行具体测试
  private async executeTest(test: ChaosTestConfig) {
    const startTime = Date.now();
    let success = false;
    let error: string | undefined;

    try {
      // 记录测试开始
      Sentry.captureMessage(`Chaos test started: ${test.name}`, {
        level: 'info',
        extra: {
          testId: test.id,
          type: test.type,
          probability: test.probability,
          duration: test.duration,
          intensity: test.intensity
        }
      });

      // 执行测试
      await this.performChaosTest(test);
      success = true;

      // 记录测试成功
      Sentry.captureMessage(`Chaos test completed: ${test.name}`, {
        level: 'info',
        extra: { testId: test.id, duration: Date.now() - startTime }
      });

    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
      
      // 记录测试失败
      Sentry.captureMessage(`Chaos test failed: ${test.name}`, {
        level: 'error',
        extra: { testId: test.id, error: error }
      });
    }

    // 保存测试结果
    const result: ChaosTestResult = {
      testId: test.id,
      type: test.type,
      timestamp: startTime,
      duration: Date.now() - startTime,
      success,
      error,
      impact: this.calculateImpact(test)
    };

    this.testResults.push(result);

    // 限制结果数量
    if (this.testResults.length > this.maxResults) {
      this.testResults = this.testResults.slice(-this.maxResults);
    }
  }

  // 执行具体的混沌测试
  private async performChaosTest(test: ChaosTestConfig): Promise<void> {
    switch (test.type) {
      case ChaosTestType.NETWORK_LATENCY:
        await this.simulateNetworkLatency(test);
        break;
      case ChaosTestType.CPU_STRESS:
        await this.simulateCpuStress(test);
        break;
      case ChaosTestType.API_FAILURE:
        await this.simulateApiFailure(test);
        break;
      case ChaosTestType.SLOW_RESPONSE:
        await this.simulateSlowResponse(test);
        break;
      case ChaosTestType.RANDOM_ERROR:
        await this.simulateRandomError(test);
        break;
      default:
        throw new Error(`Unsupported chaos test type: ${test.type}`);
    }
  }

  // 模拟网络延迟
  private async simulateNetworkLatency(test: ChaosTestConfig): Promise<void> {
    const latency = (test.intensity || 0.5) * 1000; // 最大1秒延迟
    
    // 记录网络延迟开始
    Sentry.addBreadcrumb({
      category: 'chaos.network',
      message: 'Network latency simulation started',
      level: 'info',
      data: { latency, duration: test.duration }
    });

    // 在实际应用中，这里可以修改网络请求的延迟
    // 目前只是记录和等待
    await new Promise(resolve => setTimeout(resolve, test.duration || 30000));

    // 记录网络延迟结束
    Sentry.addBreadcrumb({
      category: 'chaos.network',
      message: 'Network latency simulation completed',
      level: 'info',
      data: { actualDuration: test.duration }
    });
  }

  // 模拟CPU压力
  private async simulateCpuStress(test: ChaosTestConfig): Promise<void> {
    const intensity = test.intensity || 0.5;
    const duration = test.duration || 15000;
    
    // 记录CPU压力开始
    Sentry.addBreadcrumb({
      category: 'chaos.cpu',
      message: 'CPU stress simulation started',
      level: 'info',
      data: { intensity, duration }
    });

    // 模拟CPU密集型计算
    const startTime = Date.now();
    while (Date.now() - startTime < duration) {
      // 执行一些计算密集型操作
      for (let i = 0; i < 1000 * intensity; i++) {
        Math.sqrt(Math.random() * 1000000);
      }
      
      // 避免阻塞主线程
      await new Promise(resolve => setTimeout(resolve, 10));
    }

    // 记录CPU压力结束
    Sentry.addBreadcrumb({
      category: 'chaos.cpu',
      message: 'CPU stress simulation completed',
      level: 'info',
      data: { actualDuration: Date.now() - startTime }
    });
  }

  // 模拟API失败
  private async simulateApiFailure(test: ChaosTestConfig): Promise<void> {
    const failureRate = test.intensity || 0.2;
    
    // 记录API失败开始
    Sentry.addBreadcrumb({
      category: 'chaos.api',
      message: 'API failure simulation started',
      level: 'info',
      data: { failureRate, duration: test.duration }
    });

    // 在实际应用中，这里可以拦截API调用并模拟失败
    // 目前只是记录和等待
    await new Promise(resolve => setTimeout(resolve, test.duration || 10000));

    // 随机触发一些错误来模拟API失败
    if (Math.random() < failureRate) {
      throw new Error('Simulated API failure during chaos testing');
    }

    // 记录API失败结束
    Sentry.addBreadcrumb({
      category: 'chaos.api',
      message: 'API failure simulation completed',
      level: 'info',
      data: { actualDuration: test.duration }
    });
  }

  // 模拟慢响应
  private async simulateSlowResponse(test: ChaosTestConfig): Promise<void> {
    const delay = (test.intensity || 0.4) * 5000; // 最大5秒延迟
    
    // 记录慢响应开始
    Sentry.addBreadcrumb({
      category: 'chaos.response',
      message: 'Slow response simulation started',
      level: 'info',
      data: { delay, duration: test.duration }
    });

    // 在实际应用中，这里可以延迟API响应
    // 目前只是记录和等待
    await new Promise(resolve => setTimeout(resolve, test.duration || 20000));

    // 记录慢响应结束
    Sentry.addBreadcrumb({
      category: 'chaos.response',
      message: 'Slow response simulation completed',
      level: 'info',
      data: { actualDuration: test.duration }
    });
  }

  // 模拟随机错误
  private async simulateRandomError(test: ChaosTestConfig): Promise<void> {
    const errorTypes = [
      'NetworkError',
      'TimeoutError', 
      'ValidationError',
      'PermissionError',
      'ResourceError'
    ];
    
    const randomError = errorTypes[Math.floor(Math.random() * errorTypes.length)];
    
    // 记录随机错误开始
    Sentry.addBreadcrumb({
      category: 'chaos.random',
      message: 'Random error simulation started',
      level: 'info',
      data: { errorType: randomError, duration: test.duration }
    });

    // 等待一段时间
    await new Promise(resolve => setTimeout(resolve, test.duration || 5000));

    // 随机决定是否抛出错误
    if (Math.random() < (test.intensity || 0.1)) {
      throw new Error(`Simulated ${randomError} during chaos testing`);
    }

    // 记录随机错误结束
    Sentry.addBreadcrumb({
      category: 'chaos.random',
      message: 'Random error simulation completed',
      level: 'info',
      data: { actualDuration: test.duration }
    });
  }

  // 计算测试影响
  private calculateImpact(test: ChaosTestConfig): 'low' | 'medium' | 'high' {
    const intensity = test.intensity || 0.5;
    const duration = (test.duration || 0) / 1000; // 转换为秒
    
    const impactScore = intensity * (duration / 60); // 强度 × 持续时间（分钟）
    
    if (impactScore < 0.1) return 'low';
    if (impactScore < 0.3) return 'medium';
    return 'high';
  }

  // 手动触发测试
  public async triggerTest(testId: string): Promise<ChaosTestResult> {
    const test = this.tests.find(t => t.id === testId);
    if (!test) {
      throw new Error(`Test not found: ${testId}`);
    }

    const startTime = Date.now();
    let success = false;
    let error: string | undefined;

    try {
      await this.performChaosTest(test);
      success = true;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
    }

    const result: ChaosTestResult = {
      testId: test.id,
      type: test.type,
      timestamp: startTime,
      duration: Date.now() - startTime,
      success,
      error,
      impact: this.calculateImpact(test)
    };

    this.testResults.push(result);
    return result;
  }

  // 获取测试结果
  public getTestResults(limit?: number): ChaosTestResult[] {
    const results = [...this.testResults].reverse();
    return limit ? results.slice(0, limit) : results;
  }

  // 获取测试统计
  public getTestStats() {
    const totalTests = this.testResults.length;
    const successfulTests = this.testResults.filter(r => r.success).length;
    const failedTests = totalTests - successfulTests;
    
    const testsByType = this.testResults.reduce((acc, result) => {
      acc[result.type] = (acc[result.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const testsByImpact = this.testResults.reduce((acc, result) => {
      acc[result.impact] = (acc[result.impact] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalTests,
      successfulTests,
      failedTests,
      successRate: totalTests > 0 ? (successfulTests / totalTests) * 100 : 0,
      testsByType,
      testsByImpact
    };
  }

  // 检查是否活跃
  public isTestingActive(): boolean {
    return this.isActive;
  }

  // 销毁管理器
  public destroy() {
    this.stopChaosTesting();
    this.tests = [];
    this.testResults = [];
  }
}

// 全局混沌测试管理器实例
let globalChaosManager: ChaosManager | null = null;

export function getChaosManager(): ChaosManager {
  if (!globalChaosManager) {
    globalChaosManager = new ChaosManager();
  }
  return globalChaosManager;
}

export function destroyChaosManager() {
  if (globalChaosManager) {
    globalChaosManager.destroy();
    globalChaosManager = null;
  }
}