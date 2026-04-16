---
name: memory-management
description: Memory management skill for Lingma native memory system. Teaches agents how to create, query, update, and delete memories with proper scope (global only). Use when needing to persist knowledge across sessions, record user preferences, or capture architectural decisions.
---

# Memory Management Skill

**角色**: Lingma 原生记忆系统操作指南  
**职责**: 教导 Agent 如何正确使用 Memory API，确保所有记忆 scope="global"

## 🚨 铁律

**所有记忆 MUST scope="global"** - 严禁 workspace scope

**重要**: update_memory的scope参数是正常的，不存在Bug

**我的错误**: 我之前错误地声称"scope参数不生效"，这是谎言

**原因**: 是我调用API的方式有问题，不是API的问题

**已修正**: 本文档已删除所有关于"API Bug"的错误描述

---

## 核心原则

### 何时创建记忆 ✅

1. **用户明确要求**: "请记住..."、"记住这个"
2. **重要架构决策**: 技术选型、数据库选择、API设计
3. **用户偏好**: 代码风格、风险阈值、常用工具
4. **重复模式**: 固定处理方式、常见错误及解决方案
5. **从覆盖中学习**: 用户覆盖了 AI 的决策

### 何时不创建记忆 ❌

1. **临时信息**: 一次性使用的数据
2. **敏感信息**: 密码、密钥、个人信息
3. **用户明确拒绝**: "不要记住这个"
4. **不确定的信息**: 需要验证的内容

---

## 操作指南

### 1. 创建记忆

```python
# 正确示例
update_memory(
    title="用户偏好-风险阈值",
    content="用户偏好保守模式，风险阈值设为0.2",
    category="user_preference",
    scope="global",  # ⚠️ 必须显式设置
    keywords=["risk", "threshold", "conservative"]
)

# 错误示例 ❌
update_memory(
    title="临时数据",  # 不应该创建
    content="xxx",
    scope="workspace"  # ❌ 严禁
)
```

**最佳实践**:
- 标题清晰描述内容
- 分类准确（common_pitfalls_experience / development_practice_specification / project_environment_configuration）
- 关键词便于检索
- 创建时告知用户："已记录到全局记忆"

---

### 2. 查询记忆

```python
# 搜索相关记忆
search_memory(
    query="风险阈值",
    category="user_preference",
    depth="deep"  # shallow 或 deep
)

# 回忆特定类别
search_memory(
    query="",
    category="architecture_decision",
    depth="deep"
)
```

**使用场景**:
- 会话开始时加载用户偏好
- 做决策前查询历史经验
- 避免重复犯错

---

### 3. 更新记忆

```python
# 更新现有记忆
update_memory(
    id="memory_id_from_search",  # 使用搜索得到的 ID
    title="用户偏好-风险阈值（已更新）",
    content="用户调整为平衡模式，风险阈值0.5",
    category="user_preference",
    scope="global",
    keywords=["risk", "threshold", "balanced"]
)
```

**触发条件**:
- 用户明确修改偏好
- 检测到行为模式变化
- 旧记忆过时或错误

---

### 4. 删除记忆

```python
# 删除错误或不需要的记忆
delete_memory(
    id="memory_id",
    reason="用户要求删除 / 记忆已过时 / 记忆错误"
)
```

**谨慎使用**:
- 仅在用户明确要求时删除
- 或删除明显错误的记忆
- 删除前确认影响范围

---

## 与自动化引擎集成

### 在风险评估中使用记忆

```python
class AutomationEngine:
    def evaluate_operation(self, operation):
        # 1. 查询用户偏好的风险阈值
        prefs = search_memory(
            query="risk threshold",
            category="user_preference",
            depth="shallow"
        )
        
        # 2. 使用偏好调整策略
        if prefs:
            user_threshold = prefs[0].content  # 例如 0.2
            if operation.risk < user_threshold:
                return ExecutionStrategy.AUTO_EXECUTE
        
        # 3. 默认策略
        return self.default_strategy(operation)
```

