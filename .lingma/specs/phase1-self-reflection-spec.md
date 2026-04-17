# Phase 1: 自我反思机制实施 Spec

**版本**: 1.0  
**状态**: draft  
**优先级**: P0  
**预计完成时间**: 1周 (2026-04-17 to 2026-04-24)

---

## 📋 概述

本 Spec 定义自迭代流系统的第一阶段：**自我反思机制**。目标是让 Agent 能够在执行任务后自动评估结果质量，识别问题，并生成改进建议。

### 业务价值
- 提高输出质量 30%+
- 减少重复错误 50%+
- 实现持续自我改进
- 降低人工审查成本

### 成功标准
- [ ] AC-001: 90% 的任务执行后有质量评估
- [ ] AC-002: 能识别 80% 的常见问题类型
- [ ] AC-003: 生成的改进建议准确率 > 70%
- [ ] AC-004: 反思过程性能开销 < 10%
- [ ] AC-005: 所有反思结果可追溯和审计

---

## 🎯 需求规格

### FR-001: 质量评估引擎

**描述**: 基于多维度标准评估任务执行结果的质量

**验收标准**:
- [ ] AC-001-01: 支持代码质量评估（正确性、可读性、性能）
- [ ] AC-001-02: 支持文档质量评估（完整性、清晰度、准确性）
- [ ] AC-001-03: 支持配置质量评估（规范性、安全性、可维护性）
- [ ] AC-001-04: 可配置的质量阈值
- [ ] AC-001-05: 生成详细的质量报告

**优先级**: Must have

---

### FR-002: 问题识别系统

**描述**: 自动识别执行结果中的问题和不足

**验收标准**:
- [ ] AC-002-01: 识别语法和逻辑错误
- [ ] AC-002-02: 检测最佳实践违反
- [ ] AC-002-03: 发现潜在的性能问题
- [ ] AC-002-04: 标记安全风险
- [ ] AC-002-05: 分类问题严重程度

**优先级**: Must have

---

### FR-003: 改进建议生成

**描述**: 基于识别的问题生成具体的改进建议

**验收标准**:
- [ ] AC-003-01: 每个问题至少一个改进建议
- [ ] AC-003-02: 建议具体可执行
- [ ] AC-003-03: 提供示例代码或配置
- [ ] AC-003-04: 评估建议的预期效果
- [ ] AC-003-05: 支持多个备选方案

**优先级**: Should have

---

### FR-004: 反思记录与审计

**描述**: 完整记录所有反思过程和结果

**验收标准**:
- [ ] AC-004-01: 记录每次反思的时间戳
- [ ] AC-004-02: 存储原始结果和评估分数
- [ ] AC-004-03: 保存识别的问题列表
- [ ] AC-004-04: 归档生成的改进建议
- [ ] AC-004-05: 支持历史查询和分析

**优先级**: Must have

---

### FR-005: Agent 工作流集成

**描述**: 将反思机制无缝集成到现有 Agent 工作流

**验收标准**:
- [ ] AC-005-01: 在任务执行后自动触发反思
- [ ] AC-005-02: 低质量结果标记为需要改进
- [ ] AC-005-03: 反思结果添加到实施笔记
- [ ] AC-005-04: 不阻塞正常执行流程
- [ ] AC-005-05: 用户可查看反思详情

**优先级**: Must have

---

## 📐 技术设计

### 架构概览

```
┌─────────────────────────────────────────────┐
│           Agent Execution Flow              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Task Execution Result               │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│        Reflection Engine                    │
│  ┌───────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Quality   │→│ Issue    │→│Suggestion │  │
│  │Evaluator  │ │Detector  │ │ Generator │  │
│  └───────────┘ └──────────┘ └───────────┘  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Reflection Recorder & Auditor          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     Updated Spec with Reflection Notes      │
└─────────────────────────────────────────────┘
```

### 核心组件

#### 1. ReflectionEngine

**文件**: `.lingma/scripts/reflection_engine.py`

**职责**:
- 协调质量评估、问题检测和建议生成
- 管理反思流程
- 提供统一的反思接口

**关键方法**:
```python
class ReflectionEngine:
    def reflect_on_task(self, task: Task, result: Any) -> ReflectionResult:
        """对任务执行结果进行反思"""
        
    def evaluate_quality(self, result: Any, criteria: QualityCriteria) -> QualityScore:
        """评估结果质量"""
        
    def identify_issues(self, result: Any) -> List[Issue]:
        """识别问题"""
        
    def generate_suggestions(self, issues: List[Issue]) -> List[Suggestion]:
        """生成改进建议"""
```

#### 2. QualityEvaluator

**文件**: `.lingma/scripts/quality_evaluator.py`

**职责**:
- 基于多维度标准评估质量
- 计算综合质量分数
- 生成质量报告

