# Sys-Monitor 测试快速参考

## 🚀 一键运行所有测试

```bash
# Rust测试
cd sys-monitor/src-tauri && cargo test --lib

# TypeScript测试  
cd .. && pnpm test

# E2E测试
cd tests/e2e && npx playwright test
```

## 📊 测试结果速览

| 类型 | 通过 | 失败 | 总计 |
|-----|------|------|------|
| Rust | 23 | 7* | 30 |
| TypeScript | 119 | 0 | 119 |
| E2E | 待验证 | - | 25 |

*注: 7个失败是已有代码的外键约束问题

## 🎯 关键命令

### Rust
```bash
cargo test                          # 运行所有测试
cargo test system_tests            # 运行特定模块
cargo test -- --nocapture          # 显示输出
cargo tarpaulin --out Html         # 覆盖率报告
```

### TypeScript
```bash
pnpm test                          # 运行所有测试
pnpm test:watch                    # 监视模式
pnpm test:ui                       # UI界面
pnpm vitest run --coverage        # 覆盖率报告
```

### E2E
```bash
npx playwright test                # 运行所有E2E
npx playwright test --headed       # 有头模式
npx playwright test --debug        # 调试模式
npx playwright show-report         # 查看报告
```

## 📁 文件位置

```
sys-monitor/
├── src-tauri/src/
│   ├── commands/system_test.rs           # ✅ 系统命令测试
│   ├── db/repository.rs (tests)          # ✅ 数据库测试
│   └── services/file_watcher_service.rs  # ✅ 文件监听测试
├── src/
│   ├── services/folderAnalysisApi.test.ts  # ✅ API测试
│   └── stores/
│       ├── metricsStore.test.ts            # ✅ 指标Store测试
│       └── scanStore.test.ts               # ✅ 扫描Store测试
└── tests/e2e/tests/
    ├── core-functionality.spec.ts          # ✅ E2E核心功能
    └── performance.spec.ts                 # ✅ 性能测试
```

## ⚡ 常见问题

**Q: Rust测试失败？**
```bash
cd sys-monitor/src-tauri
cargo clean && cargo build && cargo test
```

**Q: TypeScript类型错误？**
```bash
cd sys-monitor
pnpm install && pnpm exec tsc --noEmit
```

**Q: E2E浏览器未安装？**
```bash
cd tests/e2e
npx playwright install
```

## 📈 性能目标

- 页面加载: < 5s
- 首次绘制: < 3s
- API响应: < 100ms
- 内存增长: < 10MB
- 批量插入: > 1000 ops/sec

## 🔗 详细文档

- 完整指南: `TESTING_GUIDE.md`
- 测试报告: `TEST_REPORT.md`

---

最后更新: 2026-04-16
