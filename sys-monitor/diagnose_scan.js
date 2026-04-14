// 详细诊断脚本 - 测试扫描功能的各个部分

async function diagnoseScan() {
    console.log('=== 开始详细诊断扫描功能 ===');
    
    // 1. 测试数据库路径获取
    console.log('\n1. 测试数据库路径获取...');
    try {
        const dbPath = await window.__TAURI_INVOKE__('get_db_path');
        console.log('✅ 数据库路径:', dbPath);
        
        // 检查数据库文件是否存在
        const fs = await import('@tauri-apps/api/fs');
        const exists = await fs.exists(dbPath);
        console.log('📁 数据库文件存在:', exists);
        
        if (!exists) {
            console.log('⚠️ 数据库文件不存在，将自动创建');
        }
    } catch (error) {
        console.error('❌ 数据库路径获取失败:', error);
        return;
    }
    
    // 2. 测试文件夹选择功能
    console.log('\n2. 测试文件夹选择功能...');
    try {
        const folderPath = await window.__TAURI_INVOKE__('select_folder');
        console.log('✅ 文件夹选择成功:', folderPath);
        
        // 检查文件夹是否存在
        const fs = await import('@tauri-apps/api/fs');
        const exists = await fs.exists(folderPath);
        console.log('📁 文件夹存在:', exists);
        
        if (exists) {
            const isDir = await fs.isDir(folderPath);
            console.log('📂 是文件夹:', isDir);
        }
        
        return folderPath;
    } catch (error) {
        console.log('ℹ️ 文件夹选择取消或失败:', error);
        
        // 使用一个测试路径
        const testPath = 'C:\\Windows\\System32\\drivers\\etc';
        console.log('📁 使用测试路径:', testPath);
        return testPath;
    }
}

async function testScanWithPath(path) {
    console.log('\n3. 测试扫描功能...');
    console.log('📁 扫描路径:', path);
    
    try {
        const dbPath = await window.__TAURI_INVOKE__('get_db_path');
        console.log('🚀 开始扫描...');
        
        // 调用扫描命令
        const result = await window.__TAURI_INVOKE__('scan_folder', {
            path: path,
            db_path: dbPath
        });
        
        console.log('✅ 扫描成功完成');
        console.log('📊 扫描结果:', result);
        
        // 测试获取扫描历史
        console.log('\n4. 测试扫描历史获取...');
        const scans = await window.__TAURI_INVOKE__('get_folder_scans', {
            path: path,
            limit: 5,
            db_path: dbPath
        });
        
        console.log('📋 扫描历史:', scans);
        
    } catch (error) {
        console.error('❌ 扫描失败:', error);
        console.error('🔍 错误详情:');
        console.error('错误类型:', typeof error);
        console.error('错误消息:', error.message || '无消息');
        console.error('错误字符串:', String(error));
        console.error('完整错误对象:', error);
    }
}

// 运行诊断
async function runDiagnosis() {
    const path = await diagnoseScan();
    if (path) {
        await testScanWithPath(path);
    }
    console.log('\n=== 诊断完成 ===');
}

// 运行诊断
runDiagnosis();