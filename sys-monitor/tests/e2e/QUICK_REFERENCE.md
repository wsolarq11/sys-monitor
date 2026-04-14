# Playwright 测试快速参考

## 定位器优先级（必须遵循）

```typescript
// 1️⃣ getByRole - 首选
page.getByRole('button', { name: 'Submit' })
page.getByRole('link', { name: 'Dashboard' })
page.getByRole('heading', { name: /dashboard/i })

// 2️⃣ getByLabel - 表单元素
page.getByLabel('Email')
page.getByLabel(/password/i')

// 3️⃣ getByPlaceholder - 输入框
page.getByPlaceholder('Enter email')
page.getByPlaceholder(/.*文件夹路径.*/)

// 4️⃣ getByText - 文本内容
page.getByText('Success')
page.getByText(/cpu usage/i)

// 5️⃣ getByTestId - 仅在必要时
page.getByTestId('submit-button')

// 6️⃣ locator - 最后手段
page.locator('.custom-class')
```

## 常用断言

```typescript
// 可见性
await expect(locator).toBeVisible()
await expect(locator).not.toBeVisible()

// 状态
await expect(locator).toBeEnabled()
await expect(locator).toBeDisabled()
await expect(locator).toHaveValue('expected')

// 文本内容
await expect(locator).toContainText('partial')
await expect(locator).toHaveText(/regex/)

// URL
await expect(page).toHaveURL(/.*dashboard/)
```

## 运行命令

```bash
# Smoke 测试 - 部署验证
pnpm test:smoke

# Critical 测试 - 每日 CI
pnpm test:critical

# Regression 测试 - 分支合并
pnpm test:regression

# 视觉回归测试
pnpm test:visual

# 有头模式
pnpm test:headed

# 调试模式
pnpm test:debug

# UI 模式
pnpm test:ui
```

## PowerShell 脚本

```powershell
# 运行 Smoke 测试
.\run-tests.ps1 -TestType smoke

# 有头模式
.\run-tests.ps1 -TestType critical -headed

# 调试模式
.\run-tests.ps1 -TestType regression -Debug
```

## 测试模板

```typescript
import { test, expect } from '../fixtures/test-fixtures';

test.describe('Feature Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should do something @smoke', async ({ page }) => {
    // 使用 getByRole 定位
    await expect(page.getByRole('heading', { name: 'Title' }))
      .toBeVisible();
  });
});
```

## POM 模板

```typescript
import { Page, Locator } from '@playwright/test';

export class FeaturePage {
  readonly page: Page;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.submitButton = page.getByRole('button', { name: 'Submit' });
  }

  async goto() {
    await this.page.goto('/feature');
  }

  async submit() {
    await this.submitButton.click();
  }
}
```

## API Mock

```typescript
// 成功响应
await page.route('**/api/data', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ key: 'value' })
  });
});

// 错误响应
await page.route('**/api/data', route => {
  route.fulfill({
    status: 500,
    body: JSON.stringify({ error: 'Failed' })
  });
});

// 延迟响应
await page.route('**/api/data', async route => {
  await new Promise(r => setTimeout(r, 2000));
  route.fulfill({ status: 200, body: '{}' });
});
```

## 视觉回归测试

```typescript
// 基础截图
await expect(page).toHaveScreenshot('baseline.png');

// 全页截图
await expect(page).toHaveScreenshot('full.png', { fullPage: true });

// Mask 动态区域
await expect(page).toHaveScreenshot('masked.png', {
  mask: [page.locator('[data-dynamic]')]
});
```

## CI 配置

```yaml
# GitHub Actions
- name: Run tests
  run: pnpm exec playwright test --project=smoke

# Docker
docker-compose run playwright-smoke
```

## Workers 调优

```bash
# 本地并行
pnpm test --workers=4

# CI Sharding
pnpm test --shard=1/4
```

## 常见问题

### 测试失败
1. 检查定位器是否使用 getByRole 优先
2. 检查是否需要 waitForLoadState
3. 检查 API mock 是否正确

### 测试 flaky
1. 避免硬编码等待
2. 使用条件等待替代
3. 检查网络请求竞态

### 视觉回归差异
1. 固定 viewport: `setViewportSize({ width: 1920, height: 1080 })`
2. Mask 动态区域
3. 使用 Docker 保证环境一致
