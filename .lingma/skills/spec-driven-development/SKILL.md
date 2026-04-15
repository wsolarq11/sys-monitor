---
name: spec-driven-development
description: Spec-driven development workflow that maintains specification documents across sessions, enables autonomous development based on specs, and only interacts with users when requirements need clarification. Use when starting new features, refactoring, or when the user mentions specs, specifications, or spec-driven development.
---

# Spec-Driven Development Workflow

## 核心原则

1. **Spec 即真相**: 所有开发决策基于 spec 文档
2. **跨会话持久化**: Spec 在会话间保持不变和同步
3. **自主开发**: 基于清晰的 spec  autonomously 执行开发任务
4. **最小交互**: 仅在需求不明确时与用户确认
5. **职责边界**: 专注 Spec 管理，Memory 操作委托给 memory-management Skill

## Spec 文件结构

```
.lingma/specs/
├── current-spec.md          # 当前活跃的开发规范
├── spec-history/            # 历史 spec 版本
│   ├── 2024-01-15-feature-x.md
│   └── 2024-01-20-refactor-y.md
└── templates/               # Spec 模板
    ├── feature-spec.md
    ├── refactor-spec.md
    └── bugfix-spec.md
```

## Spec 模板结构

### Feature Spec 模板

```markdown
# [功能名称] Spec

## 元数据
- **创建日期**: YYYY-MM-DD
- **状态**: draft | approved | in-progress | completed | cancelled
- **优先级**: P0 | P1 | P2 | P3
- **负责人**: [姓名]

## 背景与目标
### 问题陈述
[描述要解决的问题]

### 业务价值
[说明为什么需要这个功能]

### 成功标准
- [可衡量的成功指标 1]
- [可衡量的成功指标 2]

## 需求规格
### 功能性需求
#### FR-001: [需求名称]
**描述**: [详细描述]
**验收标准**:
- [ ] AC-001: [具体验收条件]
- [ ] AC-002: [具体验收条件]
**优先级**: Must have | Should have | Could have | Won't have

### 非功能性需求
#### NFR-001: [性能/安全/可用性等]
**要求**: [具体要求]
**验收标准**: [如何验证]

## 技术方案
### 架构设计
[系统架构图或描述]

### 技术选型
- [技术/库/框架 1]: [选择理由]
- [技术/库/框架 2]: [选择理由]

### 数据模型
[数据库 schema 或数据结构]

### API 设计
```typescript
// API 接口定义
interface ExampleAPI {
  // ...
}
```

## 实现计划
### 任务分解
- [ ] Task-001: [任务描述] (预计: Xh)
  - 子任务:
    - [ ] Subtask-001-01
    - [ ] Subtask-001-02
- [ ] Task-002: [任务描述] (预计: Xh)

### 依赖关系
- [依赖的任务或外部系统]

### 风险评估
- **风险 1**: [描述] - 缓解措施: [措施]
- **风险 2**: [描述] - 缓解措施: [措施]

## 测试策略
### 单元测试
[测试覆盖计划]

### 集成测试
[集成测试场景]

### E2E 测试
[端到端测试流程]

## 部署计划
### 前置条件
- [部署前需要完成的事项]

### 部署步骤
1. [步骤 1]
2. [步骤 2]

### 回滚方案
[如果出现问题如何回滚]

## 文档更新
- [ ] 更新用户文档
- [ ] 更新 API 文档
- [ ] 更新 CHANGELOG

## 评审记录
### 技术评审
- 评审人: [姓名]
- 评审日期: YYYY-MM-DD
- 评审意见: [意见内容]

### 产品评审
- 评审人: [姓名]
- 评审日期: YYYY-MM-DD
- 评审意见: [意见内容]

## 变更记录
| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|----------|--------|
| YYYY-MM-DD | v1.0 | 初始版本 | [姓名] |
```

## 工作流程

### Phase 1: Spec 创建/澄清

**触发条件**:
- 用户提出新功能需求
- 用户提到"spec"、"规范"、"需求文档"
- 开始新的开发任务

**执行步骤**:

