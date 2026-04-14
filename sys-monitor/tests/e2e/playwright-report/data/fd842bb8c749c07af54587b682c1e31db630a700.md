# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: functional.spec.ts >> SysMonitor Functional Tests >> 响应式设计测试
- Location: tests\functional.spec.ts:118:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/
Call log:
  - navigating to "http://localhost:1420/", waiting until "load"

```

# Test source

```ts
  19  |     const navLinks = page.locator('nav a');
  20  |     await expect(navLinks).toHaveCount(2);
  21  |     
  22  |     // 检查仪表板组件
  23  |     const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
  24  |     await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  25  |     
  26  |     // 检查系统监控组件
  27  |     const cpuMonitor = page.locator('text=CPU Usage');
  28  |     await expect(cpuMonitor).toBeVisible();
  29  |     
  30  |     const memoryMonitor = page.locator('text=Memory Usage');
  31  |     await expect(memoryMonitor).toBeVisible();
  32  |   });
  33  | 
  34  |   test('导航功能测试', async ({ page }) => {
  35  |     await page.goto('http://localhost:1420');
  36  |     
  37  |     // 等待React应用加载
  38  |     await page.waitForTimeout(3000);
  39  |     
  40  |     // 测试导航到文件夹分析页面
  41  |     const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  42  |     await folderAnalysisLink.click();
  43  |     
  44  |     // 等待页面切换
  45  |     await page.waitForTimeout(2000);
  46  |     
  47  |     // 检查文件夹分析页面
  48  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  49  |     await expect(pathInput).toBeVisible();
  50  |     
  51  |     // 测试返回仪表板
  52  |     const dashboardLink = page.locator('a[href="/"]');
  53  |     await dashboardLink.click();
  54  |     
  55  |     // 等待页面切换
  56  |     await page.waitForTimeout(2000);
  57  |     
  58  |     const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
  59  |     await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  60  |   });
  61  | 
  62  |   test('文件夹分析功能测试', async ({ page }) => {
  63  |     await page.goto('http://localhost:1420/folder-analysis');
  64  |     
  65  |     // 测试路径输入
  66  |     const testPath = 'C:\\test-folder';
  67  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  68  |     
  69  |     await pathInput.fill(testPath);
  70  |     await expect(pathInput).toHaveValue(testPath);
  71  |     
  72  |     // 测试清除输入
  73  |     await pathInput.clear();
  74  |     await expect(pathInput).toHaveValue('');
  75  |     
  76  |     // 测试错误处理
  77  |     const scanButton = page.locator('button:has-text("扫描文件夹")');
  78  |     await scanButton.click();
  79  |     
  80  |     // 检查错误消息
  81  |     const errorMessage = page.locator('[class*="bg-red-50"]');
  82  |     await expect(errorMessage).toBeVisible({ timeout: 5000 });
  83  |   });
  84  | 
  85  |   test('系统监控数据测试', async ({ page }) => {
  86  |     await page.goto('http://localhost:1420');
  87  |     
  88  |     // 等待React应用加载
  89  |     await page.waitForTimeout(3000);
  90  |     
  91  |     // 模拟系统监控数据
  92  |     await page.route('**/invoke/get_system_metrics', route => {
  93  |       route.fulfill({
  94  |         status: 200,
  95  |         contentType: 'application/json',
  96  |         body: JSON.stringify({
  97  |           cpu_usage: 45.5,
  98  |           memory_usage: 8589934592, // 8GB
  99  |           memory_total: 17179869184, // 16GB
  100 |           disk_usage: 65.2,
  101 |           disk_total: 1099511627776 // 1TB
  102 |         })
  103 |       });
  104 |     });
  105 |     
  106 |     // 等待数据加载
  107 |     await page.waitForTimeout(3000);
  108 |     
  109 |     // 检查CPU使用率显示
  110 |     const cpuValue = page.locator('text=%').first();
  111 |     await expect(cpuValue).toBeVisible();
  112 |     
  113 |     // 检查内存使用率显示
  114 |     const memoryValue = page.locator('text=GB').first();
  115 |     await expect(memoryValue).toBeVisible();
  116 |   });
  117 | 
  118 |   test('响应式设计测试', async ({ page }) => {
> 119 |     await page.goto('http://localhost:1420');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/
  120 |     
  121 |     // 等待React应用加载
  122 |     await page.waitForTimeout(3000);
  123 |     
  124 |     // 测试不同屏幕尺寸
  125 |     await page.setViewportSize({ width: 375, height: 667 }); // 移动端
  126 |     await page.waitForTimeout(1000);
  127 |     
  128 |     const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
  129 |     await expect(dashboardTitle).toBeVisible();
  130 |     
  131 |     await page.setViewportSize({ width: 1920, height: 1080 }); // 桌面端
  132 |     await page.waitForTimeout(1000);
  133 |     
  134 |     await expect(dashboardTitle).toBeVisible();
  135 |   });
  136 | 
  137 |   test('API错误处理测试', async ({ page }) => {
  138 |     await page.goto('http://localhost:1420');
  139 |     
  140 |     // 等待React应用加载
  141 |     await page.waitForTimeout(3000);
  142 |     
  143 |     // 模拟API错误
  144 |     await page.route('**/invoke/get_system_metrics', route => {
  145 |       route.fulfill({
  146 |         status: 500,
  147 |         contentType: 'application/json',
  148 |         body: JSON.stringify({ error: 'Internal server error' })
  149 |       });
  150 |     });
  151 |     
  152 |     // 等待错误处理
  153 |     await page.waitForTimeout(3000);
  154 |     
  155 |     // 检查应用程序是否仍然正常运行
  156 |     const dashboardTitle = page.locator('h1').nth(1); // 第二个h1元素
  157 |     await expect(dashboardTitle).toBeVisible();
  158 |   });
  159 | 
  160 |   test('文件夹扫描功能模拟测试', async ({ page }) => {
  161 |     await page.goto('http://localhost:1420/folder-analysis');
  162 |     
  163 |     // 等待React应用加载
  164 |     await page.waitForTimeout(3000);
  165 |     
  166 |     // 测试基本的UI交互，不模拟具体的Tauri API调用
  167 |     // 因为Tauri API调用需要实际的桌面应用程序环境
  168 |     
  169 |     // 验证页面基本元素
  170 |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  171 |     await expect(pathInput).toBeVisible();
  172 |     
  173 |     const browseButton = page.locator('button:has-text("浏览")');
  174 |     await expect(browseButton).toBeVisible();
  175 |     
  176 |     const scanButton = page.locator('button:has-text("扫描文件夹")');
  177 |     await expect(scanButton).toBeVisible();
  178 |     
  179 |     // 测试输入框交互
  180 |     const testPath = 'C:\\test-folder';
  181 |     await pathInput.fill(testPath);
  182 |     await expect(pathInput).toHaveValue(testPath);
  183 |     
  184 |     // 测试按钮点击（不期望实际扫描成功，因为需要Tauri环境）
  185 |     await scanButton.click();
  186 |     
  187 |     // 等待可能的UI状态变化
  188 |     await page.waitForTimeout(2000);
  189 |     
  190 |     // 验证应用程序没有崩溃，仍然可以正常交互
  191 |     await expect(pathInput).toBeVisible();
  192 |     await expect(scanButton).toBeVisible();
  193 |     
  194 |     // 测试导航回仪表板
  195 |     const dashboardLink = page.locator('a[href="/"]');
  196 |     await dashboardLink.click();
  197 |     await page.waitForTimeout(2000);
  198 |     
  199 |     // 验证成功导航到仪表板
  200 |     const dashboardTitle = page.locator('h1').nth(1);
  201 |     await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  202 |   });
  203 | 
  204 |   test('长时间运行稳定性测试', async ({ page }) => {
  205 |     await page.goto('http://localhost:1420');
  206 |     
  207 |     // 模拟长时间运行
  208 |     for (let i = 0; i < 10; i++) {
  209 |       // 切换页面
  210 |       const dashboardLink = page.locator('a[href="/"]');
  211 |       const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  212 |       
  213 |       await dashboardLink.click();
  214 |       await page.waitForTimeout(500);
  215 |       
  216 |       await folderAnalysisLink.click();
  217 |       await page.waitForTimeout(500);
  218 |     }
  219 |     
```