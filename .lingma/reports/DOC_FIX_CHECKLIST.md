# 文档问题修复清单

**创建日期**: 2026-04-16  
**优先级**: P0 > P1 > P2 > P3  
**状态追踪**: 🔲未开始 🔄进行中 ✅已完成

---

## P0 - 立即修复（阻塞性问题）

### 🔲 任务1: 补全Agent详细文档（4个文件）

**重要性**: ⭐⭐⭐⭐⭐  
**预计时间**: 2-3小时  
**负责人**: Documentation Agent

#### 需要创建的文件

- [ ] `.lingma/docs/architecture/agent-system/code-review-agent-detailed.md`
- [ ] `.lingma/docs/architecture/agent-system/documentation-agent-detailed.md`
- [ ] `.lingma/docs/architecture/agent-system/spec-driven-core-agent-detailed.md`
- [ ] `.lingma/docs/architecture/agent-system/test-runner-agent-detailed.md`

#### 内容要求
每个文件应包含：
1. 角色定义和职责
2. 核心能力详细说明
3. 工作流程详解
4. 技术实现细节（Python伪代码）
5. 使用示例
6. 与其他Agent的交互

#### 参考来源
- 对应的Agent文件（`.lingma/agents/*.md`）
- 现有的 `supervisor-detailed.md` 结构
- 实际Python脚本（`.lingma/scripts/*.py`）

---

### 🔲 任务2: 补全Supervisor相关文档（3个文件）

**重要性**: ⭐⭐⭐⭐⭐  
**预计时间**: 2小时  
**负责人**: Documentation Agent

#### 需要创建/修复的文件

- [ ] `.lingma/docs/architecture/agent-system/decision-log-format.md` (新建)
- [ ] `.lingma/docs/architecture/agent-system/orchestration-patterns.md` (新建)
- [ ] `.lingma/docs/architecture/agent-system/supervisor-detailed.md` (修复乱码)

#### Decision Log Format 内容要点
```markdown
# Decision Log Format

## 日志结构
{
  "timestamp": "ISO 8601",
  "task_id": "UUID",
  "decision_type": "delegation|validation|acceptance",
  "details": {...}
}

## 字段说明
...
```

#### Orchestration Patterns 内容要点
- Sequential模式详解
- Parallel模式详解
- Conditional模式详解
- Iterative模式详解
- 每种模式的适用场景和示例

#### Supervisor Detailed 修复
当前文件仅34字节乱码，需要完全重写。

---

### 🔲 任务3: 删除空/损坏文件

**重要性**: ⭐⭐⭐⭐  
**预计时间**: 10分钟  
**负责人**: 任何人

#### 需要删除的文件

- [ ] `.lingma/docs/reports/ARCHITECTURE-FIX-PLAN.md` (26 bytes)
- [ ] `.lingma/docs/architecture/agent-system/supervisor-detailed.md` (34 bytes乱码，在任务2中重建)

#### 执行命令
```bash
cd /path/to/project
rm .lingma/docs/reports/ARCHITECTURE-FIX-PLAN.md
```

---

## P1 - 高优先级（一周内完成）

### 🔲 任务4: 清理Backups目录

**重要性**: ⭐⭐⭐⭐  
**预计时间**: 30分钟  
**负责人**: 任何人

#### 当前状态
```
📁 .lingma/backups/
   总计: 20个文件, 208.56 KB
```

#### 选项A: 完全删除（推荐）
```bash
rm -rf .lingma/backups/
```

**理由**: 
- Git已有完整版本控制
- 手动备份造成冗余
- 符合"单一事实来源"原则

#### 选项B: 外部归档
```bash
mv .lingma/backups/ /path/to/external/archive/2026-04-backups/
```

**适用场景**: 
- 需要保留作为参考
- 但不希望在主仓库中

#### 决策
- [ ] 选择方案A（删除）
- [ ] 选择方案B（归档到: ____________）

---

### 🔲 任务5: 合并重复的Spec Trigger文档

**重要性**: ⭐⭐⭐⭐  
**预计时间**: 1小时  
**负责人**: Documentation Agent

#### 重复文件
```
📄 .lingma/docs/spec-trigger-hard-constraint.md (11.93 KB, 489行)
📄 .lingma/docs/guides/spec-trigger-hard-constraint.md (14.86 KB, 631行)
```

#### 执行步骤

1. **确认保留版本**
   - [ ] 保留 `guides/` 版本（更详细，631行）
   - [ ] 删除根目录版本