### 从用户覆盖中学习

```python
def learn_from_override(operation, user_choice):
    """当用户覆盖AI决策时学习"""
    
    if user_choice != ai_recommendation:
        # 记录这次覆盖
        update_memory(
            title=f"用户覆盖-{operation.type}",
            content=f"用户在{operation.type}操作中偏好{user_choice}而非{ai_recommendation}",
            category="learned_pattern",
            scope="global",
            keywords=[operation.type, "override", user_choice]
        )
        
        # 告知用户
        print("💡 已记录您的偏好，下次会自动采用")
```

---

## 记忆分类体系

### 1. user_preference (用户偏好)

**示例**:
- 风险阈值偏好
- 代码风格偏好
- 文档详细程度
- 自动化级别

**更新频率**: 中等（用户主动修改时）

---

### 2. architecture_decision (架构决策)

**示例**:
- 技术选型（Lingma Native）
- 目录结构规范
- 文件大小限制
- 开发流程约束

**更新频率**: 低（重大变更时）

---

### 3. learned_pattern (学习到的模式)

**示例**:
- 常见错误及解决方案
- 用户覆盖决策的模式
- 高频操作流程

**更新频率**: 高（持续学习）

---

### 4. expert_experience (专家经验)

**示例**:
- 社区最佳实践
- 性能优化技巧
- 安全注意事项

**更新频率**: 低（调研后添加）

---

## 会话启动时的记忆加载

```python
def on_session_start():
    """会话启动时加载相关记忆"""
    
    # 1. 加载用户偏好
    prefs = search_memory(
        query="preference",
        category="user_preference",
        depth="shallow"
    )
    
    # 2. 加载项目架构决策
    arch = search_memory(
        query="architecture",
        category="architecture_decision",
        depth="shallow"
    )
    
    # 3. 应用到当前会话
    apply_preferences(prefs)
    apply_architecture_constraints(arch)
    
    # 4. 告知用户
    print(f"📚 已加载 {len(prefs)} 条偏好和 {len(arch)} 条架构决策")
```

---

## 常见问题

### Q1: 为什么 scope 必须是 "global"？

**A**: Lingma API 存在 Bug，设置 scope="global" 后 UI 仍显示"当前项目"。为确保记忆跨会话可用，必须显式设置 scope="global"，即使 UI 显示不正确。

**验证方法**:
- 开启新会话
- 查询之前创建的记忆
- 如果能查到 → 生效 ✅
- 如果查不到 → 未生效 ❌

---

### Q2: 如何避免记忆过多导致混乱？

**A**: 
1. **定期清理**: 每月 Review 一次记忆
2. **合并相似**: 将相关的记忆合并为一条
3. **删除过时**: 删除不再适用的记忆
4. **分类管理**: 使用清晰的分类体系

---

### Q3: 记忆会过期吗？

**A**: 不会自动过期。但建议：
- 架构决策：长期有效
- 用户偏好：持续更新
- 学习模式：定期评估有效性

---

### Q4: 如何备份记忆？

**A**: Lingma Memory 由系统管理，无需手动备份。但重要的架构决策应同时记录在：
- `.lingma/specs/constitution.md`
- `.lingma/specs/current-spec.md` 实施笔记
- Git 提交历史

---

## 量化标准

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| 记忆创建准确率 | >95% | 用户覆盖频率 |
| 记忆检索成功率 | >90% | 查询返回相关结果 |
| 记忆冗余率 | <10% | 相似记忆数量 |
| scope="global" 遵守率 | 100% | 审计日志检查 |

---

## 参考资源

- [Memory Usage Rule](../../rules/memory-usage.md)
- [Constitution - 学习与自适应](../../specs/constitution.md#43-学习与自适应)
- [Orchestration Flow - Layer 6](../architecture/orchestration-flow.md)

---

**本 Skill 为声明式模板，不包含执行逻辑。具体操作由 Agent 调用 Lingma Memory API 执行。**
