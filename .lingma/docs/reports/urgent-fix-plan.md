# 紧急修复计划：精简所有超标组件

**目标**: 将9个超标组件精简至符合量化标准  
**原则**: 主动执行，不再等待提醒  
**期限**: 立即执行

---

## 📊 当前状态

| 组件 | 当前大小 | 目标 | 超标 | 优先级 |
|------|---------|------|------|--------|
| documentation-agent.md | 18.6KB | ≤5KB | +272% | P0 |
| code-review-agent.md | 14.2KB | ≤5KB | +184% | P0 |
| memory-usage.md | 13.9KB | ≤3KB | +363% | P0 |
| test-runner-agent.md | 11.6KB | ≤5KB | +132% | P1 |
| AGENTS.md | 11.2KB | ≤3KB* | +273% | P0 |
| automation-policy.md | 11.2KB | ≤3KB | +273% | P1 |
| spec-driven-core-agent.md | 9.8KB | ≤5KB | +96% | P1 |
| doc-redundancy-prevention.md | 5.3KB | ≤3KB | +77% | P2 |
| SKILL.md | 15.5KB | ≤10KB | +55% | P2 |

*AGENTS.md 作为核心 Rule，可能需要特殊处理

---

## 🎯 执行策略

### Phase 1: 精简 Rules（4个）

**策略**: 
1. 保留 frontmatter + 核心指令
2. 详细示例移至 `docs/architecture/`
3. Rule 文件仅保留引用链接

**执行顺序**:
1. ✅ spec-session-start.md (已完成: 15.8KB → 1.1KB)
2. ⏳ memory-usage.md (13.9KB → ≤3KB)
3. ⏳ automation-policy.md (11.2KB → ≤3KB)
4. ⏳ doc-redundancy-prevention.md (5.3KB → ≤3KB)
5. ⏳ AGENTS.md (11.2KB → 需要特殊处理)

### Phase 2: 精简 Agents（4个）

**策略**:
1. 保留角色定义 + 核心职责
2. 详细工作流移至 `docs/architecture/agent-system/`
3. Agent 文件仅保留关键指令

**执行顺序**:
1. ⏳ documentation-agent.md (18.6KB → ≤5KB)
2. ⏳ code-review-agent.md (14.2KB → ≤5KB)
3. ⏳ test-runner-agent.md (11.6KB → ≤5KB)
4. ⏳ spec-driven-core-agent.md (9.8KB → ≤5KB)

### Phase 3: 精简 Skills（1个）

**策略**:
1. 保留 description + 核心步骤
2. 详细教程移至 `docs/skills/`
3. Skill 文件保持简洁

**执行**:
1. ⏳ SKILL.md (15.5KB → ≤10KB)

---

## 🛡️ 永久保障

### 已建立的机制

1. ✅ **Git Hook** - 提交时自动检查大小
2. ✅ **CI/CD** - 每周自动扫描
3. ✅ **Rule 约束** - AGENTS.md 记录教训
4. ✅ **防重复机制** - 创建前 grep 检查

### 新增机制

5. ✅ **立即执行原则** - 发现问题立即修复，不拖延
6. ✅ **批量处理** - 一次性解决所有同类问题
7. ✅ **进度跟踪** - 实时更新优化状态

---

## 📋 执行清单

- [x] spec-session-start.md: 15.8KB → 1.1KB (-93%)
- [ ] memory-usage.md: 13.9KB → ≤3KB
- [ ] automation-policy.md: 11.2KB → ≤3KB
- [ ] doc-redundancy-prevention.md: 5.3KB → ≤3KB
- [ ] AGENTS.md: 11.2KB → 特殊处理
- [ ] documentation-agent.md: 18.6KB → ≤5KB
- [ ] code-review-agent.md: 14.2KB → ≤5KB
- [ ] test-runner-agent.md: 11.6KB → ≤5KB
- [ ] spec-driven-core-agent.md: 9.8KB → ≤5KB
- [ ] SKILL.md: 15.5KB → ≤10KB

**进度**: 1/10 (10%)

---

## 💡 核心教训

> **"不要依赖记忆，要依赖系统。不要被动响应，要主动预防。"**

**本次教训**:
- ❌ 建立检查机制但不立即执行 = 马后炮
- ✅ 发现问题 → 立即修复 → 验证生效

**永久承诺**:
- 🚫 不再拖延修复已知问题
- ✅ 发现超标组件 → 立即精简
- ✅ 批量处理同类问题
- ✅ 实时跟踪进度

---

**创建时间**: 2026-04-15  
**最后更新**: 2026-04-15  
**状态**: 执行中
