# Spec-Driven Development 系统架构说明

## 🎯 系统概述

这是一个完整的 **Spec-Driven Development** 自动化系统，通过 **Skill** 和 **Rule** 的联动，实现：

1. ✅ 每次会话自动检查 spec 状态
2. ✅ 智能识别用户意图
3. ✅ 优先处理需要澄清的问题
4. ✅ 基于 spec 自主开发
5. ✅ 跨会话持久化进度

---

## 🏗️ 架构组成

### 1. Skill 层（能力模块）

```
.lingma/skills/spec-driven-development/
├── SKILL.md                    # 核心工作流定义
├── QUICK_REFERENCE.md          # 快速参考
├── examples.md                 # 使用示例
├── INSTALLATION_GUIDE.md       # 安装指南
├── templates/
│   └── feature-spec.md         # Spec 模板
└── scripts/
    ├── init-spec.sh            # 初始化脚本
    └── check-spec-status.py    # 状态检查工具
```

**作用**: 提供可复用的开发能力和工具

### 2. Rule 层（行为规则）

```
.lingma/rules/
├── spec-session-start.md       # 会话启动规则 ⭐
└── README.md                   # 规则索引
```

**作用**: 控制 AI 的行为模式，确保每次都按规范执行

### 3. Data 层（数据持久化）

```
.lingma/specs/
├── current-spec.md             # 当前活跃 spec（不提交 Git）
├── spec-history/               # 历史归档（提交 Git）
└── templates/                  # 模板副本
```

**作用**: 存储开发规范和进度信息

### 4. Tools 层（辅助工具）

```
.lingma/scripts/
├── verify-setup.sh             # 配置验证工具
└── check-spec-status.py        # 状态检查（从 skills 复制）
```

**作用**: 提供命令行工具和自动化脚本

---

## 🔄 工作流程

### 会话启动流程

```
用户打开新会话
       │
       ▼
┌─────────────────────┐
│ Rule: 触发          │ ← spec-session-start.md
│ spec-session-start  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Step 1: 检查        │
│ current-spec.md     │
└────────┬────────────┘
         │
         ├─ 存在 ──→ 读取并解析
         │           - 状态
         │           - 进度
         │           - 待澄清问题
         │
         └─ 不存在 ──→ spec_status = "none"
                     │
                     ▼
┌─────────────────────────────┐
│ Step 2: 分析用户第一条消息   │
│ - 意图识别                   │
│ - 关键词提取                 │
│ - 上下文关联                 │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Step 3: 生成综合响应         │
│                             │
│ IF 有活跃 spec:             │
│   - 显示进度                │
│   - 列出待完成任务          │
│   - 关联用户消息            │
│   - 提出澄清问题（如有）     │
│   - 建议下一步              │
│                             │
│ ELSE:                       │
│   - 正常响应用户            │
│   - 提示可以创建 spec       │
└────────┬────────────────────┘
         │
         ▼
    返回给用户
```

### 开发执行流程

```
用户确认 spec 或说"继续"
       │
       ▼
┌─────────────────────┐
│ Skill: 加载         │
│ spec-driven-dev     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 读取任务列表         │
│ 找到下一个未完成任务  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 自主执行任务         │
│ - 实现代码          │
│ - 编写测试          │
│ - 运行验证          │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 更新 spec           │
│ - 标记任务完成      │
│ - 添加实施笔记      │
│ - 更新进度          │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 检查是否有           │
│ 需要澄清的问题       │
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    ▼         ▼
  询问用户  继续下一个任务
    │
    ▼
  等待回复
```

---

## 📋 Rule 详细说明

### spec-session-start.md 规则

#### 触发条件
- **Always On**: 每次会话的第一次回复前

#### 执行步骤

**Step 1: 检测 Spec 状态**
```python
if exists(".lingma/specs/current-spec.md"):
    spec = parse_spec()
    status = spec.status
    progress = calculate_progress(spec)
    clarifications = find_clarifications(spec)
else:
    status = "no_active_spec"
```

**Step 2: 分析用户意图**
```python
user_message = get_first_user_message()
intent = classify_intent(user_message)
# 意图类型: new_feature, continue, change_request, query, other
```

**Step 3: 选择响应模板**
```python
if status == "in-progress":
    template = TEMPLATE_IN_PROGRESS
elif status == "draft":
    template = TEMPLATE_DRAFT
elif status == "completed":
    template = TEMPLATE_COMPLETED
else:
    template = TEMPLATE_NO_SPEC
```

**Step 4: 生成响应**
```markdown
响应 = 模板填充(
    spec_info,
    user_message_summary,
    clarifications,
    next_steps
)
```

**Step 5: 记录日志**
```python
log_session_start({
    "timestamp": now(),
    "user_message": user_message,
    "spec_status": status,
    "progress": progress,
    "clarifications_count": len(clarifications)
})
```

#### 关键特性

1. **透明性**: 始终显示当前状态和进度
2. **关联性**: 将用户消息与当前 spec 关联
3. **优先级**: 澄清问题优先于开发
4. **指导性**: 提供明确的下一步建议