**评估维度**:
- **正确性** (Correctness): 结果是否符合预期
- **完整性** (Completeness): 是否覆盖所有需求
- **可读性** (Readability): 代码/文档是否清晰
- **性能** (Performance): 执行效率如何
- **安全性** (Security): 是否有安全隐患
- **可维护性** (Maintainability): 是否易于维护

#### 3. IssueDetector

**文件**: `.lingma/scripts/issue_detector.py`

**职责**:
- 扫描结果中的问题
- 分类问题类型和严重程度
- 提供问题详情和上下文

**问题类型**:
- `SYNTAX_ERROR`: 语法错误
- `LOGIC_ERROR`: 逻辑错误
- `BEST_PRACTICE_VIOLATION`: 最佳实践违反
- `PERFORMANCE_ISSUE`: 性能问题
- `SECURITY_RISK`: 安全风险
- `DOCUMENTATION_GAP`: 文档缺失

**严重程度**:
- `CRITICAL`: 必须修复
- `HIGH`: 应该修复
- `MEDIUM`: 建议修复
- `LOW`: 可选修复

#### 4. SuggestionGenerator

**文件**: `.lingma/scripts/suggestion_generator.py`

**职责**:
- 基于问题生成改进建议
- 提供具体的修复方案
- 评估建议的预期效果

**建议内容**:
- 问题描述
- 修复步骤
- 示例代码/配置
- 预期改进效果
- 实施难度评估

#### 5. ReflectionRecorder

**文件**: `.lingma/scripts/reflection_recorder.py`

**职责**:
- 持久化存储反思结果
- 支持历史查询
- 生成反思报告

**存储格式**:
```json
{
  "task_id": "task-001",
  "timestamp": "2026-04-17T22:00:00Z",
  "quality_score": {
    "overall": 0.85,
    "dimensions": {
      "correctness": 0.9,
      "completeness": 0.8,
      "readability": 0.85,
      "performance": 0.8,
      "security": 0.95,
      "maintainability": 0.85
    }
  },
  "issues": [
    {
      "type": "BEST_PRACTICE_VIOLATION",
      "severity": "MEDIUM",
      "description": "缺少类型注解",
      "location": "line 42"
    }
  ],
  "suggestions": [
    {
      "issue_id": "issue-001",
      "action": "添加类型注解",
      "example": "def func(x: int) -> str:",
      "expected_improvement": "提高代码可读性和类型安全性"
    }
  ]
}
```

---

## 🔧 实施任务

### Task 1.1: 创建 Reflection Engine 核心
**预计时间**: 2天

**工作内容**:
1. 创建 `reflection_engine.py` 基础框架
2. 实现 `reflect_on_task()` 主流程
3. 定义数据模型（ReflectionResult, QualityScore, Issue, Suggestion）
4. 编写单元测试

**验收标准**:
- [ ] 核心类和方法已实现
- [ ] 单元测试覆盖率 > 80%
- [ ] 能处理基本的反思流程

---

### Task 1.2: 实现 Quality Evaluator
**预计时间**: 2天

**工作内容**:
1. 创建 `quality_evaluator.py`
2. 实现各维度评估算法
3. 配置质量标准（`.lingma/config/quality-standards.json`）
4. 集成代码分析工具（pylint, mypy, black）

**验收标准**:
- [ ] 支持 6 个质量维度评估
- [ ] 能调用外部工具进行分析
- [ ] 生成详细的质量报告
- [ ] 测试通过

---

### Task 1.3: 实现 Issue Detector
**预计时间**: 1.5天

**工作内容**:
1. 创建 `issue_detector.py`
2. 实现问题扫描逻辑
3. 定义问题分类体系
4. 集成静态分析工具

**验收标准**:
- [ ] 能检测 6 种问题类型
- [ ] 正确分类严重程度
- [ ] 提供准确的问题位置
- [ ] 测试通过

---

### Task 1.4: 实现 Suggestion Generator
**预计时间**: 1.5天

**工作内容**:
1. 创建 `suggestion_generator.py`
2. 实现建议生成算法
3. 建立建议模板库
4. 评估建议效果

**验收标准**:
- [ ] 每个问题至少生成一个建议
- [ ] 建议具体可执行
- [ ] 包含示例代码
- [ ] 测试通过

---

### Task 1.5: 实现 Reflection Recorder
**预计时间**: 1天

**工作内容**:
1. 创建 `reflection_recorder.py`
2. 实现 JSON 存储
3. 添加查询接口
4. 生成反思报告

**验收标准**:
- [ ] 能持久化存储反思结果
- [ ] 支持按任务 ID 查询
- [ ] 能生成汇总报告
- [ ] 测试通过

---

### Task 1.6: 集成到 Agent 工作流
**预计时间**: 1天

**工作内容**:
1. 修改 `spec-driven-core-agent.md`
2. 在任务执行后调用反思引擎
3. 将反思结果添加到 Spec 实施笔记
4. 更新进度跟踪

