# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: functional.spec.ts >> SysMonitor Functional Tests >> 边界条件测试
- Location: tests\functional.spec.ts:225:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/folder-analysis
Call log:
  - navigating to "http://localhost:1420/folder-analysis", waiting until "load"

```

# Test source

```ts
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
  220 |     // 最终状态检查
  221 |     const dashboardTitle = page.locator('h1');
  222 |     await expect(dashboardTitle).toBeVisible();
  223 |   });
  224 | 
  225 |   test('边界条件测试', async ({ page }) => {
> 226 |     await page.goto('http://localhost:1420/folder-analysis');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:1420/folder-analysis
  227 |     
  228 |     // 测试特殊字符路径
  229 |     const specialPaths = [
  230 |       'C:\\测试文件夹\\中文路径',
  231 |       'C:\\folder with spaces',
  232 |       'C:\\very-long-folder-name-that-exceeds-normal-limits'
  233 |     ];
  234 |     
  235 |     const pathInput = page.locator('input[placeholder*="文件夹路径"]');
  236 |     
  237 |     for (const path of specialPaths) {
  238 |       await pathInput.fill(path);
  239 |       await expect(pathInput).toHaveValue(path);
  240 |       await pathInput.clear();
  241 |     }
  242 |     
  243 |     // 测试空路径错误
  244 |     const scanButton = page.locator('button:has-text("扫描文件夹")');
  245 |     await scanButton.click();
  246 |     
  247 |     const errorMessage = page.locator('[class*="bg-red-50"]');
  248 |     await expect(errorMessage).toBeVisible({ timeout: 5000 });
  249 |   });
  250 | 
  251 |   test('性能测试', async ({ page }) => {
  252 |     await page.goto('http://localhost:1420');
  253 |     
  254 |     const startTime = Date.now();
  255 |     
  256 |     // 执行一系列操作
  257 |     for (let i = 0; i < 5; i++) {
  258 |       const dashboardLink = page.locator('a[href="/"]');
  259 |       const folderAnalysisLink = page.locator('a[href="/folder-analysis"]');
  260 |       
  261 |       await dashboardLink.click();
  262 |       await page.waitForTimeout(200);
  263 |       
  264 |       await folderAnalysisLink.click();
  265 |       await page.waitForTimeout(200);
  266 |     }
  267 |     
  268 |     const endTime = Date.now();
  269 |     const duration = endTime - startTime;
  270 |     
  271 |     // 性能要求：操作应在合理时间内完成
  272 |     expect(duration).toBeLessThan(10000); // 10秒内完成
  273 |     
  274 |     // 最终状态验证
  275 |     const dashboardTitle = page.locator('h1');
  276 |     await expect(dashboardTitle).toBeVisible();
  277 |   });
  278 | });
```