1. **需求收集**
   ```
   如果需求不清晰，使用 AskUserQuestion 工具询问:
   - 功能的核心目标是什么？
   - 有哪些关键的验收标准？
   - 优先级和期望完成时间？
   - 有哪些技术约束？
   ```

2. **创建 Spec 草案**
   - 使用 appropriate template
   - 填充已知信息
   - 标记需要澄清的部分为 `[NEEDS CLARIFICATION]`

3. **用户确认**
   - 展示 spec 草案给用户
   - 请求确认或补充
   - 仅在必要时交互

4. **Spec 批准**
   - 用户确认后，标记状态为 `approved`
   - 保存到 `.lingma/specs/current-spec.md`
   - 创建 git commit: `docs: add spec for [feature name]`

### Phase 2: 基于 Spec 的自主开发

**核心原则**: 
- **严格遵循 spec**: 所有实现必须对应 spec 中的需求
- **Traceability**: 代码变更能追溯到具体的 spec 条目
- **进度跟踪**: 实时更新 spec 中的任务状态

**执行步骤**:

1. **加载 Spec**
   ```bash
   # 读取当前 spec
   read .lingma/specs/current-spec.md
   ```

2. **任务规划**
   - 从 spec 中提取任务列表
   - 创建详细的 implementation plan
   - 识别依赖和顺序

3. **自主执行**
   ```
   For each task in spec:
     a. 实现代码
     b. 编写测试
     c. 运行验证
     d. 更新 spec 状态: [ ] -> [x]
     e. 提交代码: feat: implement [task description] (ref: spec#FR-XXX)
   ```

4. **进度报告**
   - 每完成一个 major task，更新 spec
   - 在 spec 中添加实施笔记
   - 记录遇到的问题和解决方案

5. **验收检查**
   - 对照 spec 中的验收标准逐一验证
   - 确保所有 AC (Acceptance Criteria) 都满足
   - 更新 spec 状态为 `completed`

### Phase 3: Spec 维护和演化

**场景 1: 需求变更**

```markdown
1. 检测变更类型:
   - Minor change: 直接更新 spec，保留历史记录
   - Major change: 创建新版本的 spec

2. 更新流程:
   - 备份当前 spec 到 spec-history/
   - 更新 current-spec.md
   - 添加变更记录
   - 通知相关方（如果需要）
   - 重新评估影响范围
```

**场景 2: 发现 Spec 缺陷**

```markdown
1. 识别问题:
   - 技术不可行
   - 需求冲突
   - 遗漏关键场景

2. 处理流程:
   - 在 spec 中标记问题区域
   - 如果影响小，自主修正并记录
   - 如果影响大，暂停并向用户澄清
   - 更新 spec 并重新审批
```

**场景 3: 跨会话恢复**

```markdown
1. 会话开始时:
   - 检查 .lingma/specs/current-spec.md 是否存在
   - 读取 spec 状态
   - 如果状态是 in-progress，继续未完成的任务
   - 向用户报告当前进度

2. 上下文恢复:
   - 从 spec 中读取最近的实施笔记
   - 检查 git log 了解最近的变更
   - 确定下一步行动
```

## 自动化规则

### Rule 1: Spec 存在性检查

```
每次会话开始时:
  IF .lingma/specs/current-spec.md exists AND status == "in-progress":
    自动加载 spec 并继续开发
  ELSE IF 用户提到新功能:
    启动 Phase 1 (Spec 创建)
  ELSE:
    正常交互模式
```

### Rule 2: 需求澄清触发器

```
以下情况必须与用户确认:
  - Spec 中有 [NEEDS CLARIFICATION] 标记
  - 遇到相互矛盾的需求
  - 技术实现超出预期复杂度 (> 2x 预估时间)
  - 发现重大安全风险
  - 需要改变已批准的架构决策

其他情况:
  - 自主决策并记录在 spec 的实施笔记中
```

### Rule 3: 进度追踪自动化

