# 系统优化计划

**版本**: v1.0  
**最后更新**: 2026-04-15  
**目标**: 全面精简 .lingma/ 下所有组件，避免拆东墙补西墙  
**原则**: 效率为王，系统化解决，一次性到位

---

## 📊 当前状态全景分析

### 问题 1: 文档过多

**.lingma/docs/ 根目录**: 10 个文档（应 ≤5）

**重复主题**:
- 优化计划: DOCS_OPTIMIZATION_PLAN.md + SYSTEM_OPTIMIZATION_PLAN.md
- 其他待检查文档

### 问题 2: Agent 文件过大

| 文件 | 当前大小 | 目标大小 | 超标 | 优先级 |
|------|---------|---------|------|--------|
| documentation-agent.md | 18.6KB | ≤5KB | +272% | P0 |
| code-review-agent.md | 14.2KB | ≤5KB | +184% | P0 |
| test-runner-agent.md | 11.6KB | ≤5KB | +132% | P0 |
| spec-driven-core-agent.md | 9.8KB | ≤5KB | +96% | P0 |
| supervisor-agent.md | ✅ 1.8KB | ≤5KB | - | ✅ 已完成 |

**总计**: 54.2KB → 目标 20KB（减少 63%）

### 问题 3: Rules 文件过大

| 文件 | 当前大小 | 目标大小 | 超标 | 优先级 |
|------|---------|---------|------|--------|
| spec-session-start.md | 15.8KB | ≤3KB | +427% | P1 |
| memory-usage.md | 13.9KB | ≤3KB | +363% | P1 |
| automation-policy.md | 11.2KB | ≤3KB | +273% | P1 |
| AGENTS.md | 9.5KB | ≤3KB | +217% | P0 |
| doc-redundancy-prevention.md | 5.3KB | ≤3KB | +77% | P2 |

**总计**: 55.7KB → 目标 15KB（减少 73%）

### 问题 4: Skills 文件过大

| 文件 | 当前大小 | 目标大小 | 超标 |
|------|---------|---------|------|
| SKILL.md | 15.5KB | ≤10KB | +55% |

---

## 🎯 优化策略

### 核心原则

1. **单一事实来源**: 每个主题只保留一份权威文档
2. **渐进式披露**: 核心指令简洁，详细内容按需查阅
3. **自动化防护**: Git Hook + CI/CD 防止回归
4. **量化标准**: Agent ≤5KB, Rule ≤3KB, Skill ≤10KB, docs root ≤5

### 执行方法

#### A. 文档合并

**步骤**:
1. 识别重复主题
2. 提取核心内容
3. 创建统一文档
4. 删除原文档
5. 更新引用链接

**已完成的合并**:
- ✅ MCP 相关: 4个 → guides/mcp-guide.md
- ✅ ROOT_CLEANLINESS: 2个 → guides/root-cleanliness.md
- ✅ RULES_INDEX: 2个 → guides/rules-index.md
- ✅ REPORT_CLEANUP: 2个 → reports/cleanup-strategy.md

**待完成的合并**:
- ⏳ 优化计划: DOCS_OPTIMIZATION_PLAN.md + SYSTEM_OPTIMIZATION_PLAN.md → 本文档

#### B. 组件精简

**步骤**:
1. 提取详细内容到 docs/architecture/
2. 保留核心指令和引用链接
3. 验证文件大小符合标准

**已完成的精简**:
- ✅ supervisor-agent.md: 10.5KB → 1.8KB (-83%)

**待完成的精简**:
- ⏳ documentation-agent.md: 18.6KB → ≤5KB
- ⏳ code-review-agent.md: 14.2KB → ≤5KB
- ⏳ test-runner-agent.md: 11.6KB → ≤5KB
- ⏳ spec-driven-core-agent.md: 9.8KB → ≤5KB
- ⏳ spec-session-start.md: 15.8KB → ≤3KB
- ⏳ memory-usage.md: 13.9KB → ≤3KB
- ⏳ automation-policy.md: 11.2KB → ≤3KB
- ⏳ AGENTS.md: 9.5KB → ≤3KB
- ⏳ doc-redundancy-prevention.md: 5.3KB → ≤3KB
- ⏳ SKILL.md: 15.5KB → ≤10KB

---

## 🚀 执行计划（分阶段）

### Phase 1: 文档合并（已完成 80%）

