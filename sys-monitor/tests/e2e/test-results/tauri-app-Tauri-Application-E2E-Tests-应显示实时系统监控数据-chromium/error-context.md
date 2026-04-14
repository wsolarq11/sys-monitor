# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tauri-app.spec.ts >> Tauri Application E2E Tests >> 应显示实时系统监控数据
- Location: tests\tauri-app.spec.ts:105:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=%').first()
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=%').first()

```

# Test source

```ts
  13  | 
  14  |   test.beforeAll(async () => {
  15  |     console.log('启动 Tauri 应用程序...');
  16  |     
  17  |     // 启动应用程序
  18  |     appProcess = spawn(APP_PATH, [], {
  19  |       stdio: 'pipe',
  20  |       detached: false
  21  |     });
  22  | 
  23  |     // 等待应用程序启动
  24  |     await new Promise(resolve => setTimeout(resolve, 5000));
  25  |   });
  26  | 
  27  |   test.afterAll(async () => {
  28  |     console.log('关闭 Tauri 应用程序...');
  29  |     
  30  |     if (appProcess) {
  31  |       appProcess.kill();
  32  |       await new Promise(resolve => setTimeout(resolve, 2000));
  33  |     }
  34  |   });
  35  | 
  36  |   test('应用程序应成功启动', async ({ page }) => {
  37  |     test.setTimeout(TEST_TIMEOUT);
  38  |     
  39  |     // 等待应用程序窗口出现
  40  |     await page.waitForTimeout(3000);
  41  |     
  42  |     // 检查应用程序标题
  43  |     const title = await page.title();
  44  |     expect(title).toContain('SysMonitor');
  45  |   });
  46  | 
  47  |   test('应显示仪表板页面', async ({ page }) => {
  48  |     test.setTimeout(TEST_TIMEOUT);
  49  |     
  50  |     // 等待页面加载
  51  |     await page.waitForTimeout(2000);
  52  |     
  53  |     // 检查仪表板标题
  54  |     const dashboardTitle = page.locator('h1');
  55  |     await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  56  |     
  57  |     // 检查导航菜单
  58  |     const navLinks = page.locator('nav a');
  59  |     await expect(navLinks).toHaveCount(2);
  60  |     
  61  |     // 检查系统监控组件
  62  |     const cpuMonitor = page.locator('text=CPU Usage');
  63  |     await expect(cpuMonitor).toBeVisible();
  64  |     
  65  |     const memoryMonitor = page.locator('text=Memory Usage');
  66  |     await expect(memoryMonitor).toBeVisible();
  67  |   });
  68  | 
  69  |   test('应能导航到文件夹分析页面', async ({ page }) => {
  70  |     test.setTimeout(TEST_TIMEOUT);
  71  |     
  72  |     // 点击文件夹分析链接
  73  |     const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  74  |     await folderAnalysisLink.click();
  75  |     
  76  |     // 等待页面切换
  77  |     await page.waitForTimeout(2000);
  78  |     
  79  |     // 检查文件夹分析页面元素
  80  |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  81  |     await expect(pathInput).toBeVisible();
  82  |     
  83  |     const browseButton = page.locator('button:has-text("浏览...")');
  84  |     await expect(browseButton).toBeVisible();
  85  |     
  86  |     const scanButton = page.locator('button:has-text("扫描文件夹")');
  87  |     await expect(scanButton).toBeVisible();
  88  |   });
  89  | 
  90  |   test('应能返回仪表板页面', async ({ page }) => {
  91  |     test.setTimeout(TEST_TIMEOUT);
  92  |     
  93  |     // 点击仪表板链接
  94  |     const dashboardLink = page.locator('a[href="/"]');
  95  |     await dashboardLink.click();
  96  |     
  97  |     // 等待页面切换
  98  |     await page.waitForTimeout(2000);
  99  |     
  100 |     // 检查仪表板页面
  101 |     const dashboardTitle = page.locator('h1');
  102 |     await expect(dashboardTitle).toContainText('SysMonitor Dashboard');
  103 |   });
  104 | 
  105 |   test('应显示实时系统监控数据', async ({ page }) => {
  106 |     test.setTimeout(TEST_TIMEOUT);
  107 |     
  108 |     // 等待数据加载
  109 |     await page.waitForTimeout(3000);
  110 |     
  111 |     // 检查CPU使用率
  112 |     const cpuValue = page.locator('text=%').first();
> 113 |     await expect(cpuValue).toBeVisible();
      |                            ^ Error: expect(locator).toBeVisible() failed
  114 |     
  115 |     const cpuText = await cpuValue.textContent();
  116 |     expect(cpuText).toMatch(/\d+\.\d+%/);
  117 |     
  118 |     // 检查内存使用率
  119 |     const memoryValue = page.locator('text=GB').first();
  120 |     await expect(memoryValue).toBeVisible();
  121 |     
  122 |     const memoryText = await memoryValue.textContent();
  123 |     expect(memoryText).toMatch(/\d+\.\d+\s*GB/);
  124 |   });
  125 | 
  126 |   test('应处理文件夹路径输入', async ({ page }) => {
  127 |     test.setTimeout(TEST_TIMEOUT);
  128 |     
  129 |     // 导航到文件夹分析页面
  130 |     const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  131 |     await folderAnalysisLink.click();
  132 |     await page.waitForTimeout(2000);
  133 |     
  134 |     // 测试路径输入
  135 |     const testPath = 'C:\\test-folder';
  136 |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  137 |     
  138 |     await pathInput.fill(testPath);
  139 |     await expect(pathInput).toHaveValue(testPath);
  140 |     
  141 |     // 清除输入
  142 |     await pathInput.clear();
  143 |     await expect(pathInput).toHaveValue('');
  144 |   });
  145 | 
  146 |   test('应显示错误消息', async ({ page }) => {
  147 |     test.setTimeout(TEST_TIMEOUT);
  148 |     
  149 |     // 导航到文件夹分析页面
  150 |     const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  151 |     await folderAnalysisLink.click();
  152 |     await page.waitForTimeout(2000);
  153 |     
  154 |     // 尝试扫描空路径
  155 |     const scanButton = page.locator('button:has-text("扫描文件夹")');
  156 |     await scanButton.click();
  157 |     
  158 |     // 检查错误消息
  159 |     const errorMessage = page.locator('[class*="bg-red-50"]');
  160 |     await expect(errorMessage).toBeVisible({ timeout: 5000 });
  161 |   });
  162 | 
  163 |   test('应用程序应响应窗口调整', async ({ page }) => {
  164 |     test.setTimeout(TEST_TIMEOUT);
  165 |     
  166 |     // 设置小窗口尺寸
  167 |     await page.setViewportSize({ width: 800, height: 600 });
  168 |     await page.waitForTimeout(1000);
  169 |     
  170 |     // 检查布局适应性
  171 |     const dashboardTitle = page.locator('h1');
  172 |     await expect(dashboardTitle).toBeVisible();
  173 |     
  174 |     // 恢复默认尺寸
  175 |     await page.setViewportSize({ width: 1200, height: 800 });
  176 |     await page.waitForTimeout(1000);
  177 |     
  178 |     await expect(dashboardTitle).toBeVisible();
  179 |   });
  180 | 
  181 |   test('应保持应用程序稳定性', async ({ page }) => {
  182 |     test.setTimeout(TEST_TIMEOUT * 2);
  183 |     
  184 |     // 长时间运行测试
  185 |     for (let i = 0; i < 5; i++) {
  186 |       // 在页面间切换
  187 |       const dashboardLink = page.locator('a[href="/"]');
  188 |       const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  189 |       
  190 |       await dashboardLink.click();
  191 |       await page.waitForTimeout(1000);
  192 |       
  193 |       await folderAnalysisLink.click();
  194 |       await page.waitForTimeout(1000);
  195 |     }
  196 |     
  197 |     // 最终检查应用程序状态
  198 |     const dashboardTitle = page.locator('h1');
  199 |     await expect(dashboardTitle).toBeVisible();
  200 |   });
  201 | });
```