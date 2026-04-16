# FolderAnalysis 模块质量保障体系

## 📊 概述

本文档定义了FolderAnalysis模块的完整质量保障策略，包括测试金字塔、质量门禁标准和持续集成流程。

---

## 🎯 质量目标

### 核心指标
- **单元测试覆盖率**: ≥ 80%
- **集成测试覆盖率**: ≥ 70%
- **E2E测试通过率**: ≥ 95%
- **关键路径测试覆盖**: 100%
- **构建成功率**: ≥ 99%

### 性能指标
- 单元测试执行时间: < 30秒
- 集成测试执行时间: < 2分钟
- E2E测试执行时间: < 10分钟
- CI总执行时间: < 15分钟

---

## 🏗️ 测试金字塔架构

### 1. 单元测试层 (Unit Tests) - 基础层

**目标**: 验证纯函数和工具类的正确性

**覆盖范围**:
- ✅ src/utils/validation.ts - 路径验证函数
- ✅ src/utils/format.ts - 格式化函数
- ✅ src/utils/time.ts - 时间处理函数
- ✅ src/stores/scanStore.ts - 状态管理逻辑
- ⚠️ src/stores/metricsStore.ts - 已有部分测试

**测试文件清单**:
`
src/utils/
├── validation.test.ts      # 新建 - 路径验证测试
├── format.test.ts          # 已存在 - 格式化测试
└── time.test.ts            # 新建 - 时间处理测试

src/stores/
├── scanStore.test.ts       # 新建 - 扫描状态测试
└── metricsStore.test.ts    # 已存在 - 指标状态测试
`

**执行命令**:
`ash
npm test                    # 运行所有单元测试
npm run test:watch         # 监听模式
npm run test:ui            # UI模式
`

---

### 2. 集成测试层 (Integration Tests) - 中间层

**目标**: 验证组件间交互和数据流

**测试场景**:
1. **Store与UI组件集成**
   - 扫描状态同步
   - 错误状态传播
   - 历史记录更新

2. **Tauri API与前端集成**
   - invoke调用链路
   - 事件监听机制
   - 异步操作处理

3. **路由与页面集成**
   - 页面导航
   - 参数传递
   - 状态保持

**测试文件** (待创建):
`
tests/integration/
├── store-integration.spec.ts
├── tauri-api-integration.spec.ts
└── routing-integration.spec.ts
`

---

### 3. E2E测试层 (End-to-End Tests) - 顶层

**目标**: 验证完整的用户流程和业务场景

**测试分类**:

#### 冒烟测试 (Smoke Tests) - @smoke
- 应用启动
- 页面加载
- 核心功能可用性

**位置**: 	ests/e2e/tests/smoke/

#### 关键路径测试 (Critical Tests) - @critical
- 文件夹扫描完整流程
- 系统监控数据展示
- 数据库操作

**位置**: 	ests/e2e/tests/critical/

#### 回归测试 (Regression Tests) - @regression
- 历史Bug修复验证
- 边界条件测试
- 异常处理

**位置**: 	ests/e2e/tests/regression/

#### 完整E2E测试
- 多步骤用户旅程
- 跨页面交互
- 复杂业务场景

**位置**: 	ests/e2e/tests/*.spec.ts

---

## 🔧 Tauri API Mock 方案

### Mock 架构

`
Playwright Test
    ↓
page.route() 拦截网络请求
    ↓
模拟 Tauri invoke 响应
    ↓
返回Mock数据或错误
`

### Mock 配置示例

`	ypescript
import { setupCommonMocks } from '../utils/tauriMock';

test.beforeEach(async ({ page }) => {
  // 注入常用Mock
  await setupCommonMocks(page, 'folder-analysis');
});
`

### 支持的Mock场景

1. **正常流程Mock**
   - select_folder → 返回有效路径
   - scan_folder → 返回扫描结果
   - get_folder_scans → 返回历史记录

2. **错误场景Mock**
   - 文件夹不存在
   - 权限不足
   - 数据库连接失败
   - 网络超时

3. **边界条件Mock**
   - 空数据返回
   - 超大数据集
   - 特殊字符路径

---

## 🚪 质量门禁标准

### 代码提交前检查 (Pre-commit)

`ash
# 1. 代码格式检查
npx prettier --check "src/**/*.{ts,tsx}"

# 2. TypeScript类型检查
npx tsc --noEmit

# 3. ESLint检查
npx eslint "src/**/*.{ts,tsx}"