**验收标准**:
- [ ] 反思自动触发
- [ ] 结果正确记录
- [ ] 不影响正常流程
- [ ] 端到端测试通过

---

### Task 1.7: 文档和培训
**预计时间**: 0.5天

**工作内容**:
1. 编写用户指南
2. 创建开发者文档
3. 添加使用示例
4. 更新 README

**验收标准**:
- [ ] 文档完整清晰
- [ ] 包含实际示例
- [ ] API 文档齐全

---

## 📊 测试计划

### 单元测试
- ReflectionEngine: 15+ 测试用例
- QualityEvaluator: 20+ 测试用例
- IssueDetector: 15+ 测试用例
- SuggestionGenerator: 10+ 测试用例
- ReflectionRecorder: 10+ 测试用例

**目标**: 总测试用例数 > 70，覆盖率 > 80%

### 集成测试
- 完整的反思流程测试
- 与 Agent 工作流集成测试
- 性能基准测试

### 端到端测试
- 真实任务执行 + 反思
- 验证反思结果准确性
- 检查 Spec 更新正确性

---

## ⚠️ 风险与缓解

### 风险 1: 性能开销过大
**影响**: 高  
**概率**: 中

**缓解措施**:
- 异步执行反思（不阻塞主流程）
- 缓存常见模式的评估结果
- 限制反思深度和迭代次数
- 性能监控和告警

### 风险 2: 误报率高
**影响**: 中  
**概率**: 中

**缓解措施**:
- 多轮验证和优化评估算法
- 允许用户反馈和调整
- 记录误报案例用于改进
- 设置置信度阈值

### 风险 3: 建议质量不高
**影响**: 中  
**概率**: 低

**缓解措施**:
- 建立高质量的建议模板库
- 结合最佳实践和模式
- 用户评分和反馈循环
- 持续优化建议生成算法

---

## 📈 成功指标

### 技术指标
- ✅ 单元测试覆盖率 > 80%
- ✅ 集成测试通过率 100%
- ✅ 反思执行时间 < 5秒
- ✅ 内存使用增长 < 10%

### 质量指标
- ✅ 问题检测准确率 > 75%
- ✅ 建议采纳率 > 60%
- ✅ 误报率 < 20%
- ✅ 用户满意度 > 4/5

### 业务指标
- ✅ 代码质量提升 20%+
- ✅ 重复错误减少 40%+
- ✅ 审查时间减少 30%+

---

## 🚀 交付物

### 代码文件
- [ ] `.lingma/scripts/reflection_engine.py` (~300 lines)
- [ ] `.lingma/scripts/quality_evaluator.py` (~250 lines)
- [ ] `.lingma/scripts/issue_detector.py` (~200 lines)
- [ ] `.lingma/scripts/suggestion_generator.py` (~200 lines)
- [ ] `.lingma/scripts/reflection_recorder.py` (~150 lines)

### 配置文件
- [ ] `.lingma/config/quality-standards.json`

### 文档
- [ ] `.lingma/docs/guides/reflection-engine-user-guide.md`
- [ ] `.lingma/docs/architecture/reflection-engine-design.md`
- [ ] 更新 `spec-driven-core-agent.md`

### 测试
- [ ] `.lingma/tests/test_reflection_engine.py`
- [ ] `.lingma/tests/test_quality_evaluator.py`
- [ ] `.lingma/tests/test_issue_detector.py`
- [ ] `.lingma/tests/test_suggestion_generator.py`
- [ ] `.lingma/tests/test_reflection_recorder.py`

### 报告
- [ ] `.lingma/reports/phase1-completion-report.md`

---

## 📅 时间表

| 日期 | 任务 | 状态 |
|------|------|------|
| 2026-04-17 | 创建 Spec | ✅ 完成 |
| 2026-04-18 | Task 1.1: Reflection Engine 核心 | ⏳ 待开始 |
| 2026-04-19 | Task 1.2: Quality Evaluator | ⏳ 待开始 |
| 2026-04-20 | Task 1.3: Issue Detector | ⏳ 待开始 |
| 2026-04-21 | Task 1.4: Suggestion Generator | ⏳ 待开始 |
| 2026-04-22 | Task 1.5: Reflection Recorder | ⏳ 待开始 |
| 2026-04-23 | Task 1.6: Agent 集成 | ⏳ 待开始 |
| 2026-04-24 | Task 1.7: 文档 + 测试 | ⏳ 待开始 |

---

## 🎯 下一步行动

### 立即行动
1. ✅ 完成差距分析
2. ✅ 创建 Phase 1 Spec
3. ⏳ 开始 Task 1.1: Reflection Engine 核心

### 本周目标
- 完成所有 7 个任务
- 实现完整的自我反思机制
- 通过所有测试
- 更新文档

---

**Spec 版本**: 1.0  
**创建日期**: 2026-04-17  
**负责人**: AI Assistant  
**审核状态**: 待确认  
**预计完成**: 2026-04-24
