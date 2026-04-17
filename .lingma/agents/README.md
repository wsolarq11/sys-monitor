# Agents 索引

**版本**: 1.1.0  
**最后更新**: 2026-04-18  
**总数**: 5个智能体

---

## 📋 快速导航

### 决策层 (Layer 1)

| Agent | 职责 | 文件大小 | 状态 |
|-------|------|---------|------|
| [Supervisor Agent](supervisor-agent.md) | 任务编排、质量门禁、最终验收 | 6.4KB | ⚠️ 需精简 |
| [Spec-Driven Core Agent](spec-driven-core-agent.md) | Spec管理、意图识别、自主执行 | 5.2KB | ⚠️ 需精简 |

### 执行层 (Layer 2)

| Agent | 职责 | 文件大小 | 状态 |
|-------|------|---------|------|
| [Code Review Agent](code-review-agent.md) | 代码审查、安全扫描、性能分析 | 4.5KB | ✅ 符合标准 |
| [Test Runner Agent](test-runner-agent.md) | 测试执行、失败分析、回归检测 | 5.4KB | ⚠️ 需精简 |
| [Documentation Agent](documentation-agent.md) | 文档生成、同步更新、质量检查 | 4.5KB | ✅ 符合标准 |

---

## 🎯 Agent职责总览

```
用户请求
   ↓
┌─────────────────────────────┐
│  Spec-Driven Core Agent     │  ← 意图识别、Spec管理
└──────────┬──────────────────┘
           │ 任务列表
           ↓
┌─────────────────────────────┐
│    Supervisor Agent         │  ← 任务编排、质量门禁
└──┬──────────┬───────────┬───┘
   │          │           │
   ↓          ↓           ↓
┌────────┐ ┌────────┐ ┌──────────┐
│ Code   │ │ Test   │ │ Document │  ← 并行执行
│ Review │ │ Runner │ │ ation    │
└───┬────┘ └───┬────┘ └────┬─────┘
    │          │            │
    └──────────┴────────────┘
               │
               ↓ 质量门禁通过
        ┌─────────────┐
        │  最终验收    │
        └─────────────┘
```

---

## 🔧 技术架构

### 核心技术栈

- **AsyncIO**: 异步执行框架
- **Redis**: 缓存 + Pub/Sub事件驱动
- **Python 3.8+**: 主要实现语言
- **Quality Gates**: 5层质量门禁系统

### 通信机制

```
Agent A ──PUBLISH──> Redis Pub/Sub <──SUBSCRIBE── Agent B
         (事件广播)                    (事件接收)
```

**频道命名规范**: `agent:{agent_name}:{event_type}`

示例:
- `agent:supervisor:started`
- `agent:code_review:completed`
- `agent:test_runner:failed`

### 缓存策略

**缓存键格式**: `result:{task_id}:{agent_name}`

**TTL设置**:
- 默认: 3600秒 (1小时)
- 可配置范围: 300-7200秒

**缓存内容**:
- 执行结果
- Spec状态
- 审查报告
- 测试结果

---

## 📊 性能指标

| Agent | P95响应时间 | 缓存命中率目标 | 并发支持 |
|-------|------------|---------------|---------|
| Supervisor | <5s | ≥60% | 10个Agent并行 |
| Spec-Driven Core | <10s | ≥60% | 5个Spec并行 |
| Code Review | <3s/文件 | ≥70% | 5个文件并行 |
| Test Runner | <30s/套件 | ≥75% | 3种测试类型并行 |
| Documentation | <5s/文档包 | ≥65% | 3种文档类型并行 |

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Redis
# Windows: 下载 https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server

# 启动Redis
redis-server
```

### 2. 验证Agent系统

```bash
# 运行文档完整性检查
python .lingma/scripts/verify-docs.py