# 4. 单元测试
npm test
`

### CI门禁要求

| 检查项 | 阈值 | 失败动作 |
|--------|------|----------|
| 单元测试通过率 | 100% | 阻断合并 |
| 代码覆盖率 | ≥ 80% | 警告 |
| E2E测试通过率 | ≥ 95% | 阻断合并 |
| 构建成功 | 100% | 阻断合并 |
| 代码规范 | 0 errors | 阻断合并 |
| 安全扫描 | 0 critical | 阻断合并 |

### 发布前检查清单

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 所有E2E测试通过 (@critical必须100%)
- [ ] 代码覆盖率达标
- [ ] 性能测试通过
- [ ] 安全扫描无高危漏洞
- [ ] 文档已更新
- [ ] Changelog已编写

---

## 🔄 持续集成流程

### GitHub Actions Workflow

`yaml
name: Quality Gate

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # 阶段1: 快速反馈
  quick-checks:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: pnpm install
      - name: Type check
        run: npx tsc --noEmit
      - name: Lint
        run: npx eslint "src/**/*.{ts,tsx}"
      - name: Unit tests
        run: npm test
      - name: Coverage check
        run: npm test -- --coverage

  # 阶段2: E2E测试
  e2e-tests:
    needs: quick-checks
    runs-on: windows-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v3
      - name: Install Playwright
        run: npx playwright install chromium
      - name: Run E2E tests
        run: npx playwright test
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/e2e/test-results/

  # 阶段3: 构建验证
  build:
    needs: [quick-checks, e2e-tests]
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build application
        run: npm run build
`

### 本地开发工作流

`ash
# 1. 开发时运行
npm run test:watch          # 监听模式单元测试

# 2. 提交前检查
git add .
npx lint-staged             # 自动格式化和检查

# 3. 完整测试套件
npm test                    # 单元测试
cd tests/e2e && npx playwright test  # E2E测试

# 4. 生成测试报告
npx playwright test --reporter=html
`

---

## 📈 测试覆盖率要求

### 按模块划分

| 模块 | 语句覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|-----------|-----------|-----------|
| utils/ | ≥ 90% | ≥ 85% | 100% |
| stores/ | ≥ 85% | ≥ 80% | ≥ 90% |
| components/ | ≥ 70% | ≥ 65% | ≥ 75% |
| services/ | ≥ 80% | ≥ 75% | ≥ 85% |

### 排除项

以下代码不要求覆盖率:
- 类型定义文件 (*.d.ts)
- 配置文件 (vite.config.ts等)
- 测试文件本身 (*.test.ts)
- Storybook文件 (*.stories.tsx)

---

## 🐛 缺陷管理

### Bug优先级定义

- **P0 (Blocker)**: 导致应用崩溃、数据丢失
  - 响应时间: 立即
  - 修复时间: < 4小时
  
- **P1 (Critical)**: 核心功能不可用
  - 响应时间: < 1小时
  - 修复时间: < 24小时
  
- **P2 (Major)**: 重要功能异常
  - 响应时间: < 4小时
  - 修复时间: < 3天
  
- **P3 (Minor)**: 轻微问题、UI瑕疵
  - 响应时间: < 1天
  - 修复时间: < 1周

### Bug修复流程

1. 创建Issue并标记优先级
2. 编写失败的测试用例(复现Bug)
3. 修复代码使测试通过
4. 添加回归测试防止复发
5. Code Review后合并

---

## 📊 度量与报告

### 每日报告

自动生成并发送到团队频道:
- 测试通过率趋势
- 代码覆盖率变化
- 新增/修复Bug数量
- CI构建成功率

### 周报内容

- 本周测试覆盖增长
- 发现的典型问题
- 测试改进建议
- 下周期测试计划

---

## 🚀 持续改进

### 每月回顾

1. **测试有效性评估**
   - 哪些测试发现了真实Bug?
   - 哪些测试是冗余的?
   - 测试维护成本是否合理?

2. **工具链优化**
   - 是否有更好的测试框架?
   - Mock策略是否需要调整?
   - CI/CD流程是否可以加速?

3. **团队能力提升**
   - 测试技能培训需求
   - 最佳实践分享
   - 新成员onboarding

---

## 📚 参考资源

### 内部文档
- [Tauri API Mock使用指南](./tauri-mock-guide.md)
- [测试编写规范](./testing-conventions.md)
- [CI/CD配置说明](./ci-cd-setup.md)

### 外部资源
- [Playwright官方文档](https://playwright.dev/)
- [Vitest最佳实践](https://vitest.dev/guide/)
- [测试金字塔理论](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## ✅ 实施检查清单

### Phase 1: 基础建设 (Week 1-2)
- [x] 创建validation.test.ts
- [x] 创建time.test.ts
- [x] 创建scanStore.test.ts
- [x] 完善format.test.ts
- [x] 实现Tauri API Mock工具

### Phase 2: E2E测试修复 (Week 3)
- [x] 创建tauriMock.ts
- [x] 修复folder-analysis测试
- [ ] 修复其他E2E测试
- [ ] 添加缺失的测试场景

### Phase 3: 集成测试补充 (Week 4)
- [ ] 创建Store集成测试
- [ ] 创建API集成测试
- [ ] 创建路由集成测试

### Phase 4: CI/CD集成 (Week 5)
- [ ] 配置GitHub Actions
- [ ] 设置质量门禁
- [ ] 自动化测试报告

### Phase 5: 持续优化 (Ongoing)
- [ ] 监控测试指标
- [ ] 定期清理无效测试
- [ ] 优化测试执行速度
- [ ] 提升测试可维护性

---

**最后更新**: 2026-04-16  
**维护者**: QA Team  
**版本**: 1.0.0
