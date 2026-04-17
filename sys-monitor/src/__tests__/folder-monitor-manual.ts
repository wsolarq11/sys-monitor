/**
 * 文件夹监控功能测试脚本
 * 
 * 用于验证修复后的 API 层是否正常工作
 * 在浏览器控制台或测试环境中运行
 */

import {
  getDbPath,
  selectFolder,
  scanFolder,
  getFolderScans,
  addWatchedFolder,
  listWatchedFolders,
  removeWatchedFolder,
  toggleWatchedFolderActive,
} from '../services/folderAnalysisApi';

// ==================== 测试工具函数 ====================

class TestRunner {
  private passed = 0;
  private failed = 0;
  private tests: Array<{ name: string; fn: () => Promise<void> }> = [];

  test(name: string, fn: () => Promise<void>) {
    this.tests.push({ name, fn });
  }

  async run() {
    console.log('🧪 开始运行文件夹监控功能测试...\n');
    
    for (const { name, fn } of this.tests) {
      try {
        await fn();
        this.passed++;
        console.log(`✅ PASS: ${name}`);
      } catch (error) {
        this.failed++;
        console.error(`❌ FAIL: ${name}`);
        console.error(`   Error: ${error}`);
      }
    }

    console.log('\n' + '='.repeat(50));
    console.log(`测试结果: ${this.passed} 通过, ${this.failed} 失败`);
    console.log('='.repeat(50));
    
    return this.failed === 0;
  }
}

// ==================== 测试用例 ====================

const runner = new TestRunner();

// 测试 1: 获取数据库路径
runner.test('获取数据库路径', async () => {
  const dbPath = await getDbPath();
  if (!dbPath || typeof dbPath !== 'string') {
    throw new Error('数据库路径无效');
  }
  console.log('   数据库路径:', dbPath);
});

// 测试 2: 选择文件夹（需要用户交互）
runner.test('选择文件夹', async () => {
  const path = await selectFolder();
  if (path === null) {
    console.warn('   ⚠️ 用户取消了选择');
    return; // 跳过后续依赖此路径的测试
  }
  if (!path || typeof path !== 'string') {
    throw new Error('选择的文件夹路径无效');
  }
  console.log('   选择的文件夹:', path);
  
  // 保存路径供后续测试使用
  (window as any).__testFolderPath = path;
});

// 测试 3: 扫描文件夹
runner.test('扫描文件夹', async () => {
  const path = (window as any).__testFolderPath;
  if (!path) {
    console.warn('   ⚠️ 跳过：未选择文件夹');
    return;
  }
  
  const dbPath = await getDbPath();
  const result = await scanFolder(path, dbPath);
  
  if (!result || typeof result.total_size !== 'number') {
    throw new Error('扫描结果格式错误');
  }
  
  console.log('   扫描结果:', {
    total_size: result.total_size,
    file_count: result.file_count,
    folder_count: result.folder_count,
    scan_duration_ms: result.scan_duration_ms,
  });
});

// 测试 4: 获取扫描历史
runner.test('获取扫描历史', async () => {
  const path = (window as any).__testFolderPath;
  if (!path) {
    console.warn('   ⚠️ 跳过：未选择文件夹');
    return;
  }
  
  const dbPath = await getDbPath();
  const scans = await getFolderScans(path, dbPath, 10);
  
  // ✅ 关键测试：验证返回的是数组，不是包装对象
  if (!Array.isArray(scans)) {
    throw new Error(`期望返回数组，实际得到: ${typeof scans}`);
  }
  
  console.log('   扫描历史记录数量:', scans.length);
  if (scans.length > 0) {
    console.log('   最新记录:', {
      id: scans[0].id,
      path: scans[0].path,
      timestamp: new Date(scans[0].scan_timestamp).toLocaleString(),
    });
  }
});

// 测试 5: 添加监控文件夹
runner.test('添加监控文件夹', async () => {
  const path = (window as any).__testFolderPath;
  if (!path) {
    console.warn('   ⚠️ 跳过：未选择文件夹');
    return;
  }
  
  const dbPath = await getDbPath();
  const folderId = await addWatchedFolder(path, dbPath, '测试文件夹');
  
  // ✅ 关键测试：验证返回的是 number (folder_id)
  if (typeof folderId !== 'number' || folderId <= 0) {
    throw new Error(`期望返回有效的 folder_id (number)，实际得到: ${folderId}`);
  }
  
  console.log('   创建的文件夹 ID:', folderId);
  (window as any).__testFolderId = folderId;
});

// 测试 6: 列出监控文件夹
runner.test('列出监控文件夹', async () => {
  const dbPath = await getDbPath();
  const folders = await listWatchedFolders(dbPath);
  
  if (!Array.isArray(folders)) {
    throw new Error(`期望返回数组，实际得到: ${typeof folders}`);
  }
  
  console.log('   监控文件夹数量:', folders.length);
  if (folders.length > 0) {
    const testFolder = folders.find(f => f.alias === '测试文件夹');
    if (testFolder) {
      console.log('   找到测试文件夹:', {
        id: testFolder.id,
        path: testFolder.path,
        is_active: testFolder.is_active,
      });
    }
  }
});

// 测试 7: 切换监控状态
runner.test('切换监控状态', async () => {
  const folderId = (window as any).__testFolderId;
  if (!folderId) {
    console.warn('   ⚠️ 跳过：未创建测试文件夹');
    return;
  }
  
  const dbPath = await getDbPath();
  
  // 切换到 inactive
  const result1 = await toggleWatchedFolderActive(folderId, false, dbPath);
  if (typeof result1 !== 'boolean') {
    throw new Error(`期望返回 boolean，实际得到: ${typeof result1}`);
  }
  console.log('   切换到 inactive:', result1);
  
  // 切换回 active
  const result2 = await toggleWatchedFolderActive(folderId, true, dbPath);
  console.log('   切换到 active:', result2);
});

// 测试 8: 移除监控文件夹
runner.test('移除监控文件夹', async () => {
  const folderId = (window as any).__testFolderId;
  if (!folderId) {
    console.warn('   ⚠️ 跳过：未创建测试文件夹');
    return;
  }
  
  const dbPath = await getDbPath();
  await removeWatchedFolder(folderId, dbPath);
  
  // 验证已删除
  const folders = await listWatchedFolders(dbPath);
  const stillExists = folders.some(f => f.id === folderId);
  
  if (stillExists) {
    throw new Error('文件夹未被成功删除');
  }
  
  console.log('   文件夹已成功删除');
});

// 测试 9: 参数命名验证（内部测试）
runner.test('验证参数命名一致性', async () => {
  // 这个测试验证类型定义是否正确
  // 如果编译通过，说明参数命名一致
  
  const dbPath = await getDbPath();
  
  // 这些调用应该能正常编译和运行
  // ✅ 修复: listWatchedFolders 接受 string 参数，不是对象
  await listWatchedFolders(dbPath);
  
  console.log('   ✅ 参数命名验证通过');
});

// ==================== 运行测试 ====================

// 在开发环境中，可以通过以下方式运行测试：
// 1. 在浏览器控制台导入此文件
// 2. 调用 runner.run()

if (typeof window !== 'undefined') {
  (window as any).runFolderMonitorTests = () => runner.run();
  console.log('📝 测试已准备就绪，在控制台运行: runFolderMonitorTests()');
}

export default runner;
