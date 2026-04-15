---
name: spec-driven-development
description: Spec-driven development workflow that maintains specification documents across sessions, enables autonomous development based on specs, and only interacts with users when requirements need clarification. Use when starting new features, refactoring, or when the user mentions specs, specifications, or spec-driven development.
---

# Spec-Driven Development Workflow

**角色**: Spec驱动开发工作流管理器  
**职责**: 维护Spec文档、支持跨会话自主开发、仅在需求不明确时交互

## 核心原则

1. **Spec即真相** - 所有开发决策基于spec文档
2. **跨会话持久化** - Spec在会话间保持不变和同步
3. **自主开发** - 基于清晰的spec自主执行开发任务
4. **最小交互** - 仅在需求不明确时与用户确认
5. **职责边界** - 专注Spec管理，Memory操作委托给memory-management Skill

## Spec文件结构

```
.lingma/specs/
├── current-spec.md          # 当前活跃的开发规范
├── spec-history/            # 历史spec版本
└── templates/               # Spec模板
    ├── feature-spec.md
    ├── refactor-spec.md
    └── bugfix-spec.md
```

## 工作流程

1. **Spec检查** - 读取current-spec.md、分析状态
2. **意图识别** - 新功能/继续开发/需求变更/查询状态
3. **任务分解** - 将Spec拆分为可执行任务列表
4. **自主执行** - 按优先级执行、更新进度
5. **状态同步** - 记录实施笔记、标记完成

## 详细实现

完整指南见：[spec-driven-development-detailed.md](../../docs/skills/spec-driven-development-detailed.md)

## 量化标准

- Skill 文件 ≤10KB（当前需优化）
- 详细内容移至 docs/skills/
- 仅保留核心原则、文件结构、工作流概要
