// 简单测试脚本 - 验证构建监控功能
const { GitHubBuildMonitor } = require('./src/services/githubBuildMonitor.ts');

async function simpleTest() {
  console.log('测试GitHub构建监控功能...');
  
  // 使用示例配置（实际使用时需要从.env文件读取）
  const monitor = new GitHubBuildMonitor(
    'your-username',  // 替换为实际的GitHub用户名
    'FolderSizeMonitor',
    undefined  // 没有token时使用匿名访问
  );

  try {
    console.log('获取最近的工作流运行...');
    const runs = await monitor.getRecentWorkflowRuns(3);
    console.log(`成功获取 ${runs.length} 个运行记录`);
    
    if (runs.length > 0) {
      console.log('最新运行信息:');
      console.log('- 名称:', runs[0].name);
      console.log('- 状态:', runs[0].status);
      console.log('- 分支:', runs[0].branch);
    }
  } catch (error) {
    console.error('测试失败:', error.message);
  }
}

simpleTest();