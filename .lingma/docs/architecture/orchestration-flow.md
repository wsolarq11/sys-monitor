# Agents/Skills/Rules/MCP 调用链规范

**版本**: v1.0  
**生效日期**: 2026-04-16  
**状态**: ✅ 强制执行  

---

## 🎯 核心原则

**单一职责 + 明确调用 + 不可绕过**

每个组件只能做自己最擅长的事，通过标准接口调用其他组件，任何环节都不得跳过。

---

## 📊 完整调用链图

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 0: Session Start (强制触发)                           │
│  Rule: spec-session-start.md (P0 优先级)                     │
│  Action: 运行 session-middleware.py                          │
│  Output: 验证报告 (pass/fail)                                │
│  失败处理: 🔴 阻断会话 (除非 --force-bypass)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ ✅ 验证通过
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Intent Recognition (意图识别)                      │
│  Agent: spec-driven-core-agent                               │
│  Input: 用户消息 + current-spec.md                           │
│  Action:                                                     │
│    1. 读取 Spec 状态                                         │
│    2. 分析用户意图 (新功能/继续开发/需求变更/查询)            │
│    3. 决定下一步动作                                         │
│  Output: 意图分类 + 任务列表                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Workflow Execution (工作流执行)                    │
│  Skill: spec-driven-development                              │
│  Input: 意图分类 + 任务列表                                  │
│  Action:                                                     │
│    1. 加载对应模板 (feature/refactor/bugfix)                 │
│    2. 初始化任务环境                                         │
│    3. 提供工具集                                             │
│  Output: 初始化的工作环境                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Task Delegation (任务委派)                         │
│  Agent: supervisor-agent (编排引擎)                          │
│  Input: 任务列表                                             │
│  Action:                                                     │
│    1. 分析任务依赖关系                                       │
│    2. 并行/串行调度                                          │
│    3. 委派给专业 Agent                                       │
│  Output: 调度计划                                            │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│ Parallel Tasks   │   │ Sequential Tasks │
└────┬─────┬───────┘   └────────┬─────────┘
     │     │                     │
     ▼     ▼                     ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ test-runner │  │ code-review │  │ doc-gen     │
│ Agent       │  │ Agent       │  │ Agent       │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                 │
       ▼                ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Quality Gates (质量门禁)                           │
│  Gate 1: 语法检查 (test-runner)                              │
│  Gate 2: 单元测试通过率 ≥80% (test-runner)                   │
│  Gate 3: 代码评分 ≥80 (code-review)                          │
│  Gate 4: 文档完整性 (doc-gen)                                │
│  Gate 5: 最终验收 (supervisor)                               │
│  失败处理: 🟡 返回修复 / 🔴 终止流程                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ ✅ 全部通过
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Execution (具体执行)                               │
│  Tools: MCP Servers                                          │
│    - filesystem: 文件读写                                    │
│    - git: 版本控制                                           │
│    - shell: 命令执行 (受限)                                   │
│  Rules: automation-policy.md (风险评估)                      │
│  Action:                                                     │
│    1. 评估操作风险                                           │
│    2. 选择执行策略 (auto/snapshot/ask/approval)              │
│    3. 执行操作                                               │
│    4. 记录审计日志                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 6: Learning & Update (学习与更新)                     │
│  Skill: memory-management                                    │
│  Input: 执行结果 + 用户反馈                                  │
│  Action:                                                     │
│    1. 记录决策过程                                           │
│    2. 学习用户偏好                                           │
│    3. 更新 Spec 状态                                         │
│    4. 生成实施笔记                                           │
│  Output: 更新的 Memory + Spec                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Response to User                                            │
│  Content:                                                    │
│    - 任务完成状态                                            │
│    - Spec 进度更新                                           │
│    - 下一步建议                                              │
│    - 学到的新偏好 (如有)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 组件职责定义

### 1. Rules (规则层) - 约束与验证

| Rule | 触发时机 | 职责 | 输出 |
|------|---------|------|------|
| **spec-session-start.md** | 每次会话开始 | 强制环境验证 | 验证报告 (pass/fail) |
| **automation-policy.md** | 每次操作前 | 风险评估 + 策略选择 | 执行策略 (auto/snapshot/ask/approval) |
| **memory-usage.md** | 需要记忆时 | 判断是否应该创建记忆 | 记忆操作建议 |
| **AGENTS.md** | 始终激活 | 自我演进规则 | 改进建议 |