2. **更新所有引用**
   ```bash
   # 搜索所有引用 spec-trigger-hard-constraint.md 的文件
   grep -r "spec-trigger-hard-constraint.md" .lingma/ --include="*.md"
   
   # 确保所有引用指向 guides/ 版本
   ```

3. **删除重复文件**
   ```bash
   rm .lingma/docs/spec-trigger-hard-constraint.md
   ```

4. **验证**
   - [ ] 运行 `check_doc_integrity.py` 确认无broken links
   - [ ] 手动检查主要引用位置

---

### 🔲 任务6: 合并重复的QuickStart文档

**重要性**: ⭐⭐⭐  
**预计时间**: 30分钟  
**负责人**: Documentation Agent

#### 重复文件
```
📄 .lingma/docs/QUICKSTART.md (6.96 KB)
📄 .lingma/docs/guides/QUICK_START.md (12.60 KB)
```

#### 执行步骤

1. **比较两个文件**
   - [ ] 确认guides版本包含所有重要内容
   - [ ] 检查是否有独特信息需要合并

2. **删除根目录版本**
   ```bash
   rm .lingma/docs/QUICKSTART.md
   ```

3. **更新引用**
   - [ ] 搜索并更新所有引用QUICKSTART.md的位置
   - [ ] 改为引用 `guides/QUICK_START.md`

---

### 🔲 任务7: 补全Rules和Skills详细文档

**重要性**: ⭐⭐⭐⭐  
**预计时间**: 2小时  
**负责人**: Documentation Agent

#### 需要创建的文件

- [ ] `.lingma/docs/architecture/automation-policy-detailed.md`
- [ ] `.lingma/docs/skills/spec-driven-development-detailed.md`

#### Automation Policy Detailed 内容要点
- 自动化执行策略详解
- 安全边界和约束
- 错误处理机制
- 审计日志格式
- 与Git Hook的集成

#### Spec-Driven Development Detailed 内容要点
- SDD方法论详解
- Spec模板使用说明
- 状态转换规则
- 验证流程
- 最佳实践和反模式

---

### 🔲 任务8: 补全Specs模板文件

**重要性**: ⭐⭐⭐⭐  
**预计时间**: 1小时  
**负责人**: Spec-Driven Core Agent

#### 需要创建的文件

- [ ] `.lingma/specs/spec-template.md`

#### 内容要求
基于现有的spec文件和最佳实践，创建标准模板：

```markdown
# Spec Template

## 元数据
- ID: [自动生成]
- Title: [功能名称]
- Status: [draft|review|approved|implemented]
- Created: [日期]
- Updated: [日期]
- Author: [作者]

## 概述
[简要描述]

## 需求
### 功能性需求
1. ...
2. ...

### 非功能性需求
- 性能: ...
- 安全: ...

## 设计
[技术方案]

## 验收标准
- [ ] ...
- [ ] ...

## 测试计划
[测试策略]

## 依赖
- ...
```

#### 验证
- [ ] constitution.md 已存在 ✅
- [ ] 新模板符合constitution要求
- [ ] 有使用示例

---

## P2 - 中优先级（一个月内优化）

### 🔲 任务9: 拆分超大型文档

**重要性**: ⭐⭐⭐  
**预计时间**: 4-6小时  
**负责人**: Documentation Agent

#### 需要拆分的文件

1. **spec-driven-best-practices-2024-2026.md** (46.29 KB)
   - [ ] 按章节拆分为多个文件
   - [ ] 创建索引文件
   - [ ] 原文件移至archive或改为摘要

2. **current-spec.md** (34.43 KB)
   - [ ] 清理历史内容
   - [ ] 仅保留当前活跃Spec
   - [ ] 历史移至specs/history/

3. **improvement-action-plan.md** (29.06 KB)
   - [ ] 按Phase拆分为独立文件
   - [ ] 创建主索引
   - [ ] 完成的Phase移至archive

#### 拆分原则
- 每个文件聚焦单一主题
- 文件大小控制在10-15KB以内
- 保持清晰的导航结构
- 更新所有引用

---

### 🔲 任务10: 统一术语和命名规范

**重要性**: ⭐⭐⭐  
**预计时间**: 2小时  
**负责人**: 团队共识

#### 需要统一的术语

