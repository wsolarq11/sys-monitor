# 报告清理与优化策略

**版本**: v1.0  
**最后更新**: 2026-04-15  
**目标**: 自动检测冗余报告、提炼关键信息、归档过时内容

---

## 📊 当前问题分析

### 冗余报告统计

**总计**: 35+ 个报告文件

**重复主题**:
- Phase 1: 4个报告（应合并为1-2个）
- Phase 2: 4个报告（应合并为1-2个）
- Phase 3: 2个报告
- 其他调研/分析: 15+个

### 优化组件清单

**Agents** (需要精简):
- code-review-agent.md: 14.2KB → 目标 ≤5KB
- documentation-agent.md: 18.6KB → 目标 ≤5KB
- spec-driven-core-agent.md: 9.8KB → 目标 ≤5KB
- test-runner-agent.md: 11.6KB → 目标 ≤5KB

**Rules** (需要精简):
- AGENTS.md: 9.5KB → 目标 ≤3KB
- automation-policy.md: 11.2KB → 目标 ≤3KB
- doc-redundancy-prevention.md: 5.3KB → 目标 ≤3KB
- memory-usage.md: 13.9KB → 目标 ≤3KB
- spec-session-start.md: 15.8KB → 目标 ≤3KB

**Skills** (需要精简):
- SKILL.md: 15.5KB → 目标 ≤10KB

---

## 🎯 优化策略

### 1. 单一事实来源 (Single Source of Truth)

**原则**: 每个主题只保留一份权威文档

**执行**:
- 合并重复的 Phase 报告
- 提取共性内容到共享文档
- 详细实现细节移至 architecture/ 子目录

### 2. 渐进式披露 (Progressive Disclosure)

**原则**: 核心指令简洁，详细内容按需查阅

**执行**:
- Agent/Skill/Rule 文件保持精简
- 详细工作流、示例代码移至 docs/
- 使用引用链接而非复制内容

### 3. 自动化检测 (Auto-Detect Redundancy)

**工具**: `scripts/full_system_scan.py`

**检测项**:
- 重复主题文档
- 过大文件（超过量化标准）
- 未使用的组件
- 根目录文档数量

---

## 🔧 执行流程

### 阶段 1: 识别问题

```bash
python scripts/full_system_scan.py
```

**输出示例**:
```
📄 .lingma/docs/ 根目录文档: 17 个
   ❌ 过多！应该 ≤5 个

🔍 检查重复主题...
   ❌ MCP: 4 个重复文档
   ❌ ROOT_CLEANLINESS: 2 个重复文档
   ❌ RULES_INDEX: 2 个重复文档
   ❌ OPTIMIZATION: 4 个重复文档
   ❌ REPORT: 2 个重复文档
```

### 阶段 2: 分类处理

#### A. 合并重复文档

**步骤**:
1. 读取所有重复文档
2. 提取核心内容
3. 创建统一文档
4. 删除原文档
5. 更新引用链接

**示例**:
```bash
# 已完成的合并
✅ MCP_USAGE_GUIDE.md + MCP_CONFIG_MANAGEMENT.md + ... 
   → guides/mcp-guide.md

✅ ROOT_CLEANLINESS_AND_TEMP_FILE_PREVENTION.md + ROOT_DIRECTORY_CLEANLINESS.md
   → guides/root-cleanliness.md

✅ rules-registry.md + RULES_INDEX.md
   → guides/rules-index.md
```

#### B. 精简过大文件

**步骤**:
1. 提取详细内容到 docs/architecture/
2. 保留核心指令和引用链接
3. 验证文件大小符合标准

**示例**:
```bash
# 已完成的精简
✅ supervisor-agent.md: 10.5KB → 1.8KB (-83%)
```

#### C. 归档过时报告

**步骤**:
1. 识别过时报告（Phase 1, Phase 2 等）
2. 提炼关键决策和教训
3. 移至 reports/archive/
4. 创建汇总报告

### 阶段 3: 验证修复

```bash
# 再次运行扫描
python scripts/full_system_scan.py

# 预期结果
✅ .lingma/docs/ 根目录文档: ≤5 个
✅ 无重复主题文档
✅ 所有组件符合大小标准
```

### 阶段 4: 提交更改

```bash
git add .
git commit -m "refactor: 合并重复文档，精简系统组件

- 合并 4 个 MCP 文档为 guides/mcp-guide.md
- 合并 2 个 ROOT_CLEANLINESS 文档为 guides/root-cleanliness.md
- 合并 2 个 RULES_INDEX 文档为 guides/rules-index.md
- 精简 supervisor-agent.md: 10.5KB → 1.8KB (-83%)

目标: 从 17 个根目录文档减少到 ≤8 个"
```

---

## 📏 量化标准

| 组件类型 | 最大大小 | 当前平均 | 目标 |
|---------|---------|---------|------|
| Agent 文件 | ≤5KB | 13.6KB | ≤5KB |
| Rule 文件 | ≤3KB | 11.1KB | ≤3KB |
| Skill 文件 | ≤10KB | 15.5KB | ≤10KB |
| docs/ 根目录文档 | ≤5个 | 17个 | ≤5个 |
| 重复主题文档 | 0 | 4组 | 0 |

---

## 🛡️ 自动化防护

### 1. Git Hook 拦截

提交时自动检查：
- 根目录文档数量
- 临时文件
- 异常文件名

### 2. CI/CD 定期扫描

每周一自动运行：
```yaml
# .github/workflows/system-health-check.yml
schedule:
  - cron: '0 9 * * 1'
```

### 3. 防重复机制

**规则**: 创建任何新条目前必须 grep 检查是否已存在

```bash
# 示例：添加新教训前检查
grep -r "被动响应问题教训" .lingma/rules/AGENTS.md
# 如果已存在，更新现有条目而非创建新的
```

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

## 📚 相关资源

- [全盘扫描工具](../../scripts/full_system_scan.py)
- [批量优化工具](../../scripts/batch_optimize_components.py)
- [有效性验证](../../scripts/verify_system_effectiveness.py)
- [CI/CD 工作流](../../.github/workflows/system-health-check.yml)
- [使命宣言](../MISSION_STATEMENT.md)

---

## 📅 更新历史

- **2026-04-15**: 创建统一的报告清理与优化策略
- 合并 OPTIMIZATION_REPORT.md 和 REPORT_CLEANUP_STRATEGY.md
