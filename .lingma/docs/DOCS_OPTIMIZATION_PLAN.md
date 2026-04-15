# 文档精简优化计划

**问题**: `.lingma/docs/` 有 16 个文档，严重过多，违反单一入口原则  
**目标**: 精简至 ≤8 个核心文档  
**策略**: 合并相似主题 + 归档过时内容

---

## 📊 当前问题分析

### 重复文档（必须合并）

| 主题 | 文档1 | 文档2 | 操作 |
|------|-------|-------|------|
| **根目录清洁** | ROOT_CLEANLINESS_AND_TEMP_FILE_PREVENTION.md (16.3KB) | ROOT_DIRECTORY_CLEANLINESS.md (7.1KB) | 合并为 1 个 |
| **MCP配置** | MCP_CONFIG_MANAGEMENT.md (8.1KB)<br>MCP_QUICK_VERIFICATION.md (5.4KB)<br>MCP_TEST_CHECKLIST.md (5.7KB)<br>MCP_USAGE_GUIDE.md (10.3KB) | - | 合并为 1 个 |
| **Rules索引** | RULES_INDEX.md (1.8KB) | rules-registry.md (3.3KB) | 合并为 1 个 |
| **报告策略** | REPORT_CLEANUP_STRATEGY.md (17.0KB) | OPTIMIZATION_REPORT.md (0.5KB) | 合并为 1 个 |

---

## 🎯 优化方案

### 方案：合并为 8 个核心文档

```
.lingma/docs/
├── architecture/
│   └── ARCHITECTURE.md              # 架构文档（保留）
├── guides/
│   ├── QUICK_START.md               # 快速开始（保留）
│   ├── agents-usage.md              # Agent 使用指南（合并 AGENTS_USAGE_GUIDE）
│   ├── mcp-guide.md                 # MCP 完整指南（合并 4 个 MCP 文档）
│   ├── root-cleanliness.md          # 根目录清洁（合并 2 个清洁文档）
│   ├── rules-index.md               # Rules 索引（合并 2 个索引）
│   ├── doc-self-healing.md          # 文档自检测（保留 DOC_SELF_HEALING_SYSTEM）
│   ├── verification-guide.md        # 验证指南（保留 VERIFICATION_GUIDE）
│   └── optimization-plan.md         # 优化计划（合并 SYSTEM_OPTIMIZATION_PLAN + refactor-plan）
└── reports/                         # 新建：报告归档目录
    ├── cleanup-strategy.md          # 报告清理策略
    └── optimization-report.md       # 优化报告
```

**预期效果**: 
- 根目录: 0 个文档（全部移至子目录）
- guides/: 8 个核心文档
- reports/: 2 个报告文档
- **总计**: 10 个文档（从 16 个减少 38%）

---

## 🚀 执行步骤

### Phase 1: 创建子目录结构
```bash
mkdir .lingma\docs\guides
mkdir .lingma\docs\reports
```

### Phase 2: 移动文档到子目录
```bash
# 移动现有文档
move .lingma\docs\ARCHITECTURE.md .lingma\docs\architecture\
move .lingma\docs\QUICK_START.md .lingma\docs\guides\
move .lingma\docs\AGENTS_USAGE_GUIDE.md .lingma\docs\guides\agents-usage.md
move .lingma\docs\DOC_SELF_HEALING_SYSTEM.md .lingma\docs\guides\doc-self-healing.md
move .lingma\docs\VERIFICATION_GUIDE.md .lingma\docs\guides\verification-guide.md
```

### Phase 3: 合并重复文档
```bash
# 1. 合并根目录清洁文档
# 2. 合并 MCP 文档
# 3. 合并 Rules 索引
# 4. 合并报告策略
```

### Phase 4: 删除冗余文档
```bash
# 删除已合并的原文档
```

---

## 💡 核心教训

**错误**: 
- ❌ 创建了过多文档（16个）
- ❌ 相同主题有多个文档
- ❌ 违反了"单一入口原则"

**正确做法**:
- ✅ 每个主题仅 1 个文档
- ✅ 使用子目录组织（guides/, reports/, architecture/）
- ✅ 定期审查和合并

---

**下一步**: 等待确认后执行合并操作
