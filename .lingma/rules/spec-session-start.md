---
trigger: always_on
---
# Spec-Driven Development 会话启动规则

## 规则说明

此规则确保每次会话开始时，AI 会自动：
1. 检查当前 spec 状态
2. 识别需要澄清的问题
3. 综合用户第一条消息和 spec 状态给出智能响应

## 触发条件

**Always On** - 每次会话的第一次回复前必须执行

## 执行流程

### Step 1: 检测 Spec 状态并执行环境自检

在响应用户第一条消息之前，必须执行以下检查：

```python
# 伪代码逻辑 - 增强版，包含自动化

# 1. 运行环境自检
run_environment_self_check()

# 2. 检查 spec 状态
IF .lingma/specs/current-spec.md exists:
    读取 spec 内容
    提取:
        - 状态 (draft/approved/in-progress/completed)
        - 进度 (已完成任务/总任务)
        - 待完成任务列表
        - [NEEDS CLARIFICATION] 标记
        - 最近的实施笔记
ELSE:
    spec_status = "no_active_spec"

# 3. 评估当前上下文风险
assessment = automation_engine.evaluate_operation({
    "type": "session_start",
    "details": {
        "has_spec": spec_status != "no_active_spec",
        "is_continuation": True
    }
})

# 4. 根据评估结果决定行为
IF assessment.strategy == "auto_execute":
    # 自动继续之前的工作
    auto_resume_from_spec()
ELIF assessment.strategy == "ask_user":
    # 询问用户如何继续
    present_options_to_user()
```

### Step 2: 分析用户意图

分析用户的第一条消息，判断意图类型：

| 意图类型 | 关键词示例 | 处理方式 |
|---------|-----------|---------|
| 新功能 | "添加"、"实现"、"新功能" | 创建新 spec |
| 继续开发 | "继续"、"下一步"、"进度" | 加载当前 spec |
| 需求变更 | "修改"、"调整"、"改变" | 评估变更影响 |
| 查询状态 | "状态"、"进度"、"如何" | 报告 spec 状态 |
| 其他 | - | 正常响应 + spec 提示 |

### Step 3: 生成综合响应

根据 spec 状态和用户意图，生成结构化响应：

#### 场景 A: 有活跃的 in-progress spec

**响应模板**:

```markdown
👋 欢迎回来！

📋 **检测到进行中的开发任务**

**Spec**: [spec 名称]
**状态**: ⏳ in-progress
**进度**: [X/Y 任务完成] ([百分比]%)

**已完成**:
✓ Task-001: [任务描述]
✓ Task-002: [任务描述]
...

**待完成**:
⏳ Task-003: [任务描述]
⏳ Task-004: [任务描述]
...

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

#### 场景 B: 有 draft 状态的 spec

**响应模板**:

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

#### 场景 C: 没有活跃 spec

**响应模板**:

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

#### 场景 D: Spec 已完成

**响应模板**:

```markdown
👋 您好！

✨ **上一个任务已完成**

**Spec**: [spec 名称]
**状态**: ✅ completed
**完成时间**: [日期]

**成果摘要**:
- 完成任务: X/Y
- 验收标准: 全部通过
- [其他关键指标]

---

💬 **关于您的消息**: "[用户消息摘要]"

[回应用户消息]

---

💡 **下一步建议**:
1. 归档已完成的 spec
2. 开始新的功能开发
3. 或者告诉我您的需求
```

### Step 4: 处理需要澄清的问题

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

### Step 5: 记录会话启动日志

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

## 具体实现规则

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

```
When responding to user's first message:
  1. Acknowledge their message
  2. Relate it to current spec context (if applicable)
  3. Explain how it affects the development plan
  4. Propose next steps
  
