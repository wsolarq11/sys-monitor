# Playwright 测试架构规范 - SysMonitor

## 定位器策略

**严格遵循优先级顺序**（从高到低）：
1. `getByRole()` - 首选，测试用户可见行为
2. `getByLabel()` - 表单元素
3. `getByPlaceholder()` - 输入框
4. `getByText()` - 文本内容
5. `getByTestId()` - 仅在以上都不可用时使用
6. `locator()` - 最后手段，避免使用

**核心原则**：
- 测试用户可见行为而非实现细节
- 删除 class 属性不应导致测试失败
- 避免使用 `data-testid` 除非必要
- 永不使用 XPath 或 CSS 选择器作为首选

## 架构模式

### POM 与 Fixtures 混合模式

**小型项目/简单场景**：使用 Fixtures 注入 Page 对象
```typescript
// tests/example.spec.ts
import { test, expect } from '@playwright/test';

test('example', async ({ page }) => {
  await page.goto('/');
  // 直接使用 page 对象
});
```

**大型项目/复杂场景**：使用懒加载 POM 保持类型推导
```typescript
// pages/DashboardPage.ts
export class DashboardPage {
  constructor(private page: Page) {}
  
  async goto() {
    return this.page.goto('/');
  }
  
  // 懒加载定位器
  getDashboardTitle() {
    return this.page.getByRole('heading', { name: /SysMonitor Dashboard/i });
  }
}
```

## 测试组织

### 目录结构（按业务领域）
```
tests/e2e/
├── pages/                    # POM 页面对象
│   ├── DashboardPage.ts
│   ├── FolderAnalysisPage.ts
│   └── SystemMonitorPage.ts
├── fixtures/                 # 自定义 Fixtures
│   └── test-fixtures.ts
├── tests/
│   ├── smoke/               # @smoke 标签 - 每次部署
│   │   └── critical-path.spec.ts
│   ├── critical/            # @critical 标签 - 每日 CI
│   │   └── core-features.spec.ts
│   └── regression/          # @regression 标签 - 分支合并
│       └── full-suite.spec.ts
├── utils/                    # 工具函数
│   ├── api-helpers.ts
│   └── test-data.ts
└── playwright.config.ts
```

### 分层执行策略

**@smoke 标签**：
- 执行频率：每次部署
- 覆盖率：核心路径验证
- 用例数：5-10 个
- 超时：30 秒

**@critical 标签**：
- 执行频率：每日 CI
- 覆盖率：关键功能
- 用例数：20-30 个
- 超时：60 秒

**@regression 标签**：
- 执行频率：分支合并
- 覆盖率：完整回归
- 用例数：总测试量的 30%
- 超时：120 秒

**E2E 测试比例控制**：
- 维持总测试量约 30%
- 70-80% 覆盖率后新增测试成本远超价值
- 优先保证核心路径稳定性

## API 与 UI 协同测试

### 测试分层
```typescript
// API 层 - 数据准备与精确验证
import { APIRequestContext } from '@playwright/test';

async function setupTestData(api: APIRequestContext) {
  await api.post('/api/folders', {
    data: { path: 'C:\\test', name: 'Test Folder' }
  });
}

// UI 层 - 最终展示验证
test('display folder data', async ({ page }) => {
  await page.goto('/folder-analysis');
  await expect(page.getByText('Test Folder')).toBeVisible();
});
```

### Mock 策略

**MSW（Mock Service Worker）** - 推荐：
- 在网络层拦截请求
- 让应用走真实 fetch 代码路径
- 支持复杂场景模拟

**HAR 录制回放**：
- 用于确定性场景
- 完整请求/响应记录
- 适合回归测试

**page.route()**：
- 用于简单 mock
- 灵活控制单个请求
- 适合错误处理测试

```typescript
// 简单 Mock
await page.route('**/api/metrics', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ cpu: 45.5, memory: 8589934592 })
  });
});

// 错误处理 Mock
await page.route('**/api/folders', route => {
  route.fulfill({
    status: 500,
    body: JSON.stringify({ error: 'Internal server error' })
  });
});
```

## 视觉回归测试

