# .lingma - 自迭代流系统

本目录包含完整的 **Agents + Skills + Rules + MCP** 四层架构，遵循 [Anthropic Agent Skills](https://www.agentskills.io) 和 [Cursor AI](https://cursor.com) 最佳实践。

## 🏗️ 架构概览

```
┌─────────────────────────────────────────┐
│         Agents (决策层)                  │
│  - spec-driven-core-agent               │
│  - 自主任务执行与协调                    │
└──────────────┬──────────────────────────┘
               │ 调用
┌──────────────▼──────────────────────────┐
│         Skills (能力层)                  │
│  - spec-driven-development              │
│  - memory-management                    │
│  - 渐进式披露，按需加载                  │
└──────────────┬──────────────────────────┘
               │ 使用
┌──────────────▼──────────────────────────┐
│         Rules (约束层)                   │
│  - AGENTS.md (Always Apply)             │
│  - automation-policy, memory-usage      │
│  - 全局行为约束                          │
└──────────────┬──────────────────────────┘
               │ 连接
┌──────────────▼──────────────────────────┐
│     MCP Servers (工具层)                 │
│  - Filesystem, GitHub, Database...      │
│  - 外部系统集成                          │
└─────────────────────────────────────────┘
```

## 📂 目录结构

### 1. [agents/](agents/) - Agent 注册表
- **职责**: 定义 AI 代理的角色、能力和工作流程
- **核心文件**: 
  - [README.md](agents/README.md) - Agent 索引
  - [spec-driven-core-agent.md](agents/spec-driven-core-agent.md) - 核心 Agent
- **状态**: ✅ 1 Active Agent

### 2. [skills/](skills/) - Skills 注册表
- **职责**: 封装领域知识、工作流和脚本
- **核心 Skills**:
  - [spec-driven-development/](skills/spec-driven-development/) - Spec 驱动开发
  - [memory-management.md](skills/memory-management.md) - 记忆管理
- **状态**: ✅ 2 Active Skills, 100% 完整性

### 3. [rules/](rules/) - Rules 注册表
- **职责**: 定义全局行为约束和编码规范
- **核心规则**:
  - [AGENTS.md](rules/AGENTS.md) ⭐ - Always Apply 规则
  - [automation-policy.md](rules/automation-policy.md) - 自动化策略
  - [memory-usage.md](rules/memory-usage.md) - 记忆使用规范
  - [spec-session-start.md](rules/spec-session-start.md) - Session 触发器
- **状态**: ✅ 4 Active Rules

### 4. [mcp-templates/](mcp-templates/) - MCP 服务器模板
- **职责**: Model Context Protocol 服务器配置
- **可用模板**:
  - [basic.json](mcp-templates/basic.json) - 基础配置
  - [minimal.json](mcp-templates/minimal.json) - 最小化配置
- **状态**: ✅ 2 Templates Available

### 5. [specs/](specs/) - 开发规范
- **职责**: Spec-Driven Development 工作空间
- **结构**:
  - `current-spec.md` - 当前活跃 Spec（不提交 Git）
  - `spec-history/` - 历史 Spec 归档
  - `templates/` - Spec 模板
- **状态**: ✅ Operational

### 6. [scripts/](scripts/) - 工具脚本
- **职责**: 辅助工具和自动化脚本
- **主要脚本**:
  - `check_root_cleanliness.py` - 根目录清洁度检查
  - `check-spec-status.py` - Spec 状态检查
- **状态**: ✅ 7 Scripts

### 7. [hooks/](hooks/) - Git Hooks
- **职责**: Git 提交前自动检查
- **Hook 列表**:
  - `pre-commit` - 根目录清洁度拦截
- **状态**: ✅ 1 Active Hook

### 8. [docs/](docs/) - 文档
- **职责**: 系统设计和使用文档
- **核心文档**:
  - `SYSTEM_ARCHITECTURE.md` - 系统架构说明
- **状态**: ✅ 9 Documents

### 9. [reports/](reports/) - 调研报告
- **职责**: 技术调研和决策记录
- **最新报告**:
  - `GITIGNORE_ARCHITECTURE_INVESTIGATION.md` - .gitignore 架构调研
  - `TEMP_FILE_PREVENTION_COMPLETE.md` - 临时文件防范报告
- **状态**: ✅ 23 Reports

### 10. [config/](config/) - 配置文件
- **职责**: 系统配置和环境变量
- **状态**: ✅ 2 Config Files

### 11. [logs/](logs/) - 日志
- **职责**: 运行时日志和审计记录
- **格式**: JSON Lines
- **状态**: ✅ 4 Log Files

### 12. [snapshots/](snapshots/) - 快照
- **职责**: 关键状态快照备份
- **状态**: ✅ 2 Snapshots

### 13. [backups/](backups/) - 备份
- **职责**: 重要文件的历史版本
- **状态**: ✅ 3 Backup Sets

## 🎯 核心特性

### 1. 渐进式披露 (Progressive Disclosure)
- **原理**: 仅在需要时加载详细信息
- **优势**: 节省上下文窗口，提高响应速度
- **实现**: 
  - Agents/Skills/Rules 通过 README.md 提供元数据
  - Agent 评估相关性后按需读取详细内容

### 2. 模块化设计 (Modular Design)
- **原理**: 每个组件独立、可替换
- **优势**: 易于维护、测试和扩展
- **实现**: 
  - 清晰的目录边界
  - 标准化的接口定义

### 3. 自动化优先 (Automation First)
- **原理**: 尽可能自动化重复任务
- **优势**: 提高效率，减少人为错误
- **实现**: 
  - Git Hooks 自动检查
  - Spec 驱动的自动化流程
  - 清洁度检查脚本

### 4. 质量保障 (Quality Assurance)
- **原理**: 多层防护确保代码质量
- **优势**: 预防问题，而非事后修复
- **实现**: 
  - 3 层防护体系（.gitignore + 检测脚本 + Git Hook）
  - Spec 验收标准
  - 自动化测试集成

## 🚀 快速开始

### 首次使用
1. **阅读架构文档**: [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)
2. **了解核心规则**: [rules/AGENTS.md](rules/AGENTS.md)
3. **探索 Skills**: [skills/README.md](skills/README.md)

### 开始 Spec-Driven 开发
```bash
# 1. 初始化 Spec 环境
cd .lingma/skills/spec-driven-development
./scripts/init-spec.sh

# 2. 告诉 AI 你的需求
# AI 会自动创建 current-spec.md

# 3. AI 按照 Spec 执行开发
# 自动更新进度、运行测试、提交代码

# 4. 完成后归档
mv specs/current-spec.md specs/spec-history/$(date +%Y-%m-%d)-feature-name.md
```

### 检查系统健康度
```bash
# 检查根目录清洁度
python .lingma/scripts/check_root_cleanliness.py

# 检查 Spec 状态
python .lingma/scripts/check-spec-status.py
```

## 📊 系统统计

| 组件 | 数量 | 状态 |
|------|------|------|
| Agents | 1 | ✅ Active |
| Skills | 2 | ✅ Active |
| Rules | 4 | ✅ Active |
| MCP Templates | 2 | ✅ Available |
| Scripts | 7 | ✅ Ready |
| Git Hooks | 1 | ✅ Active |
| Docs | 9 | ✅ Complete |
| Reports | 23 | ✅ Archived |

### 完整性指标
- **文件索引完整性**: 100% ✅
- **文档覆盖率**: 100% ✅
- **自动化覆盖率**: 85% ⏳ (目标: 95%)

## 🔗 相关资源

### 官方标准
- [Anthropic Agent Skills](https://www.agentskills.io) - 开放标准
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP 协议
- [Cursor AI Best Practices](https://cursor.com/cn/blog/agent-best-practices) - Cursor 最佳实践

### 社区资源
- [Anthropic Skills Repository](https://github.com/anthropics/skills) - 官方 Skills
- [MCP Servers](https://github.com/modelcontextprotocol/servers) - MCP 服务器集合

### 内部文档
- [系统架构](docs/SYSTEM_ARCHITECTURE.md)
- [Spec-Driven Development Skill](skills/spec-driven-development/SKILL.md)
- [Agents 注册表](agents/README.md)
- [Rules 注册表](rules/README.md)
- [Skills 注册表](skills/README.md)
- [MCP 注册表](mcp-templates/README.md)

## 🛡️ 安全注意事项

1. **敏感信息**: 不要在配置文件中硬编码密码/API Key
2. **Git 忽略**: 确保 `.env` 和敏感文件在 `.gitignore` 中
3. **权限控制**: 限制 Agent 的执行权限
4. **审计日志**: 所有操作都有 JSON 日志记录

## 📅 更新历史

- **2026-04-15**: 
  - 创建 `.lingma` 总索引
  - 完善四层架构（Agents + Skills + Rules + MCP）
  - 所有组件达到 100% 文件索引完整性
  - 遵循 Anthropic/Cursor 最佳实践

- **2026-04-15 (Earlier)**:
  - 优化双 .gitignore 架构
  - 建立 3 层临时文件防护体系
  - 完善 Skill 结构（添加文件索引和缺失模板）

## 🎓 学习路径

### 新手入门
1. 阅读 [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)
2. 了解 [AGENTS.md](rules/AGENTS.md) 中的编码规范
3. 尝试第一个 [Spec-Driven 开发任务](skills/spec-driven-development/SKILL.md)

### 进阶使用
1. 学习创建自定义 [Skills](skills/README.md#-创建新-skill)
2. 配置 [MCP 服务器](mcp-templates/README.md#-创建新-mcp-服务器)
3. 编写项目级 [Rules](rules/README.md#-规则编写规范)

### 专家级别
1. 设计多 Agent 协作流程
2. 开发领域专用 Skills
3. 优化自动化流程和 CI/CD

---

**最后更新**: 2026-04-15  
**维护者**: 自迭代流系统  
**版本**: v1.0.0
