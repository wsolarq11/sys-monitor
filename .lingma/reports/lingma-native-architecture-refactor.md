# 基于 Lingma 原生能力的架构重构方案

## 📊 调研总结

通过深入调研 Lingma 官方文档，我发现 Lingma 已经提供了**完整的原生能力栈**，我们之前的很多实现可以大幅简化甚至完全移除。

---

## 🎯 Lingma 原生能力清单

### 1. Agent（智能体）✅ 已使用
**能力**:
- 自主决策、环境感知、工具使用
- 工程级变更（多文件修改）
- 工程自动感知（框架、技术栈、错误信息）
- 终端命令执行（可配置自动执行列表）
- MCP 工具调用

**我们的使用**: ✅ 已创建 `spec-driven-core-agent`

### 2. Memory（记忆）⭐ 新发现
**能力**:
- **长期记忆** - 自动形成开发者个人、工程相关的记忆
- **主动记忆** - 用户直接输入"记住XXX"
- **自动记忆** - 对话过程中自动形成
- **记忆管理** - 查看、删除记忆
- **作用范围** - 全局（个人习惯）+ 工程级（项目相关）

**价值**: 
- ❌ **我们可以移除自定义的 context management**
- ✅ 直接使用 Lingma 的记忆系统

### 3. Context（上下文）⭐ 新发现
**能力**:
- **#file** - 选择单个或多个文件
- **#folder** - 选择目录
- **#codebase** - 整个项目语义检索
- **#codeChanges** - Git 暂存区变更
- **#gitCommit** - 历史 commit
- **#rule** - 引用规则
- **#teamDocs** - 企业知识库（Lingma IDE 不支持）
- **#image** - 图片上下文

**触发方式**:
- VS Code: 输入 `#` 或点击添加上下文按钮
- JetBrains/Lingma IDE: 输入 `@`

**价值**:
- ❌ **我们可以移除自定义的文件查找和上下文管理**
- ✅ 直接使用 Lingma 的上下文系统

### 4. Rules（规则）✅ 已使用
**能力**:
- **4种类型**:
  1. **Manual** - 手动引入 (`#rule`)
  2. **Model Decision** - 模型决策（根据描述自动应用）
  3. **Always** - 始终生效
  4. **Specific Files** - 指定文件生效（通配符匹配）
- **存储位置**: `.lingma/rules/`
- **优先级**: Rules > Memory（冲突时优先遵循规则）
- **限制**: 单个文件最大 10000 字符

**我们的使用**: ✅ 已创建 `spec-session-start.md` (Always On)

**优化空间**:
- ⚠️ 当前使用的是 Markdown 文件
- ✅ 应该通过 IDE 的规则管理界面配置（更规范）

### 5. Skills（技能）✅ 已使用
**能力**:
- **智能调用** - 模型根据请求和 Skill 描述自主决定
- **模块化设计** - 每个 Skill 专注特定任务
- **两级作用域**:
  - 用户级: `~/.lingma/skills/{skill-name}/SKILL.md`
  - 项目级: `.lingma/skills/{skill-name}/SKILL.md`
- **触发方式**:
  - 自动: 直接描述需求，模型自动判断
  - 手动: 输入 `/skill-name`

**我们的使用**: ✅ 已创建 `spec-driven-development` skill

### 6. MCP（模型上下文协议）⭐ 待集成
**能力**:
- **标准化协议** - 连接外部工具和系统
- **两种模式**:
  - STDIO - 本地进程通信
  - SSE - 远程服务（Server-Sent Events）
- **最多10个 MCP 服务**
- **MCP 广场** - 魔搭社区、Higress 市场
- **自动调用** - 模型根据需求自主决策是否调用

**热门场景**:
- 数据库 - 获取 schemas，生成 DAO 代码
- 在线文档 - 基于文档生成代码
- 设计系统 - 根据设计稿生成前端代码

**价值**:
- ✅ **Phase 2 的核心** - 标准化外部工具接入

### 7. Tools（工具）⭐ 新发现
**内置工具** (10+):
- 文件查找
- 文件读取
- 目录读取
- 工程内语义符号检索
- 文件修改
- 错误获取
- 终端执行
- ...

**特点**:
- 智能体自主决策使用
- **无需开发者确认或干预**
- 可根据返回结果决策下一步

**价值**:
- ❌ **我们可以移除大部分自定义的工具封装**
- ✅ 直接使用 Lingma 的内置工具

### 8. Custom Commands（自定义命令）⭐ 新发现
**能力**:
- 创建快捷命令
- 绑定到特定操作
- 提高重复任务效率

**价值**:
- ✅ 可以创建快捷命令如 `/spec-status`, `/continue-dev`

### 9. Edit & Inline Chat（编辑和行间会话）
**能力**:
- 直接在编辑器中对话
- 代码片段级别的交互
- Diff View 预览更改

**价值**:
- ✅ 增强用户体验

---

## 🏗️ 重构后的架构设计