| 当前变体 | 统一为 | 出现频率 |
|---------|--------|---------|
| "Spec触发器" / "Spec Trigger" | "Spec Trigger" | 高频 |
| "质量门禁" / "Quality Gates" | "质量门禁 (Quality Gates)" | 中频 |
| "编排引擎" / "Orchestration Engine" | "编排引擎" | 中频 |
| "硬约束" / "Hard Constraint" | "硬约束 (Hard Constraint)" | 高频 |

#### 执行步骤

1. **创建术语表**
   - [ ] 创建 `.lingma/docs/GLOSSARY.md`
   - [ ] 列出所有专业术语和中英文对照
   - [ ] 提供使用示例

2. **批量替换**
   ```bash
   # 示例：统一Spec Trigger
   find .lingma/docs -name "*.md" -exec sed -i 's/Spec触发器/Spec Trigger/g' {} \;
   ```

3. **命名规范**
   - [ ] 文件名统一使用kebab-case
   - [ ] 避免下划线和驼峰命名
   - [ ] 使用小写字母

4. **路径规范**
   - [ ] 统一使用相对路径
   - [ ] 避免 `.lingma/` 前缀
   - [ ] 使用 `../` 向上级导航

---

### 🔲 任务11: 清理Archive目录

**重要性**: ⭐⭐  
**预计时间**: 1小时  
**负责人**: 任何人

#### 当前状态
```
📁 .lingma/docs/reports/archive/
   文件数: 37个
   总大小: 估计 ~500 KB
```

#### 清理策略

1. **分类**
   - [ ] 标记超过6个月的报告
   - [ ] 识别已失效的临时文档
   - [ ] 找出可以删除的草稿

2. **压缩归档**
   ```bash
   # 将旧报告打包
   tar -czf archive-2025-q4.tar.gz archive/report-2025-*.md
   rm archive/report-2025-*.md
   ```

3. **删除无用文件**
   - [ ] 临时草稿
   - [ ] 重复的实验记录
   - [ ] 过时的计划文档

4. **建立归档政策**
   - [ ] 报告完成后3个月移至archive
   - [ ] archive中的文件6个月后压缩
   - [ ] 1年后的archive可考虑删除

---

### 🔲 任务12: 优化Rule文件大小

**重要性**: ⭐⭐  
**预计时间**: 1小时  
**负责人**: Documentation Agent

#### 目标文件
- [ ] `rules/spec-session-start.md` (当前3.5 KB → 目标≤3 KB)

#### 优化方法
1. 提取详细内容至detailed文档
2. 简化示例代码
3. 移除冗余说明
4. 使用链接引用而非内联内容

---

## P3 - 低优先级（持续改进）

### 🔲 任务13: 建立文档自动化检查

**重要性**: ⭐⭐⭐⭐⭐  
**预计时间**: 3-4小时  
**负责人**: DevOps + Documentation Agent

#### 需要实现的自动化

1. **Git Hook: pre-commit**
   ```bash
   # .git/hooks/pre-commit
   #!/bin/bash
   python .lingma/scripts/check_doc_integrity.py --quick
   if [ $? -ne 0 ]; then
     echo "❌ 文档完整性检查失败"
     exit 1
   fi
   ```

2. **Git Hook: pre-push**
   ```bash
   # 检查文件大小
   python .lingma/scripts/doc_size_monitor.py
   ```

3. **CI/CD集成**
   ```yaml
   # .github/workflows/doc-check.yml
   name: Document Integrity Check
   on: [pull_request]
   jobs:
     check-docs:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Check doc integrity
           run: python .lingma/scripts/check_doc_integrity.py
   ```

4. **定期扫描**
   ```bash
   # 每周日凌晨2点运行
   0 2 * * 0 cd /path/to/project && python .lingma/scripts/check_doc_integrity.py >> .lingma/logs/doc-check.log
   ```

#### 交付物
- [ ] Git Hook脚本
- [ ] CI/CD配置文件
- [ ] Cron job配置（可选）
- [ ] 使用说明文档

---

### 🔲 任务14: 完善API文档同步

**重要性**: ⭐⭐⭐  
**预计时间**: 4-6小时  
**负责人**: Code Review Agent + Documentation Agent

#### 工作内容

1. **代码扫描**
   - [ ] 提取所有Python函数的docstring
   - [ ] 提取类和方法签名
   - [ ] 生成API列表

2. **文档对比**
   - [ ] 对比现有API文档
   - [ ] 识别缺失的API
   - [ ] 识别过时的API

3. **同步更新**
   - [ ] 补充缺失的API文档
   - [ ] 标记废弃的API
   - [ ] 更新参数说明

