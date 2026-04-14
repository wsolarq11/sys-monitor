// 调试脚本 - 模拟扫描过程并查看日志

async function debugScan() {
    console.log('=== 开始调试扫描功能 ===');
    
    // 测试数据库路径
    try {
        const dbPath = await window.__TAURI_INVOKE__('get_db_path');
        console.log('✅ 数据库路径获取成功:', dbPath);
    } catch (error) {
        console.error('❌ 数据库路径获取失败:', error);
        return;
    }
    
    // 测试一个简单的路径
    const testPath = 'C:\\Windows\\System32\\drivers\\etc'; // 一个较小的目录用于测试
    console.log('测试路径:', testPath);
    
    // 测试扫描功能
    try {
        console.log('🚀 开始扫描测试...');
        const result = await window.__TAURI_INVOKE__('scan_folder', {
            path: testPath,
            db_path: await window.__TAURI_INVOKE__('get_db_path')
        });
        console.log('✅ 扫描成功:', result);
    } catch (error) {
        console.error('❌ 扫描失败:', error);
        
        // 尝试获取更详细的错误信息
        console.log('错误类型:', typeof error);
        console.log('错误字符串:', String(error));
        console.log('错误详情:', error);
    }
    
    console.log('=== 调试完成 ===');
}

// 运行调试
debugScan();