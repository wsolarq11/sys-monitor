# 四层架构联动 - 完整实施指南

**版本**: v1.0  
**创建日期**: 2026-04-16  
**状态**: ✅ 已实施  

---

## 🎯 核心架构

Agents/Skills/Rules/MCP四层架构的完整调用链：

```
Layer 0: Session Start
  Rule: spec-session-start.md (P0)
  Action: session-middleware.py
  
Layer 1: Intent Recognition
  Agent: spec-driven-core-agent
  Input: 用户消息 + current-spec.md
  Output: 意图分类 + 任务列表
  
Layer 2: Workflow Execution
  Skill: spec-driven-development
  Action: 加载模板 + 初始化工具
  
Layer 3: Task Delegation
  Agent: supervisor-agent
  Action: 任务编排 + 并行调度
  
Layer 4: Parallel Execution
  Agents: test-runner / code-review / doc-gen
  Action: 专业任务执行
  
Layer 5: Quality Gates
  Gate 1-5: 语法/测试/代码/文档/验收
  Action: 质量门禁检查
  
Layer 6: Tool Execution
  MCP: filesystem / git / shell
  Rule: automation-policy.md (风险评估)
  
Layer 7: Learning & Update
  Skill: memory-management
  Action: 记录决策 + 学习偏好
```

---

## 📊 完整调用链图

详见 [orchestration-flow.md](./orchestration-flow.md)（456行完整文档）

---

## 🔧 组件职责边界

### Rules (规则层) - 约束与验证

| Rule | 触发时机 | 职责 | 输出 |
|------|---------|------|------|
| **spec-session-start.md** | 每次会话开始 | 强制环境验证 | 验证报告 (pass/fail) |
| **automation-policy.md** | 每次操作前 | 风险评估 + 策略选择 | 执行策略 |
| **memory-usage.md** | 需要记忆时 | 判断是否应该创建记忆 | 记忆操作建议 |
| **AGENTS.md** | 始终激活 | 自我演进规则 | 改进建议 |

**关键约束**: 
- ❌ Rules 不得直接执行操作
- ✅ Rules 仅提供决策依据
- ✅ Rules 必须快速执行 (<500ms)

---

### Agents (智能体层) - 决策与协调

| Agent | 核心职责 | 输入 | 输出 | 不得做的事 |
|-------|---------|------|------|-----------|
| **spec-driven-core-agent** | Spec管理 + 意图识别 | 用户消息 + Spec | 意图分类 + 任务列表 | 不执行具体任务 |
| **supervisor-agent** | 任务编排 + 质量门禁 | 任务列表 | 调度计划 + 验收结果 | 不直接修改代码 |
| **test-runner-agent** | 测试执行 + 失败分析 | 代码路径 | 测试结果 + 修复建议 | 不自动修复代码 |
| **code-review-agent** | 静态分析 + 安全评分 | 代码变更 | 评分 + 问题列表 | 不批准合并 |
| **documentation-agent** | 文档生成 + 过时检测 | 代码 + 上下文 | 文档草稿 + 更新建议 | 不决定文档结构 |

**关键约束**:
- ❌ Agents 不得跳过 Rules 验证
- ✅ Agents 必须通过 MCP 调用工具
- ✅ Agents 必须记录决策日志

---

### Skills (技能层) - 工作流模板

| Skill | 提供内容 | 使用场景 |
|-------|---------|---------|
| **spec-driven-development** | Spec模板 + 初始化工具 | 新功能/重构/Bug修复 |
| **memory-management** | Memory操作指南 | 需要持久化知识时 |

**Skill vs Agent 的区别**:
```
Skill (被动): 提供模板、工具、最佳实践
  ↓ 被调用
Agent (主动): 读取Spec、分解任务、执行操作
```

**关键约束**:
- ❌ Skills 不得包含执行逻辑
- ✅ Skills 仅提供声明式模板
- ✅ Skills 文件大小 ≤10KB

---

### MCP (工具层) - 能力提供

| MCP Server | 能力 | 权限 | 风险等级 |
|-----------|------|------|---------|
| **filesystem** | 文件读写 | Read/Write (受限目录) | 🟡 中 |
| **git** | 版本控制 | Read/Write/Commit | 🟢 低 |
| **shell** | 命令执行 | 白名单命令 | 🔴 高 (默认禁用) |

