# 质量门禁标准 (Quality Gates)

**版本**: 1.0  
**最后更新**: 2026-04-16  
**维护者**: Supervisor Agent  

---

## 📋 概述

本系统采用 **5层质量门禁 (Quality Gates)** 机制,确保所有代码变更、功能开发和文档更新都符合严格的质量标准。任何一层门禁失败都会导致整个任务链终止,无法绕过。

### 核心原则

1. **强制执行**: 所有门禁必须通过,无例外
2. **自动化优先**: 尽可能使用自动化工具验证
3. **量化标准**: 所有指标都有明确的数值阈值
4. **透明可追溯**: 每次检查的结果都记录在决策日志中

---

## 🚪 Gate 1: Agent自检 (Self-Validation)

**执行者**: 每个Worker Agent自身  
**触发时机**: 任务完成后立即执行  
**目标**: 确保Agent输出的基本正确性和完整性

### 检查项

#### 1.1 代码规范 (Code Style)
- **工具**: Black (Python), Prettier (TypeScript/JavaScript), rustfmt (Rust)
- **标准**:
  - Python: `black --check` 通过率 100%
  - TypeScript: `prettier --check` 通过率 100%
  - Rust: `cargo fmt --check` 通过率 100%
- **失败处理**: 自动格式化后重新提交

#### 1.2 类型检查 (Type Checking)
- **工具**: mypy (Python), tsc --noEmit (TypeScript)
- **标准**:
  - Python: `mypy --strict` 零错误
  - TypeScript: `tsc --noEmit` 零错误
- **允许忽略**: 使用 `# type: ignore` 时必须添加注释说明原因

#### 1.3 单元测试覆盖 (Unit Test Coverage)
- **工具**: pytest-cov (Python), vitest --coverage (TypeScript)
- **标准**:
  - 行覆盖率 (Line Coverage): ≥ 80%
  - 分支覆盖率 (Branch Coverage): ≥ 70%
  - 函数覆盖率 (Function Coverage): ≥ 85%
- **排除项**: 
  - 生成的代码 (generated/)
  - 测试文件本身 (__tests__/, tests/)
  - 配置文件 (.config.js, .toml)

#### 1.4 基本功能验证
- **要求**: Agent必须验证自己的输出是否符合任务要求
- **检查点**:
  - 文件是否成功创建/修改
  - 语法是否正确 (可解析)
  - 关键依赖是否满足

### 通过标准

```python
gate_1_passed = (
    code_style_check == PASS and
    type_checking == PASS and
    test_coverage >= 80% and
    basic_validation == PASS
)
```

### 失败示例

```json
{
  "gate": "gate_1_self_validation",
  "passed": false,
  "failures": [
    {
      "check": "test_coverage",
      "expected": ">= 80%",
      "actual": "65%",
      "file": "src/utils/format.py"
    }
  ]
}
```

---

## 🚪 Gate 2: 测试验证 (Test Runner)

**执行者**: Test Runner Agent  
**触发时机**: Gate 1通过后  
**目标**: 确保代码在各种场景下都能正确运行

### 检查项

#### 2.1 集成测试 (Integration Tests)
- **工具**: pytest (Python), vitest (TypeScript), cargo test (Rust)
- **标准**:
  - 所有集成测试用例 100% 通过
  - 测试执行时间 < 5分钟 (单模块)
  - 无 flaky tests (重试3次结果一致)

#### 2.2 E2E测试 (End-to-End Tests)
- **工具**: Playwright
- **标准**:
  - 关键用户路径 100% 通过
  - 跨浏览器测试 (Chrome, Firefox, Edge)
  - 响应时间 P95 < 2秒

#### 2.3 性能基准测试 (Performance Benchmarks)
- **工具**: pytest-benchmark, benchmark.js
- **标准**:
  - 关键函数性能退化 < 5%
  - 内存使用增长 < 10%
  - CPU使用率峰值 < 80%

#### 2.4 回归测试 (Regression Tests)
- **要求**: 确保新代码不破坏现有功能
- **策略**:
  - 运行全量测试套件
  - 对比历史测试结果
  - 检测意外的行为变化

### 通过标准

```python
gate_2_passed = (
    integration_tests == ALL_PASS and
    e2e_tests == ALL_PASS and
    performance_regression < 5% and
    no_regressions_detected
)
```

