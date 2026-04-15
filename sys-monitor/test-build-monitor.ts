/**
 * 远程构建状态监控测试脚本
 * 用于验证GitHub Actions构建状态监控功能
 */

import { GitHubBuildMonitor, WorkflowRun } from './src/services/githubBuildMonitor';

async function testBuildMonitor() {
  console.log('🔍 开始测试远程构建状态监控功能...\n');

  // 从环境变量获取配置
  const owner = process.env.VITE_GITHUB_OWNER || 'your-username';
  const repo = process.env.VITE_GITHUB_REPO || 'FolderSizeMonitor';
  const token = process.env.VITE_GITHUB_TOKEN;

  console.log(`📋 配置信息:`);
  console.log(`   仓库: ${owner}/${repo}`);
  console.log(`   Token: ${token ? '已设置' : '未设置 (使用匿名访问)'}`);
  console.log();

  try {
    // 创建监控器实例
    const monitor = new GitHubBuildMonitor(owner, repo, token);

    // 测试1: 获取最近的工作流运行
    console.log('🔄 测试1: 获取最近的工作流运行...');
    const recentRuns = await monitor.getRecentWorkflowRuns(5);
    console.log(`   ✅ 成功获取 ${recentRuns.length} 个运行记录`);
    
    if (recentRuns.length > 0) {
      const latestRun = recentRuns[0];
      console.log(`   📊 最新运行:`);
      console.log(`      - 名称: ${latestRun.name}`);
      console.log(`      - 状态: ${latestRun.status}`);
      console.log(`      - 结论: ${latestRun.conclusion || '进行中'}`);
      console.log(`      - 分支: ${latestRun.branch}`);
      console.log(`      - 运行号: #${latestRun.run_number}`);
      console.log(`      - 持续时间: ${latestRun.duration_ms ? GitHubBuildMonitor.formatDuration(latestRun.duration_ms) : '进行中'}`);
      console.log(`      - 更新时间: ${new Date(latestRun.updated_at).toLocaleString('zh-CN')}`);
    }
    console.log();

    // 测试2: 获取构建状态摘要
    console.log('📈 测试2: 获取构建状态摘要...');
    const summary = await monitor.getBuildStatusSummary();
    console.log(`   ✅ 成功获取构建摘要`);
    console.log(`   📊 统计信息:`);
    console.log(`      - 总运行数: ${summary.totalRuns}`);
    console.log(`      - 成功率: ${summary.successRate.toFixed(1)}%`);
    console.log(`      - 平均时长: ${GitHubBuildMonitor.formatDuration(summary.averageDuration)}`);
    console.log(`      - 正在运行: ${summary.currentStatus.length} 个`);
    console.log(`      - 最后更新: ${new Date(summary.lastBuildTime).toLocaleString('zh-CN')}`);
    console.log();

    // 测试3: 获取特定工作流的运行
    console.log('🎯 测试3: 获取CI/CD工作流运行...');
    const ciRuns = await monitor.getWorkflowRunsByName('CI/CD Multi-Platform Tests', 3);
    console.log(`   ✅ 成功获取 ${ciRuns.length} 个CI/CD运行记录`);
    
    ciRuns.forEach((run: WorkflowRun, index: number) => {
      console.log(`   ${index + 1}. #${run.run_number} - ${GitHubBuildMonitor.getStatusText(run.status, run.conclusion)} (${run.branch})`);
    });
    console.log();

    // 测试4: 工具方法测试
    console.log('🛠️ 测试4: 工具方法测试...');
    console.log(`   - 格式化时长: ${GitHubBuildMonitor.formatDuration(3661000)} (期望: 1h 1m 1s)`);
    console.log(`   - 成功状态文本: ${GitHubBuildMonitor.getStatusText('completed', 'success')}`);
    console.log(`   - 失败状态颜色: ${GitHubBuildMonitor.getStatusColor('completed', 'failure')}`);
    console.log();

    console.log('🎉 所有测试完成！构建状态监控功能正常工作。');
    console.log('\n💡 提示: 在应用中查看实时构建状态，请访问 http://localhost:1420');

  } catch (error) {
    console.error('❌ 测试失败:', error instanceof Error ? error.message : error);
    console.log('\n🔧 可能的解决方案:');
    console.log('   1. 检查网络连接');
    console.log('   2. 验证GitHub Token权限 (需要 repo 和 workflow 权限)');
    console.log('   3. 确认仓库名称和用户名正确');
    console.log('   4. 检查API速率限制');
  }
}

// 运行测试
if (import.meta.url === `file://${process.argv[1]}`) {
  testBuildMonitor();
}

export { testBuildMonitor };