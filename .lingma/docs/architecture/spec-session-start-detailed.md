# Spec Session Start - 详细实现指南

**版本**: v1.0  
**最后更新**: 2026-04-15  
**关联 Rule**: `.lingma/rules/spec-session-start.md`

---

## 📋 完整执行流程

### Step 1: 检测 Spec 状态并执行环境自检

（详见精简版 Rule）

### Step 2: 分析用户意图

| 意图类型 | 关键词示例 | 处理方式 |
|---------|-----------|---------|
| 新功能 | "添加"、"实现"、"新功能" | 创建新 spec |
| 继续开发 | "继续"、"下一步"、"进度" | 加载当前 spec |
| 需求变更 | "修改"、"调整"、"改变" | 评估变更影响 |
| 查询状态 | "状态"、"进度"、"如何" | 报告 spec 状态 |
| 其他 | - | 正常响应 + spec 提示 |

---

## 💬 响应模板（详细版）

### 场景 A: 有活跃的 in-progress spec

```markdown
👋 欢迎回来！

📋 **检测到进行中的开发任务**

**Spec**: [spec 名称]
**状态**: ⏳ in-progress
**进度**: [X/Y 任务完成] ([百分比]%)

**已完成**:
✓ Task-001: [任务描述]
✓ Task-002: [任务描述]

**待完成**:
⏳ Task-003: [任务描述]
⏳ Task-004: [任务描述]

**最近进展**:
[最近的实施笔记摘要]

---

💬 **关于您的消息**: "[用户消息摘要]"

[根据用户意图回应]

---

❓ **需要澄清的问题**:
[如果有 NEEDS CLARIFICATION 标记，列出问题]

---

💡 **建议下一步**:
[基于 spec 状态的行动建议]
```

### 场景 B: 有 draft 状态的 spec

```markdown
👋 您好！

📝 **检测到待确认的 Spec**

**Spec**: [spec 名称]
**状态**: 📝 draft (待审批)

**需要您确认的内容**:
1. [待确认点 1]
2. [待确认点 2]

---

💬 **关于您的消息**: "[用户消息摘要]"

[回应用户消息]

---

❓ **需要补充的信息**:
[列出创建完整 spec 所需的信息]

请选择：
- 回答上述问题以完善 spec
- 或者告诉我新的需求
```

### 场景 C: 没有活跃 spec

```markdown
👋 您好！我是您的 AI 开发助手。

📋 **当前没有活跃的开发任务**

您可以：
1. 🆕 开始新功能 - 告诉我您的需求
2. 📖 查看历史 spec - 运行 `ls .lingma/specs/spec-history/`
3. 🔧 其他帮助 - 直接提问

---

💬 **关于您的消息**: "[用户消息摘要]"

[正常回应用户的消息]

---

💡 **提示**: 
如果您要开始新功能，我可以帮您创建详细的 spec 文档，
然后基于 spec 自主开发，仅在需要澄清时与您交互。
```

### 场景 D: Spec 已完成

```markdown
👋 您好！

✨ **上一个任务已完成**

**Spec**: [spec 名称]
**状态**: ✅ completed
**完成时间**: [日期]

**成果摘要**:
- 完成任务: X/Y
- 验收标准: 全部通过

---

💬 **关于您的消息**: "[用户消息摘要]"

[回应用户消息]

---

💡 **下一步建议**:
1. 归档已完成的 spec
2. 开始新的功能开发
3. 或者告诉我您的需求
```

---

## ❓ 处理需要澄清的问题

如果 spec 中有 `[NEEDS CLARIFICATION]` 标记：

1. **提取所有未澄清的问题**
2. **优先级排序**（阻塞性问题的优先）
3. **使用 AskUserQuestion 工具**（如果可用）或结构化提问

**提问格式**:

```markdown
❓ **需要您的澄清**

在继续之前，我需要了解以下几点：

**问题 1** (阻塞性): [问题描述]
选项：
- A: [选项 A]
- B: [选项 B]
- C: [选项 C]
- 其他: [自定义]

**问题 2** (重要): [问题描述]
...

请回答这些问题，或者告诉我"先跳过，稍后决定"。
```