---

## 💡 使用场景

### 场景 1: 继续中断的开发

**用户**: （打开新会话）"继续"

**系统行为**:
1. Rule 检测到 `current-spec.md` 存在
2. 读取 spec，发现状态是 `in-progress`
3. 计算进度：40% (4/10 任务)
4. 生成响应，显示：
   - 当前进度
   - 已完成任务
   - 待完成任务
   - 最近进展
5. 确认从 Task-005 继续

**用户体验**: 无缝恢复，无需重复说明背景

### 场景 2: 新功能请求

**用户**: "我想添加导出报告功能"

**系统行为**:
1. Rule 检测到没有活跃 spec
2. 识别用户意图为 `new_feature`
3. 生成响应：
   - 确认收到需求
   - 提出澄清问题（格式、内容、触发方式等）
   - 说明 spec 创建流程
4. 等待用户回答

**用户体验**: 结构化的需求收集，避免遗漏

### 场景 3: 需求变更

**用户**: "阈值告警应该支持分级"

**系统行为**:
1. Rule 检测到有活跃 spec
2. 评估变更影响：
   - 受影响的需求
   - 受影响的任务
   - 额外工作量
3. 生成响应：
   - 显示当前进度
   - 列出变更影响
   - 提出澄清问题
   - 给出选项（立即更新/稍后考虑/重新规划）

**用户体验**: 清晰了解变更影响，做出明智决策

---

## 🔧 配置和定制

### 修改响应模板

编辑 `.lingma/rules/spec-session-start.md` 中的响应模板部分。

### 添加新的意图类型

在 Step 2 的意图分类中添加新的类型和处理逻辑。

### 自定义澄清问题

根据项目特点，调整需要澄清的问题列表。

### 调整进度显示

修改 `check-spec-status.py` 中的进度计算和显示逻辑。

---

## 📊 监控和度量

### 关键指标

| 指标 | 说明 | 目标 |
|------|------|------|
| Spec 完成率 | completed / total | > 90% |
| 平均会话恢复时间 | 从会话开始到继续开发 | < 1 min |
| 澄清问题数量 | 每个 spec 的平均澄清数 | < 5 |
| 用户交互频率 | 每小时的交互次数 | 最小化 |
| Spec 更新频率 | 每天 spec 更新次数 | 实时 |

### 日志位置

```
.lingma/specs/current-spec.md
  └─ 实施笔记部分
     └─ 会话启动日志
```

---

## 🚀 最佳实践

### 1. 保持 Spec 简洁
- 关注 WHAT 和 WHY
- 让 AI 决定 HOW
- 避免过度详细

### 2. 及时更新
- 每个任务完成后更新 spec
- 添加详细的实施笔记
- 记录关键决策和理由

### 3. 有效澄清
- 一次性提出所有问题
- 使用结构化选项
- 说明为什么需要澄清

### 4. 定期归档
- 完成后立即归档
- 保持工作区整洁
- 保留完整历史

---

## 🐛 故障排除

### 问题 1: Rule 未触发

**症状**: 新会话开始时 AI 没有检查 spec 状态

**排查**:
1. 检查文件是否存在: `ls .lingma/rules/spec-session-start.md`
2. 检查文件格式是否正确（Markdown）
3. 确认文件名拼写正确

**解决**: 重新创建或修复规则文件

### 问题 2: Spec 解析失败

**症状**: AI 报告无法读取 spec

**排查**:
1. 检查文件编码（应为 UTF-8）
2. 检查 Markdown 格式是否正确
3. 运行验证脚本: `bash .lingma/scripts/verify-setup.sh`

**解决**: 修复文件格式或从历史恢复

### 问题 3: 进度不同步

**症状**: Spec 显示的状态与实际代码不符

**排查**:
1. 检查 git log 了解最近的变更
2. 对比 spec 任务列表和实际完成情况
3. 查看实施笔记是否有遗漏

**解决**: 
- 告诉 AI: "请同步 spec 与当前实现"
- AI 会自动检测差异并更新

---

## 📚 相关文档

- **[SKILL.md](../skills/spec-driven-development/SKILL.md)** - Skill 详细定义
- **[spec-session-start.md](spec-session-start.md)** - Rule 完整说明
- **[INSTALLATION_GUIDE.md](../skills/spec-driven-development/INSTALLATION_GUIDE.md)** - 安装和配置
- **[examples.md](../skills/spec-driven-development/examples.md)** - 使用示例

---

## 🎓 总结

这个系统通过 **Skill + Rule** 的联动实现了：

✅ **自动化**: 每次会话自动检查状态  
✅ **智能化**: 理解用户意图并关联上下文  
✅ **透明化**: 清晰展示进度和下一步  
✅ **高效化**: 减少不必要的交互  
✅ **持久化**: 跨会话保持连续性  

**核心价值**: 让 AI 成为真正的自主开发伙伴，而不仅仅是代码生成工具。