### 测试报告格式

```json
{
  "gate": "gate_2_test_runner",
  "passed": true,
  "summary": {
    "total_tests": 156,
    "passed": 156,
    "failed": 0,
    "skipped": 3,
    "duration_seconds": 42.5
  },
  "coverage": {
    "line": 85.2,
    "branch": 72.8,
    "function": 88.5
  },
  "performance": {
    "avg_response_time_ms": 120,
    "p95_response_time_ms": 450,
    "memory_usage_mb": 256
  }
}
```

---

## 🚪 Gate 3: 代码审查 (Code Review)

**执行者**: Code Review Agent  
**触发时机**: Gate 2通过后  
**目标**: 确保代码质量、可维护性和安全性

### 检查项

#### 3.1 代码复杂度 (Code Complexity)
- **工具**: radon (Python), complexity-report (JS), clippy (Rust)
- **标准**:
  - 圈复杂度 (Cyclomatic Complexity): < 10
  - 认知复杂度 (Cognitive Complexity): < 15
  - 单个函数行数: < 50行
  - 单个文件行数: < 500行

#### 3.2 代码重复率 (Code Duplication)
- **工具**: pymetrics (Python), jscpd (JS), duplicheck (Rust)
- **标准**:
  - 重复代码比例: < 5%
  - 最小重复块: 10行
  - 允许的重复: 样板代码、自动生成代码

#### 3.3 安全漏洞扫描 (Security Scan)
- **工具**: bandit (Python), npm audit (JS), cargo-audit (Rust)
- **标准**:
  - 高危漏洞 (High/Critical): 0个
  - 中危漏洞 (Medium): ≤ 2个 (必须有缓解措施)
  - 低危漏洞 (Low): 记录但不阻塞

