# SysMonitor Playwright E2E 测试

基于 Playwright 2026 最佳实践的端到端测试框架。

## 快速开始

### 安装依赖

```bash
pnpm install
pnpm exec playwright install --with-deps
```

### 运行测试

```bash
# 运行所有测试
pnpm test

# 运行 Smoke 测试（每次部署）
pnpm test:smoke

# 运行 Critical 测试（每日 CI）
pnpm test:critical

# 运行 Regression 测试（分支合并）
pnpm test:regression

# 运行视觉回归测试
pnpm test:visual

# 有头模式运行
pnpm test:headed

# 调试模式
pnpm test:debug
```

## 测试分层

### @smoke - 部署验证
- **执行频率**: 每次部署
- **用例数**: 5-10 个
- **超时**: 30 秒
- **位置**: `tests/smoke/`

### @critical - 核心功能
- **执行频率**: 每日 CI
- **用例数**: 20-30 个
- **超时**: 60 秒
- **位置**: `tests/critical/`

### @regression - 完整回归
- **执行频率**: 分支合并
- **用例数**: 总测试量 30%
- **超时**: 120 秒
- **位置**: `tests/regression/`

## 目录结构

```
tests/e2e/
├── pages/                    # POM 页面对象
│   ├── DashboardPage.ts
│   ├── FolderAnalysisPage.ts
│   ├── BasePage.ts
│   └── index.ts
├── fixtures/                 # 自定义 Fixtures
│   └── test-fixtures.ts
├── utils/                    # 工具函数
│   └── api-helpers.ts
├── tests/
│   ├── smoke/               # Smoke 测试
│   ├── critical/            # Critical 测试
│   └── regression/          # Regression 测试
├── playwright.config.ts      # 配置文件
├── agents.md                 # AI 规范文档
└── run-tests.ps1             # PowerShell 运行脚本
```

## 定位器策略

**严格遵循优先级**（从高到低）：

1. `getByRole()` - 首选
2. `getByLabel()` - 表单元素
3. `getByPlaceholder()` - 输入框
4. `getByText()` - 文本内容
5. `getByTestId()` - 仅在必要时
6. `locator()` - 最后手段

**示例**：

```typescript
// ✅ 推荐
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByPlaceholder('Enter email').fill('test@example.com');

// ❌ 避免
await page.locator('.btn-submit').click();
await page.locator('input[type="text"]').fill('test');
```

## 架构模式

### POM + Fixtures 混合模式

```typescript
import { test, expect } from '../fixtures/test-fixtures';

test('example', async ({ dashboardPage }) => {
  await expect(dashboardPage.cpuMonitor).toBeVisible();
});
```

## CI/CD

### GitHub Actions

```yaml
- name: Run smoke tests
  run: pnpm exec playwright test --project=smoke --grep=@smoke
```

### Docker（视觉回归测试）

```bash
# 运行视觉回归测试（保证跨环境一致性）
pnpm docker:visual

# 或手动运行
docker-compose run playwright-visual
```

## Workers 优化

```bash
# 本地开发 - 并行执行
pnpm test:workers

# CI 环境 - Sharding 横向扩展
pnpm test:shard
```

## 视觉回归测试

```typescript
import { test, expect } from '../fixtures/test-fixtures';

test('dashboard baseline', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('/');
  
  await expect(page).toHaveScreenshot('dashboard-baseline.png', {
    mask: [page.locator('[data-dynamic]')]
  });
});
```

## API 与 UI 协同

```typescript
test('api + ui coordination', async ({ page }) => {
  // API 层 - 数据准备
  await page.route('**/api/metrics', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({ cpu: 45.5 })
    });
  });
  
  // UI 层 - 展示验证
  await page.goto('/');
  await expect(page.getByText('45.5%')).toBeVisible();
});
```

## 运行脚本

### PowerShell

```powershell
# 运行 Smoke 测试
.\run-tests.ps1 -TestType smoke

# 有头模式运行 Critical 测试
.\run-tests.ps1 -TestType critical -headed

# 调试模式
.\run-tests.ps1 -TestType regression -Debug
```

## 退出码

- `0`: 成功
- `32-63`: 环境问题
- `64-95`: 执行错误
- `96-127`: 数据错误

## 审计日志

测试执行日志位于 `.planning/` 目录。

## 持续改进

### 指标监控

- **测试通过率**: > 95%
- **执行时间**: < 10 分钟（smoke）
- **Flaky 测试率**: < 1%

### 定期审查

- 每月审查 flaky 测试
- 删除低价值测试
- 优化执行时间

## AI 自动化（2026）

详见 [`agents.md`](./agents.md) 文档。

## 参考

- [Playwright 官方文档](https://playwright.dev)
- [Playwright 最佳实践 2026](./agents.md)