# 检查Redis连接
redis-cli ping
# 应返回: PONG
```

### 3. 使用Agent

**方式1: 显式调用**
```
使用 supervisor-agent 编排任务
```

**方式2: 自动委托**
```
继续开发下一个功能
# AI会自动选择合适的Agent
```

---

## 📚 详细文档

### 架构文档
- [系统架构总览](../docs/architecture/ARCHITECTURE.md)
- [调用链规范](../docs/architecture/orchestration-flow.md)
- [质量门禁标准](../docs/architecture/agent-system/quality-gates.md)
- [四层架构详解](../docs/architecture/four-layer-architecture.md)

### API参考
- [统一API文档](../docs/api/agent-api-reference.md) 🆕
- [OpenAPI规范](../docs/api/openapi.yaml) 🆕
- [错误码规范](../docs/api/error-codes.md) 🆕

### 使用指南
- [快速开始](../docs/guides/QUICK_START.md)
- [Agent入门](../docs/guides/agents/getting-started.md) 🆕
- [配置指南](../docs/guides/agents/configuration.md) 🆕
- [故障排查](../docs/guides/agents/troubleshooting.md) 🆕

### 详细实现
- [Supervisor详细指南](../docs/architecture/agent-system/supervisor-detailed.md)
- [Spec-Driven详细指南](../docs/architecture/agent-system/spec-driven-core-agent-detailed.md)
- [Code Review详细指南](../docs/architecture/agent-system/code-review-agent-detailed.md)
- [Test Runner详细指南](../docs/architecture/agent-system/test-runner-agent-detailed.md)
- [Documentation详细指南](../docs/architecture/agent-system/documentation-agent-detailed.md)

---

## 🔄 变更历史

查看完整的Agent系统演进历史: [CHANGELOG.md](../CHANGELOG.md)

**最新版本**: 1.1.0 (2026-04-17)
- 新增Reflection Engine
- 增强质量反思能力

**重大版本**: 1.0.0 (2026-04-16)
- AsyncIO + Redis架构
- 5个完整Agent
- 5层质量门禁

---

## ⚠️ 注意事项

### 文件大小限制
根据量化标准，每个Agent文件应 ≤5KB。当前状态:
- ✅ code-review-agent.md (4.5KB)
- ✅ documentation-agent.md (4.5KB)
- ⚠️ spec-driven-core-agent.md (5.2KB) - 需精简0.2KB
- ⚠️ test-runner-agent.md (5.4KB) - 需精简0.4KB
- ⚠️ supervisor-agent.md (6.4KB) - 需精简1.4KB

**精简策略**: 将详细内容移至`docs/architecture/agent-system/`目录

### Redis依赖
所有Agent都依赖Redis服务:
- 确保Redis服务器正在运行
- 检查网络连接
- 监控缓存命中率

### 质量门禁
任何任务都必须通过5层质量门禁:
1. Agent自检
2. 测试验证
3. 代码审查 (≥80分)
4. 文档完整性
5. Supervisor最终验收 (≥85分)

**任何一层失败都会终止整个任务链，无法绕过。**

---

## 💡 最佳实践

### 1. 信任自动化
让Agent自主执行低风险任务，减少人工干预。

### 2. 定期审查
虽然Agent是自主的，但定期审查Spec进度和实施笔记。

### 3. 利用缓存
相同任务的第二次执行会从Redis缓存获取结果，速度提升显著。

### 4. 关注质量门禁
不要试图绕过质量门禁，它们保证了代码和文档的质量。

### 5. 记录决策
所有Agent决策都会记录到`.lingma/logs/decision-log.json`，便于追溯。

---

## 🆘 获取帮助

### 常见问题
- [故障排查FAQ](../docs/guides/agents/troubleshooting.md) 🆕
- [常见陷阱](../docs/common-pitfalls/) 

### 日志位置
- 决策日志: `.lingma/logs/decision-log.json`
- 审计日志: `.lingma/logs/audit.log`
- 错误日志: `.lingma/logs/errors.json`
- 操作日志: `.lingma/logs/operations.json`

### 社区支持
- 查看[架构决策报告](../docs/reports/unified-architecture-decision.md)
- 阅读[使命宣言](../docs/MISSION_STATEMENT.md)

---

**维护者**: Documentation Agent  
**联系方式**: 通过Issue或PR提交反馈  
**许可证**: 遵循项目许可证
