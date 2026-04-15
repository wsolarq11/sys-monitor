# 内置 Agent 使用指南

## 📋 概述

我们创建了一个**内置的 Spec-Driven Core Agent**，它将作为系统的核心协调者，利用 Lingma 的原生 Agent 系统来管理整个 Spec-Driven Development 工作流。

---

## 🎯 Agent 信息

**名称**: `spec-driven-core-agent`  
**位置**: `.lingma/agents/spec-driven-core-agent.md`  
**作用域**: 项目级别（团队共享）  
**工具权限**: Read, Write, Bash, Grep, Glob  

---

## 🚀 如何使用

### 方式 1: 显式调用

在对话中直接指定使用这个 Agent：

```
使用 spec-driven-core-agent 来检查当前 spec 状态
```

或者：

```
让 spec-driven-core-agent 继续执行下一个任务
```

### 方式 2: 自动委托

由于我们在 description 中包含了 "Proactively" 和明确的触发词，AI 会在以下情况**自动委托**给这个 Agent：

- 提到 "spec" 或 "specification"
- 请求继续开发
- 询问项目状态
- 需要澄清需求
- 执行自动化任务

**示例**:
```
用户: "继续开发"
AI: (自动检测到与 spec 相关) → 委托给 spec-driven-core-agent
```

---

## 💡 典型使用场景

### 场景 1: 会话启动 - 检查状态

```
使用 spec-driven-core-agent 检查当前开发状态
```

**Agent 会**:
1. 读取 `.lingma/specs/current-spec.md`
2. 显示当前进度
3. 列出已完成和待完成的任务
4. 提出需要澄清的问题（如有）
5. 建议下一步行动

### 场景 2: 继续开发

```
让 spec-driven-core-agent 继续执行
```

**Agent 会**:
1. 找到下一个未完成的任务
2. 评估风险并选择执行策略
3. 自主执行任务
4. 更新 spec
5. 报告结果

### 场景 3: 创建新功能 Spec

```
使用 spec-driven-core-agent 帮我创建导出功能的 spec
```

**Agent 会**:
1. 提出澄清问题（格式、内容、优先级等）
2. 创建 spec draft
3. 呈现给您审批
4. 等待确认后开始开发

### 场景 4: 需求变更

```
spec-driven-core-agent，我想调整阈值告警的触发条件
```

**Agent 会**:
1. 评估变更影响
2. 列出受影响的任务
3. 提出澄清问题
4. 给出选项
5. 根据您的选择更新 spec

---

## 🔧 Agent 能力

### 1. Spec 生命周期管理

- ✅ 创建新 spec
- ✅ 加载现有 spec
- ✅ 更新 spec 状态
- ✅ 归档完成的 spec
- ✅ 从历史恢复 spec

### 2. 自动化协调

- ✅ 调用 automation-engine.py 评估风险
- ✅ 使用 operation-logger.py 记录操作
- ✅ 通过 snapshot-manager.py 创建/回滚快照
- ✅ 集成 spec-driven-agent.py 执行任务

### 3. Rules 强制执行

- ✅ 加载 `.lingma/rules/` 中的所有规则
- ✅ 在执行前检查约束
- ✅ 阻止违反规则的操作
- ✅ 报告规则违规

### 4. Skills 应用

- ✅ 发现可用的 skills
- ✅ 加载适用的 skill
- ✅ 按照 skill 定义的工作流程执行
- ✅ 组合多个 skills

### 5. 智能决策

- ✅ 风险评估（低/中/高/严重）
- ✅ 置信度计算
- ✅ 策略选择（auto/snapshot/ask/approve）
- ✅ 基于历史学习优化

---

## 📊 Agent 工作流程

```
用户请求
   ↓
┌─────────────────────┐
│ 1. 解析意图          │
│    - 识别任务类型    │
│    - 提取参数        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 2. 检查 Spec 状态    │
│    - 读取 current    │
│    - 提取上下文      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 3. 加载 Skills       │
│    - 发现适用 skill  │
│    - 加载工作流程    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 4. 应用 Rules        │
│    - 检查约束        │
│    - 验证合法性      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 5. 风险评估          │
│    - 计算风险分数    │
│    - 选择执行策略    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 6. 执行任务          │
│    - 调用工具        │
│    - 记录日志        │
│    - 验证结果        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 7. 更新 Spec         │
│    - 标记任务完成    │
│    - 添加实施笔记    │
│    - 更新进度        │
└────────┬────────────┘
         │
         ▼
    返回结果给用户
```

---

## 🎓 最佳实践

### 1. 信任自动化

对于低风险操作，让 Agent 自主执行：

```
✅ 好: "继续执行下一个任务"
❌ 不好: "请告诉我下一步要做什么，然后我确认后再执行"
```

