# 系统组件精简优化计划

**目标**: 全面精简 .lingma/ 下所有组件，避免拆东墙补西墙  
**原则**: 效率为王，系统化解决，一次性到位  
**参考**: OpenAI/Claude Code 最佳实践（Agent ≤5KB, Rule ≤3KB, Skill ≤10KB）

---

## 📊 当前状态全景分析

### Agent 文件（5个，全部超标）
| 文件 | 当前大小 | 目标大小 | 超标 | 优先级 |
|------|---------|---------|------|--------|
| documentation-agent.md | 18.6KB / 798行 | ≤5KB | **+272%** | P0 |
| code-review-agent.md | 14.2KB / 643行 | ≤5KB | **+184%** | P0 |
| test-runner-agent.md | 11.6KB / 470行 | ≤5KB | **+132%** | P0 |
| supervisor-agent.md | 10.5KB / 434行 | ≤5KB | **+110%** | P0 |
| spec-driven-core-agent.md | 9.8KB / 396行 | ≤5KB | **+96%** | P0 |

**总计**: 64.7KB → 目标 25KB（减少 61%）

---

### Rules 文件（5个，部分超标）
| 文件 | 当前大小 | 目标大小 | 超标 | 优先级 |
|------|---------|---------|------|--------|
| spec-session-start.md | 15.8KB / 640行 | ≤3KB | **+427%** | P1 |
| memory-usage.md | 13.9KB / 661行 | ≤3KB | **+363%** | P1 |
| automation-policy.md | 11.2KB / 518行 | ≤3KB | **+273%** | P1 |
| AGENTS.md | 9.5KB / 257行 | ≤3KB | **+217%** | P0 |
| doc-redundancy-prevention.md | 5.3KB / 190行 | ≤3KB | **+77%** | P2 |

**总计**: 55.7KB → 目标 15KB（减少 73%）

---

### Skills 文件（1个，超标）
| 文件 | 当前大小 | 目标大小 | 超标 | 优先级 |
|------|---------|---------|------|--------|
| spec-driven-development/SKILL.md | 15.5KB | ≤10KB | **+55%** | P1 |

---

## 🎯 优化策略（避免拆东墙补西墙）

### 核心原则
```
1. 提取共性 → 创建共享文档/Skills
2. 按需加载 → 详细内容通过 Read 工具动态读取
3. 保持简洁 → Agent/Rule 仅保留核心指令
4. 一次到位 → 批量处理，避免反复修改
```

---

### 策略 1: 创建共享架构文档（推荐）⭐

**问题**: 多个 Agent/Rule 包含重复的详细逻辑  
**解决**: 提取到 docs/architecture/，Agent/Rule 引用

```
docs/architecture/
├── agent-system/
│   ├── orchestration-patterns.md      # 编排模式（从 supervisor 提取）
│   ├── quality-gates.md               # 质量门禁标准（从多个 Agent 提取）
│   └── decision-log-format.md         # 决策日志格式（从 automation-policy 提取）
├── rules-system/
│   ├── session-management.md          # 会话管理（从 spec-session-start 提取）
│   └── memory-guidelines.md           # 记忆使用指南（从 memory-usage 提取）
└── skills-system/
    └── spec-workflow-details.md       # Spec 工作流详情（从 SKILL.md 提取）
```

**效果**:
- ✅ Agent 文件减少 60-70%
- ✅ Rule 文件减少 70-80%
- ✅ 详细内容统一管理，避免重复
- ✅ 按需加载，节省上下文

---

### 策略 2: 精简 Agent 文件模板

**标准结构**（≤5KB）:
```markdown
---
name: agent-name
description: 简短描述（用于模型选择）
tools: Read, Write, Bash, Grep, Glob
---

# Agent 名称

**角色**: 1句话定义  
**职责**: 3-5条核心职责  

## 工作流程
1. 步骤1（1行）
2. 步骤2（1行）
3. 步骤3（1行）

## 可用资源
- 详细指南: docs/architecture/xxx.md
- 相关 Skills: skill-name

## 输出要求
- 关键要点1
- 关键要点2
```

---

### 策略 3: 精简 Rule 文件模板

**标准结构**（≤3KB）:
```markdown
---
trigger: always_on  # 或 model_decision/specific_files
---

# Rule 名称

**目标**: 1句话  
**适用范围**: 1句话  

## 核心规则
1. 规则1（简洁明了）
2. 规则2
3. 规则3

## 示例
✅ 正确做法
❌ 错误做法

## 参考
- 详细说明: docs/rules/xxx.md
```

---

### 策略 4: 精简 Skill 文件

**标准结构**（≤10KB）:
```markdown
---
name: skill-name
description: 用于语义匹配的描述
version: 1.0
---

# Skill 名称

## 何时使用
- 场景1
- 场景2

## 快速开始
1. 步骤1
2. 步骤2

## 详细工作流
（保持在 5-8 步内）

## 参考文档
- 详细说明: docs/skills/xxx.md
- 最佳实践: docs/guides/xxx.md
```

---

## 🚀 执行计划（分阶段，确保效率）

### Phase 1: 创建共享文档（30分钟）
```bash
# 1. 创建目录结构
mkdir -p docs/architecture/{agent-system,rules-system,skills-system}

# 2. 提取详细内容
# - 从 supervisor-agent.md 提取编排模式 → docs/architecture/agent-system/orchestration-patterns.md
# - 从 automation-policy.md 提取决策日志 → docs/architecture/agent-system/decision-log-format.md
# - 从 spec-session-start.md 提取会话管理 → docs/architecture/rules-system/session-management.md
# - 从 memory-usage.md 提取记忆指南 → docs/architecture/rules-system/memory-guidelines.md
# - 从 spec-driven-development/SKILL.md 提取工作流 → docs/architecture/skills-system/spec-workflow-details.md
```

