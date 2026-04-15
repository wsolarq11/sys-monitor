# Skills Registry

本目录包含 Agent Skills，遵循 [Anthropic Agent Skills](https://www.agentskills.io) 开放标准。

## 🎯 Skills 列表

### 1. [spec-driven-development/](spec-driven-development/) ⭐ 核心 Skill
- **类型**: Workflow Skill（工作流技能）
- **能力**:
  - Spec 生命周期管理
  - 自动化开发流程
  - 质量保障机制
- **入口点**: [SKILL.md](spec-driven-development/SKILL.md)
- **触发方式**: 
  - 用户请求 Spec-Driven 开发
  - 检测到新功能需求
  - 手动调用 `/spec` 命令
- **状态**: ✅ Active & Complete

### 2. [memory-management.md](memory-management.md)
- **类型**: Utility Skill（工具技能）
- **能力**:
  - 记忆分类与存储
  - 上下文优化
  - 冲突解决
- **触发方式**: 
  - 自动（会话开始时）
  - 手动调用 `/memory` 命令
- **状态**: ✅ Active

## 🏗️ 架构设计

### Skills 在自迭代流中的角色
```
Agent (决策层)
    ↓
Skills (能力层) ← 本目录
    ↓
Tools/MCP (工具层)
    ↓
External Systems (外部系统)
```

### 渐进式披露机制
1. **启动时**: 仅加载 SKILL.md 元数据
2. **判断相关性**: Agent 评估是否需要此 Skill
3. **按需加载**: 读取详细指令和资源
4. **执行任务**: 按照 Skill 定义工作
5. **释放上下文**: 完成后卸载，节省 token

## 📝 Skill 编写规范

### 目录结构
```
skill-name/
├── SKILL.md              # 必需：主入口点
├── README.md             # 可选：详细说明
├── examples.md           # 可选：使用示例
├── scripts/              # 可选：辅助脚本
│   ├── init.sh
│   └── validate.py
├── templates/            # 可选：模板文件
│   └── template.md
└── resources/            # 可选：参考资源
    └── reference.pdf
```

### SKILL.md 必需章节
```markdown
# Skill 名称

## 概述
简要说明此 Skill 的用途和价值

## 何时使用
明确列出适用场景和触发条件

## 工作流程
详细的操作步骤

## 工具和资源
可用的脚本、模板、参考文档

## 输出格式
期望的交付物格式

## 最佳实践
成功的关键因素

## 常见问题
FAQ 和故障排除
```

### 质量检查清单
- [ ] SKILL.md 存在且格式正确
- [ ] 所有引用的文件都存在
- [ ] 提供了清晰的使用示例
- [ ] 包含了错误处理指南
- [ ] 文件索引完整性 100%

## 🔧 创建新 Skill

### 步骤 1: 需求分析
- 是否有明确的职责边界？
- 是否能提高专业化程度？
- 是否可复用？

### 步骤 2: 设计 Skill
1. 定义能力和范围
2. 设计工作流程
3. 准备必要的资源
4. 编写使用示例

### 步骤 3: 实现
```bash
# 创建目录结构
mkdir -p .lingma/skills/new-skill/{scripts,templates,resources}

# 创建 SKILL.md
touch .lingma/skills/new-skill/SKILL.md

# 基于 spec-driven-development 的结构填充
```

### 步骤 4: 测试
- 在隔离环境中测试
- 验证所有链接有效
- 确保工作流程顺畅

### 步骤 5: 注册
- 更新本 README.md
- 添加到相关文档的引用
- 通知团队成员

## 📊 Skills 统计

| 类型 | 数量 | 状态 |
|------|------|------|
| Workflow Skills | 1 | ✅ Active |
| Utility Skills | 1 | ✅ Active |
| Domain Skills | 0 | ⏳ Planned |
| **总计** | **2** | **✅ Operational** |

### 完整性指标
- **文件索引完整性**: 100% ✅
- **模板覆盖率**: 100% ✅
- **文档完整度**: 100% ✅

## 🔗 相关资源

- [Anthropic Agent Skills 官方标准](https://www.agentskills.io)
- [Skill Authoring Best Practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/authoring)
- [Community Skills Repository](https://github.com/anthropics/skills)
- [Spec-Driven Development Skill](spec-driven-development/SKILL.md)
- [Agents 注册表](../agents/README.md)
- [Rules 注册表](../rules/README.md)

## 🚀 未来规划

### Phase 1: 基础 Skills（已完成）
- [x] Spec-Driven Development
- [x] Memory Management

### Phase 2: 专业 Skills（计划中）
- [ ] Test Automation（测试自动化）
- [ ] Code Review（代码审查）
- [ ] Documentation Generation（文档生成）

### Phase 3: 领域 Skills（远期）
- [ ] Rust Best Practices
- [ ] React Performance Optimization
- [ ] Kubernetes Deployment

## 📅 更新历史

- **2026-04-15**: 创建 Skills Registry，统一 Skills 管理
- **2026-04-15**: spec-driven-development Skill 完整性达到 100%
- 遵循渐进式披露原则，支持动态加载