### 配置要求
```typescript
// 固定 viewport
await page.setViewportSize({ width: 1920, height: 1080 });

// Mask 动态区域
await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [page.locator('[data-dynamic]')],
  maskColor: '#00FF00'
});

// 全页截图
await expect(page).toHaveScreenshot('full-page.png', {
  fullPage: true
});
```

### Docker 容器一致性
```dockerfile
# 使用官方 Playwright 镜像
FROM mcr.microsoft.com/playwright:v1.40.0

# 固定分辨率
ENV PLAYWRIGHT_HEADLESS=true
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

## CI 配置

### webServer 自动启停
```typescript
// playwright.config.ts
webServer: {
  command: 'pnpm dev',
  url: 'http://localhost:1420',
  reuseExistingServer: !process.env.CI, // CI 环境全新启动
  timeout: 60000,
  stdout: 'pipe',
  stderr: 'pipe'
}
```

### Workers 优化
```typescript
// 本地开发：并行执行
workers: process.env.CI ? 1 : undefined,

// CI 环境：根据资源调整
workers: process.env.CI ? 2 : undefined,
```

### Sharding 横向扩展
```bash
# 单机资源饱和后启用
pnpm test -- --shard=1/4
pnpm test -- --shard=2/4
pnpm test -- --shard=3/4
pnpm test -- --shard=4/4
```

### Flaky 测试阻断
```typescript
// Playwright v1.52+
// CI 配置：--fail-on-flaky-tests
```

## 测试用例编写规范

### 基本结构
```typescript
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display dashboard title', async ({ page }) => {
    // ✅ 使用 getByRole
    await expect(page.getByRole('heading', { name: 'SysMonitor Dashboard' }))
      .toBeVisible();
  });

  test('should navigate to folder analysis', async ({ page }) => {
    // ✅ 使用 getByRole 导航
    await page.getByRole('link', { name: 'Folder Analysis' }).click();
    await expect(page).toHaveURL(/.*folder-analysis/);
  });
});
```

### 标签使用
```typescript
// Smoke 测试
test('should load dashboard @smoke', async ({ page }) => {
  // ...
});

// Critical 测试
test('should display real-time metrics @critical', async ({ page }) => {
  // ...
});

// Regression 测试
test('should handle all edge cases @regression', async ({ page }) => {
  // ...
});
```

### 断言最佳实践
```typescript
// ✅ 可见性断言
await expect(page.getByText('Success')).toBeVisible();

// ✅ 状态断言
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByRole('textbox')).toHaveValue('test');

// ✅ URL 断言
await expect(page).toHaveURL(/.*dashboard/);

// ❌ 避免硬编码等待
// await page.waitForTimeout(5000); // 不要这样做

// ✅ 使用条件等待
await page.waitForLoadState('networkidle');
await expect(page.getByText('Loaded')).toBeVisible();
```

## AI 自动化生态（2026）

### Planner - 探索应用生成计划
- 分析应用结构
- 识别可测试区域
- 生成测试计划

### Generator - 转换为可执行测试
- 基于计划生成测试代码
- 遵循定位器优先级
- 自动添加标签

### Healer - 自动修复失败测试
- 分析失败原因
- 定位器失效自动修复
- 更新测试用例

### MCP（Model Context Protocol）
- 基于可访问性树而非截图执行
- 理解语义结构
- 智能定位元素

## 错误处理

### 退出码规范
- `0`: 成功
- `32-63`: 环境问题
- `64-95`: 执行错误
- `96-127`: 数据错误
- `128+`: 信号中断

### 审计日志
```json
{
  "timestamp": "2026-04-14T10:00:00Z",
  "level": "INFO",
  "trace_id": "uuid-v4",
  "action": "test_start",
  "result": "success"
}
```

## 持续改进

### 定期审查
- 每月审查 flaky 测试
- 删除低价值测试（覆盖率<70%）
- 优化执行时间

### 指标监控
- 测试通过率 > 95%
- 执行时间 < 10 分钟（smoke）
- Flaky 测试率 < 1%

---

**版本**: 1.0.0  
**更新**: 2026-04-14  
**遵循**: Playwright 最佳实践 2026