### 核心原则

**最大化利用 Lingma 原生能力，最小化自定义实现**

### 新架构图

```
┌──────────────────────────────────────┐
│      Lingma Native Agent             │ ← 使用内置 Agent
│      (spec-driven-core-agent)        │    - 自主决策
│                                      │    - 工具调用
│                                      │    - 终端执行
└──────────┬───────────────────────────┘
           │ 使用
┌──────────▼───────────────────────────┐
│      Lingma Native Features          │ ← 全部原生能力
│                                      │
│  ┌────────────────────────────────┐  │
│  │ Rules (.lingma/rules/)         │  │ ← 约束和规范
│  │ - spec-session-start (Always)  │  │
│  │ - automation-policy (Decision) │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ Skills (.lingma/skills/)       │  │ ← 工作流程
│  │ - spec-driven-development      │  │
│  │ - code-review                  │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ Memory (Lingma Built-in)       │  │ ← 替代自定义 context
│  │ - 长期记忆（自动形成）          │  │
│  │ - 工程级记忆                   │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ Context (#file, #codebase...)  │  │ ← 替代自定义文件查找
│  │ - #file / #folder              │  │
│  │ - #codebase (语义检索)         │  │
│  │ - #codeChanges / #gitCommit    │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ MCP Servers (Phase 2)          │  │ ← 外部工具接入
│  │ - filesystem-mcp               │  │
│  │ - git-mcp                      │  │
│  │ - spec-mcp                     │  │
│  └────────────────────────────────┘  │
└──────────┬───────────────────────────┘
           │ 调用
┌──────────▼───────────────────────────┐
│   Lingma Built-in Tools              │ ← 替代自定义脚本
│   - 文件读写                         │
│   - 目录操作                         │
│   - 语义检索                         │
│   - 终端执行                         │
│   - 错误获取                         │
└──────────────────────────────────────┘
```

### 关键变化

#### ❌ 可以移除的自定义实现

| 原实现 | 替代方案 | 理由 |
|--------|---------|------|
| `automation-engine.py` | Lingma Agent 自主决策 | Agent 已有风险评估和策略选择能力 |
| `operation-logger.py` | Lingma 内置日志 | IDE 自动记录所有操作 |
| `snapshot-manager.py` | Git + Lingma 快照 | IDE 支持多次对话迭代和快照回滚 |
| `spec-driven-agent.py` | 内置 Agent | 功能重复 |
| 自定义 context 管理 | `#codebase`, `#file` | 原生支持且更强大 |
| 自定义 memory 管理 | Lingma Memory | 自动形成和管理 |

#### ✅ 保留的核心组件

| 组件 | 原因 |
|------|------|
| `.lingma/specs/` | Spec 文档是业务逻辑，不是工具 |
| `.lingma/skills/` | 符合 Lingma Skill 标准 |
| `.lingma/rules/` | 符合 Lingma Rule 标准 |
| `.lingma/agents/` | 符合 Lingma Agent 标准 |

#### ⭐ 新增的原生能力使用

