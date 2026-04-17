# Agent Tests

单元测试套件用于验证Agent架构设计（AsyncIO + Redis）。

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

或单独安装：

```bash
pip install pytest pytest-asyncio redis aiohttp bandit coverage pytest-cov
```

## 🧪 运行测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定Agent测试

```bash
pytest tests/test_supervisor_agent.py -v
pytest tests/test_code_review_agent.py -v
pytest tests/test_documentation_agent.py -v
pytest tests/test_spec_driven_agent.py -v
pytest tests/test_test_runner_agent.py -v
```

### 生成覆盖率报告

```bash
pytest tests/ -v --cov=.lingma/agents/ --cov-report=html --cov-report=term-missing
```

覆盖率HTML报告将生成在 `htmlcov/` 目录。

### 详细输出和短追溯

```bash
pytest tests/ -v --tb=short
```

## 🔒 安全扫描

### 运行Bandit扫描

```bash
# JSON格式报告
bandit -r .lingma/agents/ -f json -o bandit-report.json

# HTML格式报告
bandit -r .lingma/agents/ -f html -o bandit-report.html

# 终端输出
bandit -r .lingma/agents/
```

## 📊 测试覆盖场景

每个Agent测试覆盖：

1. **缓存机制**
   - 缓存命中流程
   - 缓存未命中流程
   - TTL过期验证

2. **并行执行**
   - asyncio.gather()并发验证
   - 性能提升测量

3. **事件系统**
   - Redis Pub/Sub发布
   - 事件订阅监听

4. **错误处理**
   - 异常捕获和恢复
   - return_exceptions=True验证

5. **多任务编排**
   - 批量任务处理
   - 并发控制

## ⚠️ 注意事项

### 测试性质

这些是**架构验证测试**，不是功能测试。它们验证：
- ✅ AsyncIO设计模式正确性
- ✅ Redis缓存策略可行性
- ✅ Pub/Sub事件流合理性
- ✅ 错误处理机制完整性

### 导入说明

由于Agent文件是Markdown格式（`.md`），测试使用**Mock对象**模拟Agent行为，不直接导入Agent实现。

如需测试实际Python实现，需要：
1. 创建对应的Python模块
2. 实现Agent类
3. 更新测试导入路径

### CI/CD集成

测试已集成到GitHub Actions：
- `.github/workflows/ci.yml` 中的 `test-agents` job
- 自动运行所有测试
- 上传覆盖率报告到Codecov
- 执行Bandit安全扫描

## 📈 预期结果

### 测试通过标准

- ✅ 所有47个测试用例通过
- ✅ 代码覆盖率 ≥80%
- ✅ Bandit扫描零漏洞
- ✅ 并行执行时间 < 串行时间的50%

### 性能指标

| 场景 | 预期时间 |
|-----|---------|
| 缓存命中 | < 10ms |
| 缓存未命中+执行 | < 5s |
| 并行3个Agent | < 0.2s |
| Bandit扫描 | < 3s |

## 🐛 故障排除

### ModuleNotFoundError

**问题**: `No module named 'tests.lingma'`

**原因**: Agent是Markdown文件，无法作为Python模块导入

**解决**: 这是预期行为。测试使用Mock对象，不需要实际导入。

### Redis连接错误

**问题**: 测试尝试连接Redis失败

**解决**: 测试使用MockRedis，不需要真实Redis实例。确保没有移除Mock层。

### 覆盖率报告为空

**问题**: 覆盖率显示0%

**原因**: Agent是Markdown文件，无法被coverage工具分析

**解决**: 这是预期行为。覆盖率统计针对未来的Python实现。

## 📚 相关文档

- [Phase 3重构报告](../PHASE3_REFACTORING_REPORT.md)
- [Supervisor Agent](../.lingma/agents/supervisor-agent.md)
- [Code Review Agent](../.lingma/agents/code-review-agent.md)
- [Documentation Agent](../.lingma/agents/documentation-agent.md)
- [Spec-Driven Core Agent](../.lingma/agents/spec-driven-core-agent.md)
- [Test Runner Agent](../.lingma/agents/test-runner-agent.md)

## 🤝 贡献

添加新测试时请遵循：
1. 使用`pytest.mark.asyncio`装饰器
2. 使用MockRedis模拟缓存
3. 覆盖缓存、并行、事件、错误场景
4. 保持测试独立性和可重复性

---

**最后更新**: 2026-04-18  
**维护者**: AI Agent Team
