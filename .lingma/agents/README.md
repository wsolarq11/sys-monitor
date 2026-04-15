# Agents Registry

本目录包含自定义 Agent 定义，遵循 [Anthropic Agent Skills](https://www.agentskills.io) 和 [Cursor Subagents](https://cursor.com/cn/blog/agent-best-practices) 最佳实践。

## 🤖 Agent 列表

### 1. [spec-driven-core-agent.md](spec-driven-core-agent.md) ⭐ 核心 Agent
- **类型**: Core Agent（核心代理）
- **能力**:
  - Spec 生命周期管理
  - 自动化引擎协调
  - 规则强制执行
  - 自主任务执行
- **触发方式**: 
  - 用户请求 Spec-Driven 开发
  - 检测到 `current-spec.md` 存在
  - 手动调用 `/spec` 命令
- **权限级别**: High（可修改代码、运行测试、提交 Git）
- **状态**: ✅ Active

### 2. [test-runner-agent.md](test-runner-agent.md) 🧪 测试执行 Agent
- **类型**: Specialized Agent（专业代理）
- **能力**:
  - 自动执行单元测试、集成测试、E2E 测试
  - 分析测试结果并分类失败原因
  - 提供可执行的修复建议
  - 生成详细的测试报告
  - 维护测试基线和回归检测
- **触发方式**: 
  - 用户请求运行测试
  - CI/CD 流水线触发
  - 代码变更后自动执行
- **权限级别**: Medium（可运行测试、读取日志、不可修改业务代码）
- **状态**: ✅ Active

### 3. [code-review-agent.md](code-review-agent.md) 🔍 代码审查 Agent
- **类型**: Specialized Agent（专业代理）
- **能力**:
  - 自动审查 Pull Request / 代码变更
  - 检测代码质量问题（bug、安全漏洞、性能问题）
  - 检查编码规范和最佳实践
  - 提供可操作的改进建议
  - 生成结构化的审查报告
- **触发方式**: 
  - PR 创建时自动触发
  - 用户手动请求审查
  - 定期代码质量扫描
- **权限级别**: Low（仅读取代码、生成报告、不可修改代码）
- **状态**: ✅ Active

## 🏗️ 架构设计

### Agent 层级
```
Core Agents (spec-driven-core-agent)
    ↓
Specialized Agents (未来扩展)
    ↓
Task-Specific Agents (按需创建)
```

### 协作模式
- **单一职责**: 每个 Agent 专注特定领域
- **渐进式披露**: 仅在需要时加载 Agent 上下文
- **上下文隔离**: 不同 Agent 之间不共享私有状态
- **协调机制**: 通过 Spec 文件进行通信

## 📝 Agent 定义规范

### 文件命名
- 使用 `kebab-case` 格式
- 包含角色和用途
- 示例: `spec-driven-core-agent.md`, `test-runner-agent.md`

### 必需章节
```markdown
# Agent 名称

## 角色定义
你是谁，你的核心职责

## 能力范围
你能做什么，不能做什么

## 工作流程
标准操作步骤

## 决策框架
如何做选择，优先级判断

## 工具使用
可用的工具和 MCP 服务器

## 输出格式
如何呈现结果

## 错误处理
遇到问题时的应对策略
```

### 避免的设计
- ❌ 职责过于宽泛（"全能助手"）
- ❌ 与其他 Agent 重叠
- ❌ 缺少明确的边界
- ✅ 专注、清晰、可组合

## 🔧 创建新 Agent

### 步骤 1: 需求分析
- 是否有明确的职责边界？
- 是否需要独立的上下文？
- 是否能提高专业化程度？

### 步骤 2: 设计 Agent
1. 定义角色和能力
2. 确定工作流程
3. 列出所需工具
4. 设计输出格式

### 步骤 3: 实现
```bash
# 创建 Agent 文件
touch .lingma/agents/new-agent-name.md

# 基于模板填充
# 参考 spec-driven-core-agent.md 的结构
```

### 步骤 4: 测试
- 在隔离环境中测试
- 验证边界条件
- 确保不与其他 Agent 冲突

### 步骤 5: 注册
- 更新本 README.md
- 添加到相关文档的引用
- 通知团队成员

## 📊 Agent 统计

| 类型 | 数量 | 状态 |
|------|------|------|
| Core Agents | 1 | ✅ Active |
| Specialized Agents | 2 | ✅ Active |
| Task-Specific Agents | 0 | ⏳ On-demand |
| **总计** | **3** | **✅ Operational** |

## 🔗 相关资源

- [Anthropic Agent Skills 规范](https://www.agentskills.io)
- [Cursor Subagents 最佳实践](https://cursor.com/cn/blog/agent-best-practices)
- [Spec-Driven Development Skill](../skills/spec-driven-development/SKILL.md)
- [Rules 注册表](../rules/README.md)

## 🚀 未来规划

### Phase 1: 基础 Agent（已完成）
- [x] Spec-Driven Core Agent

### Phase 2: 专业 Agent（已完成 ✅）
- [x] Test Runner Agent（自动化测试执行）
- [x] Code Review Agent（代码审查）
- [ ] Documentation Agent（文档生成）

### Phase 3: 协作 Agent（远期）
- [ ] Multi-Agent Orchestration（多 Agent 协调）
- [ ] Agent Communication Protocol（Agent 通信协议）

## 📅 更新历史

- **2026-04-15**: 创建 Agents Registry，统一管理 Agent 定义
- 遵循渐进式披露原则，支持动态加载