**关键约束**:
- ❌ MCP 不得绕过 automation-policy 风险评估
- ✅ 所有 MCP 调用必须记录审计日志
- ✅ Shell MCP 默认禁用，需显式启用

---

## 🔄 典型场景调用链

### 场景 1: 新功能开发

```
用户: "添加文件夹大小监控功能"
  ↓
spec-session-start Rule → ✅ 验证通过
  ↓
spec-driven-core-agent → 意图: 新功能
  ↓
spec-driven-development Skill → 加载 feature-spec 模板
  ↓
supervisor-agent → 分解任务: [设计API, 实现后端, 编写测试, 更新文档]
  ↓
并行执行:
  ├─ documentation-agent → 生成 API 设计文档
  ├─ spec-driven-core-agent → 创建后端实现 Spec
  └─ test-runner-agent → 准备测试框架
  ↓
Gate 1-4 质量检查 → ✅ 全部通过
  ↓
MCP filesystem → 创建文件
MCP git → 提交代码
  ↓
memory-management Skill → 记录用户偏好
  ↓
响应: "功能已完成，Spec 进度 80%"
```

---

### 场景 2: Bug 修复

```
用户: "修复文件夹扫描超时问题"
  ↓
spec-session-start Rule → ✅ 验证通过
  ↓
spec-driven-core-agent → 意图: Bug修复
  ↓
spec-driven-development Skill → 加载 bugfix-spec 模板
  ↓
supervisor-agent → 分解任务: [复现Bug, 定位原因, 修复, 回归测试]
  ↓
test-runner-agent → 复现Bug + 编写回归测试
  ↓
spec-driven-core-agent → 定位原因 + 修复代码
  ↓
Gate 1-4 质量检查 → ✅ 全部通过
  ↓
MCP git → 提交修复
  ↓
memory-management Skill → 记录常见Bug模式
  ↓
响应: "Bug已修复，添加回归测试防止复发"
```

---

## 🚫 禁止的调用模式

### ❌ 反模式 1: 跳过验证

```
用户请求 → Agent 直接执行 (跳过 session-middleware)
```

**正确做法**:
```
用户请求 → spec-session-start Rule → session-middleware → Agent
```

---

### ❌ 反模式 2: Agent 直接操作文件

```
Agent → 直接写入文件系统
```

**正确做法**:
```
Agent → automation-policy Rule (风险评估) → MCP filesystem → 执行
```

---

### ❌ 反模式 3: Skill 包含执行逻辑

```
Skill → 直接执行任务
```

**正确做法**:
```
Skill → 提供模板 → Agent 读取模板 → Agent 执行
```

---

### ❌ 反模式 4: 绕过质量门禁

```
Agent → 直接提交代码 (跳过 Gate 1-5)
```

**正确做法**:
```
Agent → Gate 1-5 检查 → supervisor 验收 → MCP git 提交
```

---

## 📊 性能指标

| 环节 | 目标耗时 | 实际耗时 | 状态 |
|------|---------|---------|------|
| Session Middleware | <500ms | ~200ms | ✅ |
| Intent Recognition | <1s | - | ⏳ |
| Task Delegation | <500ms | - | ⏳ |
| Quality Gates | <5s | - | ⏳ |
| **总耗时** | **<10s** | **~200ms** | ✅ (仅Session) |

---

## ✅ 实施经验

1. **保持调用链透明**: 每次响应说明经过的组件和决策
2. **失败时提供修复指南**: 不只说"失败"，要说为什么+如何修复
3. **持续优化**: 定期Review哪些环节可合并/并行/缓存
4. **Skills收敛**: 避免功能重叠，保持≤5个核心Skill
5. **Memory scope="global"**: 铁律，严禁workspace scope

---

## 🔗 相关文件

- [orchestration-flow.md](./orchestration-flow.md) - 456行完整调用链规范
- [session-middleware.py](../../scripts/session-middleware.py) - 363行会话启动验证
- [constitution.md](../../specs/constitution.md) - 宪法第1章（不可变原则）
- [spec-session-start.md](../../rules/spec-session-start.md) - P0优先级Rule

---

*最后更新: 2026-04-16*