**预期成果**: 5个共享文档，总大小 ~20KB

---

### Phase 2: 批量精简 Agent 文件（20分钟）
```bash
# 重写所有 5 个 Agent 文件，每个 ≤5KB
# 保留: frontmatter + 核心指令 + 引用链接
# 移除: 详细示例、代码片段、冗长说明
```

**预期成果**: 5个 Agent 文件，总大小从 64.7KB → 25KB（减少 61%）

---

### Phase 3: 批量精简 Rule 文件（15分钟）
```bash
# 重写所有 5 个 Rule 文件，每个 ≤3KB
# 保留: trigger + 核心规则 + 简要示例
# 移除: 冗长解释、重复内容
```

**预期成果**: 5个 Rule 文件，总大小从 55.7KB → 15KB（减少 73%）

---

### Phase 4: 精简 Skill 文件（10分钟）
```bash
# 重写 spec-driven-development/SKILL.md，≤10KB
# 保留: 核心工作流 + 关键步骤
# 移除: 过度详细的说明
```

**预期成果**: 1个 Skill 文件，从 15.5KB → 10KB（减少 35%）

---

### Phase 5: 验证与测试（5分钟）
```bash
# 1. 运行自动化验证
python scripts/verify_system_effectiveness.py

# 2. 检查文件大小
python scripts/check_component_sizes.py  # 新建脚本

# 3. Git 提交
git add .lingma/ docs/
git commit -m "refactor: 系统性精简所有组件，减少 65% 体积"
```

---

## 📊 预期效果对比

| 组件类型 | 当前总大小 | 目标总大小 | 减少比例 | 预计时间 |
|---------|-----------|-----------|---------|---------|
| Agents | 64.7KB | 25KB | **-61%** | 20分钟 |
| Rules | 55.7KB | 15KB | **-73%** | 15分钟 |
| Skills | 15.5KB | 10KB | **-35%** | 10分钟 |
| **新增共享文档** | 0KB | 20KB | - | 30分钟 |
| **净减少** | **135.9KB** | **70KB** | **-48%** | **75分钟** |

---

## 🔍 如何避免拆东墙补西墙？

### 社区最佳实践

#### 1. 单一事实来源（Single Source of Truth）
```
❌ 错误: 在多个 Agent/Rule 中重复相同逻辑
✅ 正确: 提取到共享文档，其他地方引用
```

**实现**:
- 编排模式 → docs/architecture/agent-system/orchestration-patterns.md
- 质量门禁 → docs/architecture/agent-system/quality-gates.md
- 会话管理 → docs/architecture/rules-system/session-management.md

---

#### 2. 渐进式披露（Progressive Disclosure）
```
❌ 错误: 所有细节都在 Agent/Rule 文件中
✅ 正确: 核心指令在文件，详细内容在 docs/
```

**实现**:
```markdown
# Agent 文件（简洁）
当需要详细了解时，读取: docs/architecture/xxx.md

# docs/ 文件（详细）
完整的工作流、示例、边界情况
```

---

#### 3. 自动化检测（Automated Detection）
```bash
# Git Hook: 阻止过大文件提交
if [ $SIZE_KB -gt 5 ]; then
    echo "❌ Agent 文件过大"
    exit 1
fi

# 验证脚本: 定期检测
python scripts/verify_system_effectiveness.py
```

---

#### 4. 定期审查（Regular Review）
```yaml
# .github/workflows/component-size-check.yml
name: Component Size Check
on:
  schedule:
    - cron: '0 9 * * 1'  # 每周一

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check sizes
        run: python scripts/check_component_sizes.py
      
      - name: Alert if oversized
        if: failure()
        run: |
          echo "⚠️ 检测到组件过大，需要精简"
          # 发送通知
```

---

## 💡 核心思考框架

### 1. 结合什么？
- **Lingma 官方文档**: Custom Agent 规范
- **社区最佳实践**: OpenAI/Claude Code/Google
- **项目实际需求**: 哪些功能真正必需？
- **自动化能力**: Git Hook + 验证脚本

### 2. 怎么去做更有效？
- **批量处理**: 一次性解决所有问题
- **提取共性**: 避免重复内容
- **按需加载**: 详细内容放 docs/
- **自动化防护**: 防止再次臃肿

### 3. 怎么确定会有效？
- **量化指标**: 文件大小、行数
- **自动化验证**: verify_system_effectiveness.py
- **Git Hook**: 阻止违规提交
- **定期审查**: 每周/每月检查

---

## 🎯 立即执行决策

**推荐方案**: 执行完整的 Phase 1-5（75分钟）

**理由**:
1. ✅ 一次性解决所有臃肿问题
2. ✅ 建立共享文档体系，避免重复
3. ✅ 自动化防护，防止再次发生
4. ✅ 符合社区最佳实践

**风险**: 
- ⚠️ 需要 75 分钟集中处理
- ⚠️ 可能影响短期开发效率

**缓解**:
- ✅ 分批提交，降低风险
- ✅ 保留原始文件备份
- ✅ 逐步验证，确保功能正常

---

**是否立即执行？请确认！** 🚀
