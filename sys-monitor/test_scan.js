// 简单的测试脚本来验证扫描功能
// 在浏览器控制台中运行此脚本

async function testScan() {
    console.log('开始测试扫描功能...');
    
    // 测试数据库路径获取
    try {
        const dbPath = await window.__TAURI_INVOKE__('get_db_path');
        console.log('数据库路径:', dbPath);
    } catch (error) {
        console.error('获取数据库路径失败:', error);
        return;
    }
    
    // 测试文件夹选择
    try {
        const folderPath = await window.__TAURI_INVOKE__('select_folder');
        console.log('选择的文件夹:', folderPath);
    } catch (error) {
        console.log('文件夹选择取消或失败:', error);
    }
    
    console.log('测试完成！');
}

// 运行测试
testScan();