1. **Memory** - 替代自定义上下文管理
2. **Context (#codebase)** - 替代自定义文件查找
3. **Built-in Tools** - 替代自定义工具封装
4. **Custom Commands** - 提供快捷操作

---

## 📋 实施计划

### Phase 1.5: 架构精简（预计: 4h）

**目标**: 移除冗余实现，改用原生能力

#### Task-019: 评估并标记可移除的代码
- [ ] 审查 `automation-engine.py`
- [ ] 审查 `operation-logger.py`
- [ ] 审查 `snapshot-manager.py`
- [ ] 审查 `spec-driven-agent.py`
- [ ] 创建迁移计划

#### Task-020: 配置 Lingma Rules（通过 IDE）
- [ ] 将 `spec-session-start.md` 转换为 Always On Rule
- [ ] 创建 Model Decision Rules:
  - `automation-policy` - 自动化策略
  - `risk-assessment` - 风险评估
- [ ] 测试规则生效

#### Task-021: 优化 Skills
- [ ] 确保 `spec-driven-development` 符合标准
- [ ] 添加更多实用 Skills:
  - `code-review` - 代码审查
  - `test-generator` - 测试生成
  - `doc-writer` - 文档编写

#### Task-022: 设置 Memory 策略
- [ ] 定义需要记忆的内容:
  - 用户偏好（自动化级别）
  - 项目规范（代码风格）
  - 常用工作流
- [ ] 测试记忆形成和使用

#### Task-023: 创建 Custom Commands
- [ ] `/spec-status` - 查看 spec 状态
- [ ] `/continue-dev` - 继续开发
- [ ] `/create-spec` - 创建新 spec
- [ ] `/archive-spec` - 归档 spec

### Phase 2: MCP 集成（保持不变，预计: 8h）

**调整**: 使用 Lingma 原生 MCP 配置界面

#### Task-006: 配置 MCP 服务器
- [ ] 通过 IDE 的 MCP 服务页面添加
- [ ] 或使用配置文件 `.lingma/mcp-config.json`

#### Task-007-009: 实现和测试（同原计划）

### Phase 3: 增强原生能力使用（预计: 4h）

#### Task-024: 充分利用 Context
- [ ] 在 Skills 中使用 `#codebase` 进行语义检索
- [ ] 使用 `#codeChanges` 进行代码审查
- [ ] 使用 `#gitCommit` 追溯历史

#### Task-025: 优化 Agent 提示
- [ ] 更新 `spec-driven-core-agent.md`
- [ ] 强调使用原生工具
- [ ] 减少自定义逻辑

#### Task-026: 创建最佳实践文档
- [ ] 如何使用 Memory
- [ ] 如何有效使用 Context
- [ ] Rules 配置指南
- [ ] Skills 编写规范

---

## 💡 关键洞察

### 1. 我们之前"过度工程化"了

**问题**:
- 创建了太多自定义实现
- 没有充分利用 Lingma 的原生能力
- 增加了维护负担

**解决**:
- 信任 Lingma 的能力
- 只在必要时自定义
- 专注于业务逻辑（Spec）

### 2. Lingma 的能力远超预期

**原生能力覆盖**:
- ✅ Agent - 自主决策和执行
- ✅ Memory - 长期记忆和上下文
- ✅ Context - 文件和代码检索
- ✅ Rules - 规范和约束
- ✅ Skills - 工作流程
- ✅ MCP - 外部工具集成
- ✅ Tools - 文件操作、终端执行
- ✅ Custom Commands - 快捷操作

**我们只需要**:
- 配置和优化
- 业务逻辑（Spec）
- 团队规范（Rules/Skills）

### 3. 正确的分层

```
Layer 1: Lingma Native (平台层)
  ├─ Agent
  ├─ Memory
  ├─ Context
  ├─ Rules
  ├─ Skills
  ├─ MCP
  └─ Tools

Layer 2: Project Specific (项目层)
  ├─ Specs (业务逻辑)
  ├─ Custom Rules (团队规范)
  └─ Custom Skills (项目工作流)

Layer 3: User Preferences (用户层)
  ├─ Memory (个人习惯)
  └─ Custom Commands (个人快捷方式)
```

**关键**: Layer 1 由 Lingma 提供，Layer 2-3 由我们配置

---

## 🎯 推荐行动方案

### 立即行动（今天）

1. **暂停 Phase 2** - 先进行架构精简
2. **启动 Phase 1.5** - 评估和标记可移除代码
3. **配置原生 Rules** - 通过 IDE 界面
4. **测试 Memory** - 了解其工作方式

### 本周内

1. **完成 Phase 1.5** - 移除冗余代码
2. **优化 Skills** - 确保符合标准
3. **创建 Custom Commands** - 提高效率
4. **更新文档** - 反映新架构

### 下周

1. **开始 Phase 2** - MCP 集成（使用原生配置）
2. **Phase 3** - 增强原生能力使用
3. **全面测试** - 验证新架构

---

## 📊 预期收益

### 代码量减少

| 组件 | 当前 | 重构后 | 减少 |
|------|------|--------|------|
| Python 脚本 | 2,396 lines | ~500 lines | -79% |
| 配置文件 | 100 lines | 50 lines | -50% |
| **总计** | **2,496 lines** | **~550 lines** | **-78%** |

### 维护成本降低

- **依赖减少**: 从 3 个自定义组件 → 0 个
- **测试简化**: 从 9 个测试 → 3 个配置验证
- **文档精简**: 从 5 个报告 → 2 个指南

### 能力提升

- **更强的 Agent**: 使用 Lingma 原生 Agent，能力更全面
- **更好的 Memory**: 自动形成，无需手动管理
- **更智能的 Context**: 语义检索，更准确
- **更丰富的 Tools**: 10+ 内置工具，持续增加

---

## ⚠️ 注意事项

### 1. 渐进式迁移

**不要**:
- ❌ 一次性删除所有自定义代码
- ❌ 立即切换到新架构

**应该**:
- ✅ 逐步验证原生能力
- ✅ 保持向后兼容
- ✅ 充分测试后再移除

### 2. 保留 Spec 系统

**Spec 是业务逻辑**，不是工具实现：
- ✅ 保留 `.lingma/specs/`
- ✅ 保留 Spec 驱动的工作流
- ✅ 只是简化底层实现

### 3. 团队培训

新架构需要团队理解：
- 如何使用 Memory
- 如何有效使用 Context
- Rules 的配置方法
- Skills 的编写规范

---

## 🚀 下一步

**您希望我：**

1. **立即开始 Phase 1.5** - 评估并标记可移除的代码
2. **先详细规划** - 创建详细的迁移计划
3. **测试原生能力** - 验证 Lingma 的能力是否满足需求
4. **其他想法** - 请告诉我您的具体需求

**我的建议**: 选项 1，立即开始评估，然后根据您的反馈决定是否继续。