#### 3.4 最佳实践检查 (Best Practices)
- **检查点**:
  - ✅ 遵循 SOLID 原则
  - ✅ DRY (Don't Repeat Yourself)
  - ✅ KISS (Keep It Simple, Stupid)
  - ✅ YAGNI (You Aren't Gonna Need It)
  - ✅ 适当的错误处理
  - ✅ 日志记录完整
  - ✅ 资源清理 (文件句柄、数据库连接等)

#### 3.5 代码可读性 (Readability)
- **评分维度**:
  - 命名清晰度 (1-10分): ≥ 7
  - 注释充分性 (1-10分): ≥ 6
  - 结构合理性 (1-10分): ≥ 8
  - 一致性 (1-10分): ≥ 8

### 评分算法

```python
code_review_score = (
    complexity_score * 0.25 +      # 25% 权重
    duplication_score * 0.20 +     # 20% 权重
    security_score * 0.30 +        # 30% 权重
    best_practices_score * 0.15 +  # 15% 权重
    readability_score * 0.10       # 10% 权重
)

# 归一化到 0-100 分
normalized_score = min(100, max(0, code_review_score * 100))
```

### 通过标准

```python
gate_3_passed = (
    code_review_score >= 80 and
    critical_security_issues == 0 and
    high_complexity_functions == 0
)
```

### 审查报告示例

```json
{
  "gate": "gate_3_code_review",
  "passed": true,
  "score": 87.5,
  "breakdown": {
    "complexity": {"score": 9.2, "max_allowed": 10, "status": "PASS"},
    "duplication": {"percentage": 3.2, "max_allowed": 5, "status": "PASS"},
    "security": {
      "critical": 0,
      "high": 0,
      "medium": 1,
      "low": 3,
      "status": "PASS"
    },
    "best_practices": {"violations": 2, "status": "WARNING"},
    "readability": {"average_score": 8.1, "status": "PASS"}
  },
  "recommendations": [
    "考虑将 function_x 拆分为更小的函数 (当前复杂度: 12)",
    "修复中等安全风险: 未 sanitization 的用户输入"
  ]
}
```

---

## 🚪 Gate 4: 文档完整性 (Documentation Check)

**执行者**: Documentation Agent  
**触发时机**: Gate 3通过后  
**目标**: 确保代码变更有完整的文档支持

### 检查项

#### 4.1 API文档 (API Documentation)
- **工具**: Sphinx (Python), TypeDoc (TypeScript), rustdoc (Rust)
- **标准**:
  - 所有公共函数/类必须有 docstring/JSDoc
  - 参数、返回值、异常都有说明
  - 提供使用示例
  - 文档可成功构建 (无警告)

#### 4.2 架构决策记录 (ADR - Architecture Decision Records)
- **要求**: 重大架构变更必须创建 ADR
- **模板**:
  ```markdown
  # ADR-XXX: [决策标题]
  
  ## 状态
  [提议/接受/废弃]
  
  ## 背景
  [为什么需要做这个决策]
  
  ## 决策
  [我们决定做什么]
  
  ## 后果
  [这个决策带来的影响]
  ```
- **存储位置**: `.lingma/docs/architecture/adr/`

#### 4.3 变更日志 (CHANGELOG)
- **标准**: 遵循 [Keep a Changelog](https://keepachangelog.com/) 格式
- **分类**:
  - `Added`: 新功能
  - `Changed`: 现有功能变更
  - `Deprecated`: 即将移除的功能
  - `Removed`: 已移除的功能
  - `Fixed`: Bug修复
  - `Security`: 安全相关修复
- **要求**: 每个用户可见的变更都必须记录

#### 4.4 用户指南同步 (User Guide Sync)
- **检查点**:
  - README.md 是否反映最新功能
  - 快速开始指南是否仍然有效
  - 配置选项是否有完整说明
  - 故障排查章节是否覆盖常见问题

#### 4.5 代码注释质量
- **标准**:
  - 复杂逻辑必须有注释解释 WHY (而非 WHAT)
  - TODO/FIXME 必须有负责人和截止日期
  - 魔法数字/字符串必须定义为常量并注释

### 通过标准

```python
gate_4_passed = (
    api_docs_complete and
    adr_created_if_needed and
    changelog_updated and
    user_guide_synced and
    code_comments_adequate
)
```

### 文档检查报告

```json
{
  "gate": "gate_4_documentation",
  "passed": true,
  "checks": {
    "api_docs": {
      "coverage": 95.5,
      "missing_docstrings": 2,
      "build_warnings": 0,
      "status": "PASS"
    },
    "adr": {
      "required": true,
      "created": true,
      "file": ".lingma/docs/architecture/adr/ADR-042-async-refactor.md",
      "status": "PASS"
    },
    "changelog": {
      "updated": true,
      "entries_added": 5,
      "format_valid": true,
      "status": "PASS"
    },
    "user_guide": {
      "readme_updated": true,
      "quick_start_validated": true,
      "status": "PASS"
    }
  }
}
```

---

## 🚪 Gate 5: Supervisor最终验收 (Final Acceptance)

**执行者**: Supervisor Agent  
**触发时机**: Gate 1-4全部通过后  
**目标**: 综合评估整体质量,做出最终决策

### 评估维度

#### 5.1 综合评分计算

```python
# 加权平均算法
final_score = (
    gate1_score * 0.20 +    # Agent自检: 20%
    gate2_score * 0.30 +    # 测试验证: 30% (最重要)
    gate3_score * 0.25 +    # 代码审查: 25%
    gate4_score * 0.15 +    # 文档完整性: 15%
    gate5_manual_bonus      # 人工加分项: 0-10分
)

# 归一化到 0-100
normalized_final_score = min(100, max(0, final_score))
```

#### 5.2 回归测试验证
- **要求**: 运行全量回归测试套件
- **标准**:
  - 所有历史测试用例 100% 通过
  - 性能指标无显著退化 (< 5%)
  - 无新增的安全漏洞

#### 5.3 人工审批阈值
- **自动通过**: 综合评分 ≥ 90
- **需要人工审查**: 85 ≤ 评分 < 90
- **自动拒绝**: 评分 < 85

#### 5.4 风险评估
- **风险等级**:
  - 🟢 低风险: 文档更新、小Bug修复
  - 🟡 中风险: 新功能、重构非核心模块
  - 🟠 高风险: 核心模块重构、数据库迁移
  - 🔴 极高风险: 架构变更、生产数据操作

- **审批要求**:
  - 低风险: Supervisor自动批准
  - 中风险: 需要1名高级工程师审查
  - 高风险: 需要2名高级工程师 + Tech Lead批准
  - 极高风险: 需要架构委员会审批

### 通过标准

```python
gate_5_passed = (
    all_previous_gates_passed and
    final_score >= 85 and
    regression_tests_pass and
    risk_level_approved
)
```

### 最终验收报告

```json
{
  "gate": "gate_5_supervisor_acceptance",
  "passed": true,
  "final_score": 92.3,
  "breakdown": {
    "gate_1": {"score": 95.0, "weight": 0.20, "weighted": 19.0},
    "gate_2": {"score": 90.5, "weight": 0.30, "weighted": 27.15},
    "gate_3": {"score": 87.5, "weight": 0.25, "weighted": 21.88},
    "gate_4": {"score": 93.0, "weight": 0.15, "weighted": 13.95},
    "manual_bonus": 10.0
  },
  "regression_tests": {
    "total": 1250,
    "passed": 1250,
    "failed": 0,
    "status": "PASS"
  },
  "risk_assessment": {
    "level": "MEDIUM",
    "requires_human_approval": true,
    "approved_by": ["senior-dev-001"],
    "approval_timestamp": "2026-04-16T15:30:00Z"
  },
  "verdict": "ACCEPTED",
  "confidence": 0.95,
  "recommendations": [
    "建议在下一个迭代中优化 function_x 的性能",
    "考虑为 module_y 添加更多的集成测试"
  ]
}
```

---

## 🔄 失败处理流程

### 自动重试机制

当某层门禁失败时:

1. **第一次失败**: 
   - 记录失败原因
   - 自动尝试修复 (如果可能)
   - 重新执行该层门禁

2. **第二次失败**:
   - 通知相关负责人
   - 生成详细的失败报告
   - 等待人工干预

3. **第三次失败**:
   - 标记任务为 FAILED
   - 回滚所有变更
   - 创建 GitHub Issue 追踪问题

### 回滚策略

```python
if gate_failed and retry_count >= 3:
    # 1. 回滚文件变更
    git_reset --hard HEAD
    
    # 2. 清理临时文件
    cleanup_temp_files()
    
    # 3. 恢复数据库快照 (如果有)
    restore_database_snapshot()
    
    # 4. 通知团队
    send_notification(
        channel="#dev-alerts",
        message=f"Task {task_id} failed at {failed_gate}. Rolled back."
    )
    
    # 5. 创建Issue
    create_github_issue(
        title=f"[FAILED] Task {task_id} - {failed_gate}",
        body=generate_failure_report(),
        labels=["quality-gate-failed", "needs-investigation"]
    )
```

---

## 📊 监控和度量

### 关键指标

| 指标 | 说明 | 目标 |
|------|------|------|
| Gate通过率 | 各层门禁的通过比例 | > 90% |
| 平均修复时间 | 从失败到重新通过的时间 | < 2小时 |
| 误报率 | 错误的失败判定比例 | < 1% |
| 自动化率 | 自动通过的门禁比例 | > 80% |
| 人工介入频率 | 需要人工审查的比例 | < 20% |

### 仪表盘

所有质量门禁的结果都会推送到监控仪表盘:

- **实时状态**: 当前正在执行的门禁
- **历史趋势**: 过去30天的通过率
- **瓶颈分析**: 哪层门禁最常失败
- **团队表现**: 各开发者的代码质量评分

---

## 🎓 最佳实践

### 1. 预防胜于治疗
- 在本地开发时就运行所有检查
- 使用 pre-commit hooks 自动格式化
- IDE 集成 linter 和 type checker

### 2. 持续改进
- 定期回顾失败的门禁,找出根本原因
- 根据团队反馈调整阈值
- 自动化新的检查项

### 3. 平衡速度与质量
- 低风险变更可以放宽某些检查
- 核心模块必须严格执行所有门禁
- 紧急修复可以先合并后补文档 (但必须在24小时内补齐)

### 4. 透明沟通
- 失败时提供清晰的错误信息
- 给出具体可行的修复建议
- 记录所有决策和理由

---

## 📚 相关文档

- [Supervisor Agent 详细指南](supervisor-detailed.md)
- [Decision Log 格式规范](decision-log-format.md)
- [Orchestration Patterns](orchestration-patterns.md)
- [Agent System Architecture](../ARCHITECTURE.md)

---

**维护说明**: 本文档应随系统演进而更新。每次修改质量门禁标准时,必须:
1. 更新版本号
2. 在 CHANGELOG 中记录变更
3. 通知所有团队成员
4. 更新相关的自动化脚本