```
每完成一个任务:
  1. 更新 spec 中的任务状态
  2. 添加实施笔记:
     ```markdown
     ### 实施笔记 - YYYY-MM-DD HH:mm
     - 完成了: [任务描述]
     - 关键决策: [决策内容和理由]
     - 遇到的问题: [问题及解决方案]
     - 下一步: [计划]
     ```
  3. Git commit with spec reference
  4. 如果所有任务完成，更新 spec 状态为 completed
```

### Rule 4: Spec 版本控制

```markdown
Git commit 规范:
  - Spec 创建: docs: create spec for [feature]
  - Spec 更新: docs: update spec for [feature] - [change summary]
  - 代码实现: feat: [description] (ref: spec#FR-XXX)
  - Bug 修复: fix: [description] (ref: spec#FR-XXX)
  - 完成任务: chore: complete task [task-id] from spec
```

## 最佳实践

### 1. Spec 质量检查清单

在开始开发前，确保 spec 包含:
- [ ] 明确的成功标准（可衡量）
- [ ] 完整的验收标准
- [ ] 技术方案经过可行性验证
- [ ] 风险评估和缓解措施
- [ ] 任务分解足够细粒度（每个任务 < 4h）
- [ ] 依赖关系清晰

### 2. 实施笔记规范

```markdown
### 实施笔记 - 2024-01-15 14:30

**完成**: 实现用户认证模块 (Task-003)

**关键决策**:
- 选择 JWT 而非 Session: 更好的可扩展性，符合微服务架构
- Token 过期时间设为 24h: 平衡安全性和用户体验

**遇到的问题**:
- 问题: JWT 库版本冲突
- 解决: 升级到最新兼容版本，更新 package.json

**测试结果**:
- 单元测试: 15/15 通过
- 集成测试: 3/3 通过

**下一步**: 开始实现权限管理模块 (Task-004)
```

### 3. Spec 审查要点

定期（每周或每个里程碑）审查 spec:
- 实际进度 vs 计划进度
- 是否有偏离 spec 的实现
- 是否需要调整后续任务
- 经验教训总结

## 工具和脚本

### Spec 初始化脚本

创建 `.lingma/scripts/init-spec.sh`:

```bash
#!/bin/bash
# 初始化 spec 目录结构

SPEC_DIR=".lingma/specs"
HISTORY_DIR="$SPEC_DIR/spec-history"
TEMPLATES_DIR="$SPEC_DIR/templates"

mkdir -p "$HISTORY_DIR"
mkdir -p "$TEMPLATES_DIR"

# 复制模板
cp templates/feature-spec.md "$TEMPLATES_DIR/"
cp templates/refactor-spec.md "$TEMPLATES_DIR/"
cp templates/bugfix-spec.md "$TEMPLATES_DIR/"

echo "Spec directory structure created at $SPEC_DIR"
```

### Spec 状态检查脚本

创建 `.lingma/scripts/check-spec-status.py`:

```python
#!/usr/bin/env python3
"""检查当前 spec 的状态和进度"""

import re
from pathlib import Path

def check_spec_status():
    spec_file = Path(".lingma/specs/current-spec.md")
    
    if not spec_file.exists():
        print("❌ No active spec found")
        return
    
    content = spec_file.read_text()
    
    # 提取状态
    status_match = re.search(r'\*\*状态\*\*:\s*(\w+)', content)
    status = status_match.group(1) if status_match else "unknown"
    
    # 计算任务进度
    total_tasks = len(re.findall(r'- \[.\]', content))
    completed_tasks = len(re.findall(r'- \[x\]', content))
    progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    print(f"📋 Spec Status: {status}")
    print(f"📊 Progress: {completed_tasks}/{total_tasks} tasks ({progress:.1f}%)")
    
    if status == "in-progress":
        print("\n⏳ Next steps:")
        # 找到第一个未完成的任务
        next_task = re.search(r'- \[ \] (Task-\d+:.+)', content)
        if next_task:
            print(f"  → {next_task.group(1)}")

if __name__ == "__main__":
    check_spec_status()
```

## 示例场景

### 场景 1: 新功能开发

**用户输入**: "我需要添加一个文件夹大小阈值告警功能"