4. **自动化**
   - [ ] 创建API文档生成脚本
   - [ ] 集成到构建流程
   - [ ] 每次发布时自动更新

---

### 🔲 任务15: 创建文档索引和导航

**重要性**: ⭐⭐⭐  
**预计时间**: 2小时  
**负责人**: Documentation Agent

#### 需要创建的索引

1. **主索引**: `.lingma/docs/INDEX.md`
   ```markdown
   # 文档导航
   
   ## 快速开始
   - [QUICK_START](guides/QUICK_START.md)
   - [安装指南](skills/INSTALLATION_GUIDE.md)
   
   ## 架构设计
   - [系统架构](architecture/ARCHITECTURE.md)
   - [Agent系统](architecture/agents-usage-guide.md)
   - [编排流程](architecture/orchestration-flow.md)
   
   ## Rules
   - [AGENTS](../rules/AGENTS.md)
   - [Spec Session Start](../rules/spec-session-start.md)
   - ...
   
   ## Skills
   - [Memory Management](skills/memory-management/SKILL.md)
   - [Spec-Driven Development](skills/spec-driven-development/SKILL.md)
   
   ## 报告
   - [最新审计报告](../reports/DOCUMENT_INTEGRITY_AUDIT_SUMMARY.md)
   - [所有报告](reports/)
   ```

2. **分类索引**
   - [ ] `docs/architecture/INDEX.md`
   - [ ] `docs/guides/INDEX.md`
   - [ ] `docs/skills/INDEX.md`

3. **搜索功能**（可选）
   - [ ] 集成简单的全文搜索
   - [ ] 或使用第三方工具如DocSearch

---

## 📊 进度追踪

### 总体进度

```
P0 任务: 3个
  ✅ 完成: 0/3 (0%)
  🔄 进行中: 0/3
  🔲 未开始: 3/3

P1 任务: 5个
  ✅ 完成: 0/5 (0%)
  🔄 进行中: 0/5
  🔲 未开始: 5/5

P2 任务: 4个
  ✅ 完成: 0/4 (0%)
  🔄 进行中: 0/4
  🔲 未开始: 4/4

P3 任务: 3个
  ✅ 完成: 0/3 (0%)
  🔄 进行中: 0/3
  🔲 未开始: 3/3

总计: 15个任务
总体进度: 0%
```

### 时间规划

| 阶段 | 时间范围 | 任务 | 预期成果 |
|------|---------|------|---------|
| Phase 1 | 今天 | P0任务1-3 | 缺失链接降至~100 |
| Phase 2 | 本周内 | P1任务4-8 | 缺失链接降至~5，冗余减少80% |
| Phase 3 | 本月内 | P2任务9-12 | 文档结构优化，大小合规 |
| Phase 4 | 持续 | P3任务13-15 | 自动化检查，长期维护 |

---

## 🎯 成功标准

修复完成后应达到：

- [ ] **0个缺失链接** - 所有内部引用有效
- [ ] **0个重复内容** - 通过相似度检查
- [ ] **0个空文件** - 所有文件有实质内容
- [ ] **Agent ≤5KB** - 所有Agent文件符合规范
- [ ] **Rule ≤3KB** - 所有Rule文件符合规范（AGENTS.md ≤5KB）
- [ ] **Skill ≤10KB** - 所有Skill文件符合规范
- [ ] **docs/根目录 ≤5个文件** - 遵循单一入口原则
- [ ] **自动化检查运行中** - Git Hook + CI/CD
- [ ] **文档健康度 >95%** - 综合评分

---

## 📝 备注

### 已知问题
1. supervisor-detailed.md 文件损坏，需要完全重写
2. backups目录包含208KB的冗余备份
3. reports目录下有大量路径错误（已部分修复）

### 依赖关系
- 任务1和任务2可以并行进行
- 任务4（删除backups）应在其他任务完成后执行
- 任务13（自动化）依赖于所有手动修复完成

### 风险
- 删除backups前需确认Git历史完整
- 合并重复文档时需仔细检查引用
- 拆分大文件时可能破坏现有链接

### 建议
1. 每完成一个任务就提交Git
2. 使用branch进行大规模重构
3. 定期运行check_doc_integrity.py验证
4. 团队成员共享此清单，协同工作

---

**清单创建者**: Documentation Audit System  
**最后更新**: 2026-04-16  
**下次更新**: 每完成一个任务后更新状态