- [x] 合并 MCP 文档 (4→1)
- [x] 合并 ROOT_CLEANLINESS 文档 (2→1)
- [x] 合并 RULES_INDEX 文档 (2→1)
- [x] 合并 REPORT_CLEANUP 文档 (2→1)
- [ ] 合并优化计划文档 (2→1) ← **当前任务**
- [ ] 检查并合并其他重复文档

**目标**: .lingma/docs/ 根目录从 10 个减少到 ≤5 个

### Phase 2: Agent 精简（进行中）

- [x] supervisor-agent.md: 10.5KB → 1.8KB (-83%)
- [ ] documentation-agent.md: 18.6KB → ≤5KB
- [ ] code-review-agent.md: 14.2KB → ≤5KB
- [ ] test-runner-agent.md: 11.6KB → ≤5KB
- [ ] spec-driven-core-agent.md: 9.8KB → ≤5KB

**目标**: Agents 总大小从 54.2KB 减少到 ≤20KB

### Phase 3: Rules 精简（待开始）

- [ ] spec-session-start.md: 15.8KB → ≤3KB
- [ ] memory-usage.md: 13.9KB → ≤3KB
- [ ] automation-policy.md: 11.2KB → ≤3KB
- [ ] AGENTS.md: 9.5KB → ≤3KB
- [ ] doc-redundancy-prevention.md: 5.3KB → ≤3KB

**目标**: Rules 总大小从 55.7KB 减少到 ≤15KB

### Phase 4: Skills 精简（待开始）

- [ ] SKILL.md: 15.5KB → ≤10KB

---

## 🛡️ 自动化防护

### 1. Git Hook 拦截

```bash
# .git/hooks/pre-commit
# 检查 .lingma/docs/ 根目录文档数量
DOCS_ROOT_COUNT=$(git diff --cached --name-only --diff-filter=A | grep "^\.lingma/docs/[^/]*\.md$" | wc -l)

if [ $DOCS_ROOT_COUNT -gt 0 ]; then
    echo "⚠️  警告: 在 .lingma/docs/ 根目录添加了 $DOCS_ROOT_COUNT 个文档"
    read -p "是否继续提交? (y/N): " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

### 2. CI/CD 定期扫描

```yaml
# .github/workflows/system-health-check.yml
schedule:
  - cron: '0 9 * * 1'  # 每周一上午9点
```

运行脚本:
- `scripts/full_system_scan.py` - 全盘扫描
- `scripts/batch_optimize_components.py` - 批量优化检查
- `scripts/verify_system_effectiveness.py` - 有效性验证

### 3. 防重复机制

**规则**: 创建任何新条目前必须 grep 检查是否已存在

```bash
# 示例
grep -r "被动响应问题教训" .lingma/rules/AGENTS.md
# 如果已存在，更新现有条目而非创建新的
```

---

## 📊 监控指标

| 指标 | 目标 | 当前状态 | 进度 |
|------|------|----------|------|
| docs/ 根目录文档数 | ≤5 | 10 | 50% ❌ |
| Agent 总大小 | ≤20KB | 54.2KB | 19% ❌ |
| Rule 总大小 | ≤15KB | 55.7KB | 0% ❌ |
| Skill 总大小 | ≤10KB | 15.5KB | 0% ❌ |
| 重复主题文档 | 0 | 1组 | 80% ✅ |

---

## 💡 最佳实践

### 1. 创建前先思考

- 这个内容是否已存在？
- 是否可以合并到现有文档？
- 是否符合量化标准？

### 2. 定期检查

```bash
# 每周检查
python scripts/full_system_scan.py

# 查看待优化组件
python scripts/batch_optimize_components.py
```

### 3. 及时清理

- 报告生成后立即评估是否需要保留
- 过时的 Phase 报告归档
- 临时文档用完后删除

---

## 🔗 相关资源

- [全盘扫描工具](../../scripts/full_system_scan.py)
- [批量优化工具](../../scripts/batch_optimize_components.py)
- [有效性验证](../../scripts/verify_system_effectiveness.py)
- [CI/CD 工作流](../../.github/workflows/system-health-check.yml)
- [使命宣言](../MISSION_STATEMENT.md)

---

## 📅 更新历史

- **2026-04-15**: 创建统一的系统优化计划
- 合并 DOCS_OPTIMIZATION_PLAN.md 和 SYSTEM_OPTIMIZATION_PLAN.md
- 记录当前进度和待完成任务