**AI 响应流程**:

1. **需求澄清** (仅当必要时):
   ```
   AskUserQuestion:
   - 阈值如何配置？(固定值/用户可配置)
   - 告警方式？(UI 提示/邮件/系统通知)
   - 检查频率？(实时/定时)
   ```

2. **创建 Spec**:
   - 使用 feature-spec.md 模板
   - 填充需求细节
   - 生成技术方案
   - 请求用户确认

3. **自主开发**:
   - 按照 spec 中的任务列表执行
   - 实现后端阈值检查逻辑
   - 实现前端配置 UI
   - 实现告警通知
   - 编写测试
   - 更新文档

4. **完成报告**:
   ```
   ✅ Spec 完成: 文件夹大小阈值告警
   
   实施摘要:
   - 所有 8 个任务已完成
   - 15 个验收标准全部满足
   - 单元测试覆盖率: 92%
   - 已更新用户文档
   
   查看完整 spec: .lingma/specs/current-spec.md
   ```

### 场景 2: 跨会话恢复

**新会话开始**:

1. **自动检测**:
   ```
   发现活跃的 spec: .lingma/specs/current-spec.md
   状态: in-progress
   进度: 5/8 任务完成 (62.5%)
   ```

2. **进度报告**:
   ```
   📋 检测到进行中的开发任务:
   
   Spec: 文件夹大小阈值告警
   状态: 进行中 (62.5%)
   
   已完成:
   ✓ Task-001: 设计数据模型
   ✓ Task-002: 实现阈值配置 API
   ✓ Task-003: 实现阈值检查逻辑
   ✓ Task-004: 编写单元测试
   ✓ Task-005: 创建前端配置组件
   
   待完成:
   ⏳ Task-006: 实现告警通知系统
   ⏳ Task-007: 集成测试
   ⏳ Task-008: 文档更新
   
   最后更新: 2024-01-15 16:45
   
   是否继续执行剩余任务？
   ```

3. **继续执行**:
   - 用户确认后，从 Task-006 继续
   - 自主完成剩余任务
   - 更新 spec 状态为 completed

## 注意事项

### ⚠️ 常见陷阱

1. **Spec 过于详细**: 
   - ❌ 避免: 逐行代码级别的 spec
   - ✅ 推荐: 关注 WHAT 和 WHY，让 AI 决定 HOW

2. **Spec 僵化**:
   - ❌ 避免: 发现更好方案仍坚持原 spec
   - ✅ 推荐: 灵活调整，记录变更原因

3. **过度交互**:
   - ❌ 避免: 每个小决策都问用户
   - ✅ 推荐: 建立信任，自主决策并记录

4. **Spec 过时**:
   - ❌ 避免: 实现偏离 spec 但不更新
   - ✅ 推荐: 保持 spec 与实现同步

### 💡 成功要素

1. **清晰的验收标准**: 可衡量、可验证
2. **合理的任务粒度**: 每个任务 2-4 小时
3. **持续的状态更新**: 保持 spec 准确反映进度
4. **良好的实施笔记**: 记录决策和问题
5. **定期的回顾**: 总结经验，改进流程

## 快速开始

### 首次使用

1. **初始化 Spec 目录**:
   ```bash
   mkdir -p .lingma/specs/{spec-history,templates}
   ```

2. **创建第一个 Spec**:
   - 告诉 AI 你的需求
   - AI 会引导你创建 spec
   - 确认后开始开发

3. **后续会话**:
   - AI 会自动检测活跃的 spec
   - 继续未完成的工作
   - 或创建新的 spec

### 常用命令

```bash
# 查看当前 spec 状态
python .lingma/scripts/check-spec-status.py

# 归档完成的 spec
mv .lingma/specs/current-spec.md .lingma/specs/spec-history/$(date +%Y-%m-%d)-feature-name.md

# 创建新 spec
# (通过与 AI 对话自动创建)
```

---

**记住**: Spec 是活的文档，它随着项目演进而演化。保持它的准确性和相关性比严格遵守更重要。