---

## 📝 记录会话启动日志

在 `.lingma/specs/current-spec.md` 的实施笔记部分添加：

```markdown
### 会话启动 - {{DATE}} {{TIME}}

**用户消息**: "{{user_first_message}}"
**Spec 状态**: {{spec_status}}
**进度**: {{progress}}
**需要澄清**: {{clarification_count}} 个问题
**响应策略**: {{response_strategy}}
```

---

## 🎯 具体实现规则

### Rule 1: 强制状态检查与自动化评估

```
BEFORE responding to the first user message in a session:
  1. Run environment self-check (auto-fix minor issues)
  2. Check if .lingma/specs/current-spec.md exists
  3. If exists, read and parse the spec
  4. Extract status, progress, and clarification needs
  5. Use AutomationEngine to evaluate the context
  6. Analyze user's intent from their first message
  7. Generate response based on:
     - Spec status
     - Automation assessment
     - User intent
  8. Log the decision using OperationLogger
```

### Rule 2: 澄清问题优先

```
IF spec contains [NEEDS CLARIFICATION] markers:
  - MUST list all unresolved questions
  - MUST prioritize blocking questions
  - SHOULD use AskUserQuestion tool if available
  - MUST NOT proceed with implementation until clarified
  
ELSE IF user's request is ambiguous:
  - MUST ask clarifying questions
  - SHOULD provide options when possible
  - MUST explain why clarification is needed
```

### Rule 3: 进度透明化

```
ALWAYS include in the first response:
  - Current spec status (if any)
  - Progress percentage
  - Next immediate action
  - Any blockers or decisions needed
  
NEVER assume the user knows the current state.
ALWAYS make it explicit.
```

### Rule 4: 上下文关联

当响应用户的第一条消息时：
1. 确认他们的消息
2. 将其与当前 spec 上下文关联（如适用）
3. 解释它如何影响开发计划
4. 提出下一步建议

### Rule 5: 新 Spec 创建流程

如果用户请求新功能且没有活跃 spec：
1. 确认请求
2. 识别创建 spec 所需的缺失信息
3. 提出有针对性的问题（最多 5 个）
4. 创建 spec 草稿
5. 提交审查
6. 等待批准后开始开发

### Rule 6: 自动化执行策略

对于开发过程中的每个操作：
1. 使用 AutomationEngine.evaluate_operation() 评估
2. 根据策略执行：
   - auto_execute: 立即执行
   - execute_with_snapshot: 创建快照后执行
   - ask_user: 向用户呈现选项
   - require_explicit_approval: 需要明确批准

---

## ⚠️ 异常处理

### 情况 1: Spec 文件损坏

```
IF cannot parse current-spec.md:
  - Inform user about the issue
  - Suggest restoring from spec-history
  - Offer to create a new spec
  - DO NOT attempt to auto-fix without user confirmation
```

### 情况 2: Spec 与代码严重不同步

```
IF detect significant divergence between spec and codebase:
  - Alert user: "⚠️ 检测到 spec 与代码实现存在较大差异"
  - List specific discrepancies
  - Offer options:
    A: Update spec to match code
    B: Revert code to match spec
    C: Create new spec for current state
  - Wait for user decision
```

### 情况 3: 多个活跃 Spec

```
IF multiple spec files found (should not happen):
  - Warn user about the anomaly
  - List all found specs with their statuses
  - Ask user to specify which one to work on
  - Suggest archiving old specs
```

---

## 📚 相关资源

- [精简版 Rule](../../rules/spec-session-start.md)
- [Spec-Driven Development Skill](../../skills/spec-driven-development/SKILL.md)
- [验证指南](../guides/verification-guide.md)

---

**注意**: 此文档包含详细的实现指南和示例，不应放入 Rule 文件中。Rule 文件应保持简洁（≤3KB），仅包含核心指令和引用链接。
