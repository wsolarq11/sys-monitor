# Rules Registry

本目录包含项目级 AI 行为规则，遵循 [Cursor Rules](https://cursor.com/cn/blog/agent-best-practices) 和 [Anthropic Skills](https://www.agentskills.io) 最佳实践。

## 📋 规则列表

### 1. [AGENTS.md](AGENTS.md) ⭐ 核心规则
- **类型**: Always Apply（始终应用）
- **范围**: 全局
- **用途**: 
  - 编码规范与路径处理
  - 退出码标准
  - 审计日志格式
  - Shell 约束
  - RTK (Rust Token Killer) 命令前缀
- **优先级**: P0（最高）

### 2. [automation-policy.md](automation-policy.md)
- **类型**: Project Rule（项目规则）
- **范围**: 自动化任务
- **用途**:
  - 定义自动化边界
  - 风险评估流程
  - 回滚策略
  - 人工干预触发条件

### 3. [memory-usage.md](memory-usage.md)
- **类型**: Context Management（上下文管理）
- **范围**: 记忆系统
- **用途**:
  - 记忆分类标准
  - 存储策略
  - 检索优化
  - 冲突解决机制

### 4. [spec-session-start.md](spec-session-start.md)
- **类型**: Workflow Trigger（工作流触发器）
- **范围**: Spec-Driven Development
- **用途**:
  - Session 初始化检查清单
  - Spec 加载验证
  - 环境准备确认

## 🏗️ 架构设计

### 规则层级
```
Always Apply (AGENTS.md)
    ↓
Project Rules (automation-policy.md, memory-usage.md)
    ↓
Workflow Triggers (spec-session-start.md)
```

### 加载顺序
1. **启动时**: 加载 `AGENTS.md`（全局约束）
2. **任务识别**: 根据任务类型加载对应规则
3. **工作流触发**: 特定场景激活专用规则

## 📝 规则编写规范

### 文件命名
- 使用 `kebab-case` 格式
- 描述性强，一眼看出用途
- 示例: `automation-policy.md`, `memory-usage.md`

### 内容结构
```markdown
# 规则名称

## 适用范围
明确说明何时应用此规则

## 核心原则
3-5 条关键原则

## 具体规范
可执行的详细规则

## 示例
正例 vs 反例

## 例外情况
何时不适用此规则
```

### 避免的规则
- ❌ 过于宽泛（"写好代码"）
- ❌ 与其他规则冲突
- ❌ 无法自动化验证
- ✅ 具体、可执行、可测试

## 🔧 维护指南

### 添加新规则
1. 评估是否需要全局规则还是项目规则
2. 检查是否与现有规则冲突
3. 编写清晰的适用范围
4. 提供正反示例
5. 更新本索引文件

### 删除旧规则
1. 确认不再需要
2. 检查是否有依赖
3. 从本索引移除
4. 归档到 `.lingma/backups/rules/`

### 定期审查
- **频率**: 每月一次
- **检查项**:
  - 规则是否仍然相关
  - 是否有重复或冲突
  - 是否需要细化或简化

## 📊 规则统计

| 类别 | 数量 | 状态 |
|------|------|------|
| Always Apply | 1 | ✅ Active |
| Project Rules | 2 | ✅ Active |
| Workflow Triggers | 1 | ✅ Active |
| **总计** | **4** | **✅ All Active** |

## 🔗 相关资源

- [Cursor Rules 最佳实践](https://cursor.com/cn/blog/agent-best-practices)
- [Anthropic Skills 规范](https://www.agentskills.io)
- [Spec-Driven Development Skill](../skills/spec-driven-development/SKILL.md)
- [Agents 注册表](../agents/README.md)

## 📅 更新历史

- **2026-04-15**: 创建 Rules Registry，统一规则管理
- 遵循渐进式披露原则，仅列出必要信息