**关键约束**:
- ❌ Rules 不得直接执行操作
- ✅ Rules 仅提供决策依据
- ✅ Rules 必须快速执行 (<500ms)

---

### 2. Agents (智能体层) - 决策与协调

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

### 3. Skills (技能层) - 工作流模板

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

### 4. MCP (工具层) - 能力提供

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

### 场景 3: 架构重构

```
用户: "重构数据库访问层"
  ↓
spec-session-start Rule → ✅ 验证通过
  ↓
spec-driven-core-agent → 意图: 重构
  ↓
spec-driven-development Skill → 加载 refactor-spec 模板
  ↓
supervisor-agent → ⚠️ 检测到高风险操作
  ↓
automation-policy Rule → 风险评估: high → 要求用户确认
  ↓
用户: "确认执行"
  ↓
code-review-agent → 分析现有代码
  ↓
spec-driven-core-agent → 制定重构方案
  ↓
Gate 1-5 严格质量检查 → ✅ 全部通过
  ↓
MCP git → 创建特性分支 + 提交
  ↓
memory-management Skill → 记录重构模式
  ↓
响应: "重构完成，请Review PR #123"
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

## 📋 实现清单

### 已实现 ✅

- [x] spec-session-start Rule (P0 优先级)
- [x] session-middleware.py (验证引擎)
- [x] spec-driven-core-agent (意图识别)
- [x] spec-driven-development Skill (工作流模板)
- [x] automation-policy Rule (风险评估)
- [x] constitution.md (不可变原则)

### 待实现 ⏳

- [ ] supervisor-agent (任务编排)
- [ ] test-runner-agent (测试执行)
- [ ] code-review-agent (代码审查)
- [ ] documentation-agent (文档生成)
- [ ] MCP servers 配置
- [ ] 质量门禁实现 (Gate 1-5)
- [ ] decision-log.json (决策日志)

---

## 🔍 验证方法

### 自动化验证脚本

```python
# .lingma/scripts/verify-orchestration.py
def verify_orchestration():
    """验证调用链完整性"""
    
    checks = [
        check_session_middleware_exists(),
        check_spec_file_exists(),
        check_agents_defined(),
        check_skills_available(),
        check_rules_active(),
        check_mcp_configured(),
    ]
    
    if all(checks):
        print("✅ Orchestration chain intact")
        return True
    else:
        print("❌ Orchestration chain broken")
        return False
```

### 手动验证步骤

1. **开启新会话** → 观察是否自动执行 session-middleware
2. **发送请求** → 检查 spec-driven-core-agent 是否读取 Spec
3. **执行任务** → 验证是否经过 quality gates
4. **查看日志** → 确认 decision-log.json 有记录

---

## 📊 性能指标

| 环节 | 目标耗时 | 实际耗时 | 状态 |
|------|---------|---------|------|
| Session Middleware | <500ms | ~200ms | ✅ |
| Intent Recognition | <1s | - | ⏳ |
| Task Delegation | <500ms | - | ⏳ |
| Quality Gates | <5s | - | ⏳ |
| MCP Execution | 视操作而定 | - | ⏳ |
| **总耗时** | **<10s** | **~200ms** | ✅ (仅Session) |

---

## 🎓 最佳实践

### 1. 保持调用链透明

每次响应都应说明：
- 经过了哪些组件
- 做出了什么决策
- 下一步是什么

### 2. 失败时提供修复指南

不要只说"失败"，要说：
- 为什么失败
- 如何修复
- 是否可以绕过

### 3. 持续优化调用链

定期 Review：
- 哪些环节可以合并
- 哪些环节可以并行
- 哪些环节可以缓存

---

## 📝 变更记录

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 2026-04-16 | v1.0 | 初始版本，定义完整调用链 | AI Assistant |

---

**本规范为强制执行标准，所有 Agents/Skills/Rules/MCP 必须遵循此调用链。**

违反此规范将导致验证失败和会话阻断。