Example:
  User: "我想调整阈值告警的触发条件"
  
  Response:
    "我理解您想调整阈值告警的触发条件。
    
    📋 当前 Spec: 文件夹阈值告警功能
    状态: in-progress (40%)
    
    这个变更会影响：
    - FR-002: 实时监测（需要修改触发逻辑）
    - Task-003: 集成到文件监听服务（可能需要返工）
    
    ❓ 需要澄清：
    您希望如何调整触发条件？
    - A: 改为定时检查（如每小时）
    - B: 改为文件大小变化超过 X% 时
    - C: 其他方案
    
    请告诉我您的选择，我会更新 spec 并继续开发。"
```

### Rule 5: 新 Spec 创建流程

```
IF user requests a new feature AND no active spec OR user explicitly wants new spec:
  1. Acknowledge the request
  2. Identify missing information for spec creation
  3. Ask targeted questions (max 5 at a time)
  4. Create spec draft
  5. Present for review
  6. Wait for approval before starting development
  
Questions to ask (adapt based on context):
  - What is the core problem this feature solves?
  - Who are the primary users?
  - What are the must-have vs nice-to-have features?
  - Are there any technical constraints?
  - What is the expected timeline/priority?
```

### Rule 6: 自动化执行策略

```
FOR each operation during development:
  1. Use AutomationEngine.evaluate_operation() to assess
  2. Based on strategy:
     
     IF strategy == "auto_execute":
       - Execute immediately
       - Log operation
       - Continue to next task
     
     ELIF strategy == "execute_with_snapshot":
       - Create snapshot using SnapshotManager
       - Execute operation
       - Verify result
       - IF failed: rollback automatically
       - Log operation with snapshot ID
     
     ELIF strategy == "ask_user":
       - Present options to user
       - Explain risks and benefits
       - Wait for user decision
       - Execute based on decision
       - Log user's choice
     
     ELIF strategy == "require_explicit_approval":
       - Detailed risk explanation
       - Require explicit "yes" confirmation
       - Create snapshot before execution
       - Execute only after confirmation
       - Log with high priority flag

NEVER execute high-risk operations without explicit user approval.
ALWAYS create snapshots before modifying production code.
ALWAYS log all decisions and outcomes.
```

---

## 异常处理

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

## 示例响应

### 示例 1: 继续开发场景

**用户第一条消息**: "继续"

**AI 响应**:

```markdown
👋 欢迎回来！

📋 **检测到进行中的开发任务**

**Spec**: 文件夹大小阈值告警功能
**状态**: ⏳ in-progress
**进度**: ████████░░░░░░░░░░ 40.0% (4/10 任务)

**已完成**:
✓ Task-001: 扩展数据库 schema
✓ Task-002: 实现阈值检查逻辑
✓ Task-003: 集成到文件监听服务
✓ Task-004: 编写单元测试

**待完成**:
⏳ Task-005: 创建阈值配置 UI 组件 (预计: 2h)
⏳ Task-006: 实现告警通知组件 (预计: 2h)
⏳ Task-007: 添加告警历史页面 (预计: 2h)
⏳ Task-008: 端到端集成测试 (预计: 2h)
⏳ Task-009: 性能优化 (预计: 1h)
⏳ Task-010: 文档更新 (预计: 1h)

**最近进展**:
2024-01-15 16:45 - 完成 Task-004，单元测试覆盖率 92%

---

💬 **关于您的消息**: "继续"

好的，我将从 Task-005 继续执行。

---

❓ **需要澄清的问题**: 无

---

💡 **下一步**:
开始实现 Task-005: 创建阈值配置 UI 组件

我将：
1. 创建 ThresholdConfig 组件
2. 添加表单验证
3. 集成到 WatchedFoldersList
4. 编写组件测试

预计耗时: 2 小时

是否开始？(或者告诉我您的其他想法)
```

### 示例 2: 新功能请求场景

**用户第一条消息**: "我想添加一个导出扫描报告的功能"

**AI 响应**:

```markdown
👋 您好！

📋 **当前没有活跃的开发任务**

---

💬 **关于您的消息**: "我想添加一个导出扫描报告的功能"

这是一个很好的功能！让我帮您创建详细的 spec。

---

❓ **需要澄清的问题**

为了创建准确的 spec，我需要了解：