### 2. 提供清晰的反馈

当 Agent 提出澄清问题时，给出明确的答案：

```
✅ 好: "1A, 2B, 3A"
✅ 好: "使用 PDF 格式，包含汇总统计和详细列表，手动触发"
❌ 不好: "随便" 或 "你决定"
```

### 3. 定期审查进度

虽然 Agent 是自主的，但定期审查可以确保方向正确：

```
"spec-driven-core-agent，显示当前进度和实施笔记"
```

### 4. 利用历史记录

查看已完成的 specs 了解模式：

```bash
ls .lingma/specs/spec-history/
cat .lingma/specs/spec-history/[spec-name].md
```

### 5. 自定义配置

根据需要调整 Agent 行为：

编辑 `.lingma/config/agent-config.json`:
```json
{
  "execution": {
    "max_retries": 3,
    "timeout_seconds": 300
  },
  "memory": {
    "short_term": {
      "max_messages": 50
    }
  }
}
```

---

## 🔍 监控和调试

### 查看 Agent 日志

```bash
# 查看操作日志
cat .lingma/logs/operations.json | python -m json.tool

# 查看审计日志
tail -f .lingma/logs/audit.log

# 查看错误日志
cat .lingma/logs/errors.json | python -m json.tool
```

### 检查快照状态

```bash
# 列出所有快照
python .lingma/scripts/snapshot-manager.py list

# 查看快照统计
python .lingma/scripts/snapshot-manager.py stats
```

### 验证 Agent 配置

```bash
# 运行测试
python .lingma/scripts/test-agent.py

# 检查配置文件
cat .lingma/config/agent-config.json | python -m json.tool
```

---

## ⚠️ 注意事项

### 1. 工具权限限制

当前 Agent 只有以下工具权限：
- ✅ Read - 读取文件
- ✅ Write - 写入文件
- ✅ Bash - 执行命令
- ✅ Grep - 搜索内容
- ✅ Glob - 查找文件

**没有的权限**:
- ❌ Edit - 不能直接编辑（需要通过 Write）
- ❌ WebFetch - 不能访问外部 URL
- ❌ WebSearch - 不能进行网络搜索

如果需要更多权限，编辑 `.lingma/agents/spec-driven-core-agent.md` 的 `tools` 字段。

### 2. 隔离上下文

Agent 在**隔离的上下文**中运行，这意味着：
- ✅ 不会污染主对话的上下文
- ✅ 有专门的系统提示
- ✅ 只能访问授权的工具

### 3. 自主性边界

Agent 被设计为**尽可能自主**，但在以下情况会停止并询问：
- 风险等级 >= 0.8（高风险）
- 需求不明确或歧义
- 遇到无法自动解决的问题
- 违反 Rules 约束

---

## 🔄 与其他组件的关系

```
.spec-driven-core-agent (内置 Agent)
    ↓ 协调
.spec-driven-agent.py (Python Agent 类)
    ↓ 调用
.automation-engine.py (风险评估)
.operation-logger.py (日志记录)
.snapshot-manager.py (快照管理)
    ↓ 使用
.skills/ (Skills 定义)
.rules/ (Rules 约束)
.specs/ (Spec 文档)
```

**分工**:
- **内置 Agent**: 高层协调、用户交互、决策
- **Python Agent**: 具体执行、工具调用、状态管理
- **自动化组件**: 提供底层能力

---

## 🚀 快速开始

### Step 1: 验证 Agent 已创建

```bash
ls -la .lingma/agents/spec-driven-core-agent.md
```

### Step 2: 测试 Agent

在对话中说：

```
使用 spec-driven-core-agent 检查当前状态
```

### Step 3: 开始使用

让 Agent 自主工作：

```
spec-driven-core-agent，继续执行下一个任务
```

---

## 📚 相关文档

- [Spec-Driven Development Skill](../skills/spec-driven-development/SKILL.md)
- [统一架构决策报告](../reports/unified-architecture-decision.md)
- [Phase 1 最终报告](../reports/phase1-final-report.md)
- [当前 Spec](../specs/current-spec.md)

---

## 💡 总结

**内置 Agent 的优势**:

✅ **原生集成** - 利用 Lingma 的原生 Agent 系统  
✅ **隔离上下文** - 不污染主对话  
✅ **专用提示** - 针对 Spec-Driven 优化  
✅ **工具控制** - 精细的权限管理  
✅ **自动委托** - AI 会自动使用合适的 Agent  
✅ **团队共享** - 项目级别，可版本控制  

**推荐使用场景**:

- 日常开发工作流
- Spec 管理和维护
- 自动化任务执行
- 跨会话连续性

**现在就试试吧！**

```
使用 spec-driven-core-agent 开始工作
```
