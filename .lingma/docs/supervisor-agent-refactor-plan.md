# Supervisor Agent 重构计划

**问题**: supervisor-agent.md 过于臃肿（435行/10KB），违反极简主义原则  
**目标**: 精简至 ≤ 2KB，详细内容移至 docs/ 或通过 Skills 引用  
**参考**: OpenAI/Claude Code 最佳实践（SOUL.md ≤ 500字，AGENTS.md ≤ 1000字）

---

## 📋 当前问题分析

### 臃肿内容
1. **详细的工作流示例**（模式 A/B/C/D）- 应移至 docs/
2. **TypeScript 接口定义** - 不应在 Agent 文件中
3. **质量门禁详细说明** - 应引用外部文档
4. **决策日志格式** - 应作为 Skill 或独立文档
5. **错误处理策略** - 应移至 automation-policy.md

### 应保留内容
1. ✅ Frontmatter（name/description/tools）
2. ✅ 核心角色定义（1-2句）
3. ✅ 关键职责列表（3-5条）
4. ✅ 触发方式
5. ✅ 核心工作流程（简化版，≤ 10行）

---

## 🎯 重构方案

### 方案 1: 极致精简（推荐）⭐

```markdown
---
name: supervisor-agent
description: Multi-agent orchestration engine. Manages task decomposition, intelligent delegation to worker agents, 5-layer quality gates, and final acceptance. Supports 4 orchestration patterns (Sequential/Parallel/Conditional/Iterative).
tools: Read, Write, Bash, Grep, Glob
---

# Supervisor Agent

**角色**: 多智能体编排引擎  
**职责**: 任务分解、智能委派、质量验收  

## 工作流程
1. 分析用户需求
2. 选择编排模式（Sequential/Parallel/Conditional/Iterative）
3. 委派给 Worker Agents
4. 执行 5层质量门禁
5. 最终验收并报告

## 可用 Workers
- spec-driven-core-agent: 代码实现
- test-runner-agent: 测试执行
- code-review-agent: 代码审查
- documentation-agent: 文档更新

## 参考文档
- 详细编排模式: docs/architecture/orchestration-patterns.md
- 质量门禁标准: docs/guides/quality-gates.md
- 决策日志格式: docs/api/decision-log.md
```

**预期大小**: ~500字 / 2KB

---

### 方案 2: 创建 Orchestration Skill

将详细的编排逻辑提取为 Skill：

```
.lingma/skills/multi-agent-orchestration/
├── SKILL.md              # Skill 定义
├── orchestration-patterns.md  # 4种编排模式详解
├── quality-gates.md      # 5层质量门禁标准
└── decision-log-format.md # 决策日志格式
```

**优点**:
- Agent 文件保持简洁
- 详细内容按需加载
- 可被其他 Agent 复用

---

### 方案 3: 混合方案

Agent 文件保留核心逻辑，详细内容通过 `Read` 工具动态读取：

```markdown
---
name: supervisor-agent
description: ...
tools: Read, Write, Bash, Grep, Glob
---

# Supervisor Agent

当需要详细了解编排模式时，读取: docs/architecture/orchestration-patterns.md
当需要了解质量门禁时，读取: docs/guides/quality-gates.md
```

---

## 📊 对比分析

| 方案 | Agent 文件大小 | 可维护性 | 灵活性 | 推荐度 |
|------|--------------|---------|--------|--------|
| 方案 1: 极致精简 | ~2KB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 方案 2: 创建 Skill | ~2KB + Skill | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 方案 3: 混合方案 | ~3KB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🚀 执行计划

### Phase 1: 创建详细文档
```bash
# 1. 创建编排模式文档
mkdir -p docs/architecture
mv supervisor-agent.md 中的工作流部分 → docs/architecture/orchestration-patterns.md

# 2. 创建质量门禁文档
mkdir -p docs/guides
mv supervisor-agent.md 中的质量门禁部分 → docs/guides/quality-gates.md
```

### Phase 2: 精简 Agent 文件
```bash
# 重写 supervisor-agent.md，仅保留核心内容
# 目标: ≤ 2KB
```

### Phase 3: 验证
```bash
python scripts/verify_system_effectiveness.py
# 检查:
# - Agent 文件大小 ≤ 2KB
# - Frontmatter 完整
# - Description 清晰
```

---

## 💡 核心教训

**社区最佳实践**:
> "给 Agent 一张地图，而非一本百科全书" - OpenAI/Claude Code

**我们的错误**:
- ❌ 在 Agent 文件中放置过多实现细节
- ❌ 包含 TypeScript 代码示例
- ❌ 详细的工作流图

**正确做法**:
- ✅ Agent 文件仅包含系统提示词
- ✅ 详细内容放在 docs/ 或通过 Skills 引用
- ✅ 保持简洁，聚焦核心职责

---

**下一步**: 等待用户确认后执行重构