**问题 1** (核心功能): 导出报告的格式？
- A: PDF 格式（专业，适合打印）
- B: Excel/CSV 格式（便于数据分析）
- C: HTML 格式（易于分享和查看）
- D: 全部支持

**问题 2** (报告内容): 报告应包含哪些信息？
- A: 仅汇总统计（总大小、文件数等）
- B: 详细文件列表
- C: 文件类型分布图表
- D: 历史对比数据
- E: 自定义选择

**问题 3** (触发方式): 如何触发导出？
- A: 手动点击导出按钮
- B: 定时自动生成
- C: 扫描完成后自动导出
- D: API 调用

**问题 4** (优先级): 这个功能的优先级？
- A: P0 - 紧急（本周内完成）
- B: P1 - 高（本月内完成）
- C: P2 - 中（下个迭代）
- D: P3 - 低（有空再做）

**问题 5** (存储位置): 导出文件保存到哪里？
- A: 用户选择目录
- B: 固定的导出文件夹
- C: 系统临时目录
- D: 云存储

---

💡 **建议**:
请回答以上问题（可以直接回复选项字母，如 "1A, 2B, 3A, 4B, 5A"），
或者告诉我您的具体需求，我会据此创建完整的 spec 文档。

创建 spec 后，我将基于 spec 自主开发，仅在需要澄清时与您交互。
```

### 示例 3: 需求变更场景

**用户第一条消息**: "我觉得阈值告警应该支持分级，比如警告、严重、危急"

**AI 响应**:

```markdown
👋 您好！

📋 **检测到进行中的开发任务**

**Spec**: 文件夹大小阈值告警功能
**状态**: ⏳ in-progress
**进度**: 40.0% (4/10 任务)

---

💬 **关于您的消息**: "我觉得阈值告警应该支持分级，比如警告、严重、危急"

这是一个很好的改进建议！这会让告警系统更加实用。

---

⚠️ **变更影响评估**

这个变更会影响：

**受影响的需求**:
- FR-001: 阈值配置 → 需要支持多级阈值
- FR-003: 告警通知 → 需要区分告警级别

**受影响的任务**:
- Task-002: 实现阈值检查逻辑（需要返工）
- Task-005: 创建阈值配置 UI（需要重新设计）
- Task-006: 实现告警通知组件（需要添加级别显示）

**新增任务**:
- Task-011: 实现告警级别定义（预计: 1h）
- Task-012: 添加分级告警测试（预计: 1h）

**额外工作量**: 约 +4 小时
**对进度的影响**: 从 16h → 20h

---

❓ **需要澄清的问题**

**问题 1**: 告警级别的阈值如何设置？
- A: 固定比例（如 80%/90%/95%）
- B: 用户自定义每级阈值
- C: 预设模板 + 自定义

**问题 2**: 不同级别的告警方式是否不同？
- A: 是，危急级别发送系统通知，警告仅 UI 提示
- B: 否，所有级别使用相同通知方式
- C: 用户可配置每级的通知方式

**问题 3**: 是否需要告警升级机制？
- A: 是，如果警告持续 N 小时未处理，升级为严重
- B: 否，级别固定不变

---

💡 **建议下一步**:

请选择：
1. **立即更新 spec** - 回答上述问题，我更新 spec 后继续开发
2. **完成当前任务后再考虑** - 先完成现有 spec，之后作为增强功能
3. **暂停并重新规划** - 停止当前开发，重新设计整个告警系统

请告诉我您的选择，或者直接回答澄清问题。
```

---

## 总结

此规则确保：

✅ **每次会话开始时自动检查 spec 状态**  
✅ **智能识别用户意图并关联当前上下文**  
✅ **优先处理需要澄清的问题**  
✅ **提供透明的进度信息**  
✅ **给出明确的下一步建议**  
✅ **保持 spec 与开发的同步**  

通过这种方式，用户可以：
- 随时中断和恢复开发
- 清楚地了解项目状态
- 只在必要时参与决策
- 享受高效的自主开发体验
