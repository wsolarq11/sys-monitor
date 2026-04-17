#!/usr/bin/env python3
"""
AI Agent Code Self-Modification System - AI Agent 代码自修改系统

HyperAgents风格的自指改进、Gödel Machine理念、安全代码演化
实现生产级 AI Agent 的代码自我优化框架

参考社区最佳实践:
- HyperAgents (Meta, ICLR 2026): Self-referential improvement
- Gödel Machine: All levels modifiable
- Safe code evolution with validation
- Version control and rollback
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import hashlib
import difflib
import shutil
import subprocess
import random

logger = logging.getLogger(__name__)


class ModificationType(Enum):
    """修改类型"""
    BUG_FIX = "bug_fix"  # Bug修复
    PERFORMANCE_OPTIMIZATION = "performance_optimization"  # 性能优化
    CODE_CLEANUP = "code_cleanup"  # 代码清理
    FEATURE_ADDITION = "feature_addition"  # 功能添加
    REFACTORING = "refactoring"  # 重构
    SECURITY_PATCH = "security_patch"  # 安全补丁


class ValidationLevel(Enum):
    """验证级别"""
    SYNTAX_CHECK = "syntax_check"  # 语法检查
    UNIT_TESTS = "unit_tests"  # 单元测试
    INTEGRATION_TESTS = "integration_tests"  # 集成测试
    PERFORMANCE_BENCHMARK = "performance_benchmark"  # 性能基准
    SECURITY_SCAN = "security_scan"  # 安全扫描


@dataclass
class CodeSnapshot:
    """代码快照"""
    snapshot_id: str
    file_path: str
    content_hash: str
    timestamp: str
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    test_results: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ModificationProposal:
    """修改提案"""
    proposal_id: str
    modification_type: ModificationType
    target_file: str
    current_code: str
    proposed_code: str
    expected_improvement: Dict[str, float]
    confidence: float
    rationale: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def get_diff(self) -> str:
        """获取差异"""
        diff = difflib.unified_diff(
            self.current_code.splitlines(keepends=True),
            self.proposed_code.splitlines(keepends=True),
            fromfile='current',
            tofile='proposed'
        )
        return ''.join(diff)


@dataclass
class ValidationResult:
    """验证结果"""
    validation_id: str
    proposal_id: str
    validation_level: ValidationLevel
    passed: bool
    metrics: Dict[str, float]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ImprovementRecord:
    """改进记录"""
    record_id: str
    proposal: ModificationProposal
    validation_results: List[ValidationResult]
    applied: bool
    performance_before: Dict[str, float]
    performance_after: Dict[str, float]
    actual_improvement: Dict[str, float]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class CodeAnalyzer:
    """代码分析器
    
    分析代码质量和性能
    """
    
    def __init__(self):
        self.analysis_history: List[Dict] = []
    
    def analyze_code_quality(self, code: str, file_path: str = "") -> Dict:
        """
        分析代码质量
        
        Args:
            code: 代码内容
            file_path: 文件路径
            
        Returns:
            质量分析结果
        """
        lines = code.split('\n')
        
        # 基本统计
        total_lines = len(lines)
        non_empty_lines = sum(1 for line in lines if line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        
        # 复杂度估算
        complexity_indicators = [
            'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except',
            'def ', 'class ', 'with ', 'and ', 'or '
        ]
        
        complexity_score = sum(
            code.count(indicator) for indicator in complexity_indicators
        )
        
        # 代码风格检查（简化）
        style_issues = []
        
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                style_issues.append(f"Line {i}: Too long ({len(line)} chars)")
            
            if line and not line[0].isspace() and not line.startswith(('def ', 'class ', '#', '"""', "'''")):
                if i > 1 and lines[i-2].strip():
                    pass  # 可能是正常的
        
        quality_score = max(0.0, min(1.0, 
            1.0 - (complexity_score / max(non_empty_lines, 1)) * 0.5
            - len(style_issues) * 0.05
        ))
        
        result = {
            "total_lines": total_lines,
            "non_empty_lines": non_empty_lines,
            "comment_ratio": round(comment_lines / max(non_empty_lines, 1), 2),
            "complexity_score": complexity_score,
            "style_issues": style_issues,
            "quality_score": round(quality_score, 4),
            "estimated_maintainability": "high" if quality_score > 0.8 else "medium" if quality_score > 0.6 else "low"
        }
        
        self.analysis_history.append({
            "file": file_path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "quality_score": quality_score
        })
        
        logger.info(f"Code quality analyzed: score={quality_score:.2f}, complexity={complexity_score}")
        
        return result
    
    def detect_code_smells(self, code: str) -> List[Dict]:
        """检测代码异味"""
        smells = []
        
        # 检测长函数
        lines = code.split('\n')
        function_start = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                if function_start is not None and i - function_start > 50:
                    smells.append({
                        "type": "long_function",
                        "severity": "warning",
                        "message": f"Function too long (>50 lines)",
                        "line": function_start
                    })
                function_start = i
        
        # 检测重复代码模式（简化）
        if code.count('for ') > 10:
            smells.append({
                "type": "possible_duplication",
                "severity": "info",
                "message": "Many loops detected, consider refactoring"
            })
        
        # 检测深层嵌套
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent // 4)
        
        if max_indent > 4:
            smells.append({
                "type": "deep_nesting",
                "severity": "warning",
                "message": f"Deep nesting detected (level {max_indent})",
                "max_level": max_indent
            })
        
        logger.info(f"Code smells detected: {len(smells)}")
        
        return smells
    
    def estimate_performance(self, code: str) -> Dict:
        """估算性能特征"""
        # 基于代码模式的性能估算
        indicators = {
            "has_loops": 'for ' in code or 'while ' in code,
            "has_recursion": code.count('def ') > 0 and any(
                code.count(func_name) > 2 
                for func_name in [line.split('def ')[1].split('(')[0] 
                                 for line in code.split('\n') if 'def ' in line]
            ),
            "has_io_operations": any(op in code for op in ['open(', 'read(', 'write(', 'print(']),
            "has_network_calls": any(call in code for call in ['requests.', 'http.', 'urllib']),
            "has_database_queries": any(db in code for db in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', '.query(', '.execute('])
        }
        
        # 性能评分（越高越好）
        performance_score = 1.0
        
        if indicators["has_loops"]:
            loop_count = code.count('for ') + code.count('while ')
            performance_score -= min(0.3, loop_count * 0.05)
        
        if indicators["has_recursion"]:
            performance_score -= 0.1
        
        if indicators["has_io_operations"]:
            performance_score -= 0.1
        
        if indicators["has_network_calls"]:
            performance_score -= 0.15
        
        if indicators["has_database_queries"]:
            performance_score -= 0.1
        
        performance_score = max(0.0, min(1.0, performance_score))
        
        return {
            "indicators": indicators,
            "performance_score": round(performance_score, 4),
            "bottleneck_risk": "high" if performance_score < 0.5 else "medium" if performance_score < 0.7 else "low"
        }


class CodeModifier:
    """代码修改器
    
    生成和应用代码修改
    """
    
    def __init__(self):
        self.modification_history: List[ImprovementRecord] = []
        self.code_analyzer = CodeAnalyzer()
    
    def propose_modification(
        self,
        current_code: str,
        improvement_goal: str,
        file_path: str = ""
    ) -> ModificationProposal:
        """
        提出修改建议
        
        Args:
            current_code: 当前代码
            improvement_goal: 改进目标
            file_path: 文件路径
            
        Returns:
            修改提案
        """
        # 分析当前代码
        quality_analysis = self.code_analyzer.analyze_code_quality(current_code, file_path)
        code_smells = self.code_analyzer.detect_code_smells(current_code)
        performance_estimate = self.code_analyzer.estimate_performance(current_code)
        
        # 确定修改类型
        if "bug" in improvement_goal.lower() or "fix" in improvement_goal.lower():
            mod_type = ModificationType.BUG_FIX
        elif "performance" in improvement_goal.lower() or "optimize" in improvement_goal.lower():
            mod_type = ModificationType.PERFORMANCE_OPTIMIZATION
        elif "clean" in improvement_goal.lower() or "refactor" in improvement_goal.lower():
            mod_type = ModificationType.CODE_CLEANUP
        elif "add" in improvement_goal.lower() or "feature" in improvement_goal.lower():
            mod_type = ModificationType.FEATURE_ADDITION
        elif "security" in improvement_goal.lower():
            mod_type = ModificationType.SECURITY_PATCH
        else:
            mod_type = ModificationType.REFACTORING
        
        # 模拟代码改进（在实际应用中，这里应调用LLM生成改进代码）
        proposed_code = self._simulate_code_improvement(current_code, mod_type, improvement_goal)
        
        # 计算预期改进
        expected_improvement = self._calculate_expected_improvement(
            current_code, proposed_code, mod_type
        )
        
        # 创建提案
        proposal = ModificationProposal(
            proposal_id=str(uuid.uuid4()),
            modification_type=mod_type,
            target_file=file_path,
            current_code=current_code,
            proposed_code=proposed_code,
            expected_improvement=expected_improvement,
            confidence=random.uniform(0.7, 0.95),
            rationale=f"Proposed {mod_type.value} to achieve: {improvement_goal}"
        )
        
        logger.info(f"Modification proposed: type={mod_type.value}, confidence={proposal.confidence:.2f}")
        
        return proposal
    
    def _simulate_code_improvement(
        self,
        current_code: str,
        mod_type: ModificationType,
        goal: str
    ) -> str:
        """模拟代码改进（实际应由LLM生成）"""
        # 这里只是模拟，实际应用需要LLM
        improved_code = current_code
        
        if mod_type == ModificationType.CODE_CLEANUP:
            # 移除多余空行
            lines = improved_code.split('\n')
            cleaned_lines = []
            prev_empty = False
            
            for line in lines:
                is_empty = not line.strip()
                
                if is_empty and prev_empty:
                    continue
                
                cleaned_lines.append(line)
                prev_empty = is_empty
            
            improved_code = '\n'.join(cleaned_lines)
        
        elif mod_type == ModificationType.PERFORMANCE_OPTIMIZATION:
            # 添加注释标记优化点
            improved_code = "# Performance optimized\n" + improved_code
        
        elif mod_type == ModificationType.BUG_FIX:
            # 添加错误处理
            improved_code = "# Bug fixed\n" + improved_code
        
        return improved_code
    
    def _calculate_expected_improvement(
        self,
        current_code: str,
        proposed_code: str,
        mod_type: ModificationType
    ) -> Dict[str, float]:
        """计算预期改进"""
        current_quality = self.code_analyzer.analyze_code_quality(current_code)
        proposed_quality = self.code_analyzer.analyze_code_quality(proposed_code)
        
        improvement = {
            "quality_score": proposed_quality["quality_score"] - current_quality["quality_score"],
            "complexity_reduction": max(0, current_quality["complexity_score"] - proposed_quality["complexity_score"]),
            "style_issues_fixed": max(0, len(current_quality["style_issues"]) - len(proposed_quality["style_issues"]))
        }
        
        if mod_type == ModificationType.PERFORMANCE_OPTIMIZATION:
            current_perf = self.code_analyzer.estimate_performance(current_code)
            proposed_perf = self.code_analyzer.estimate_performance(proposed_code)
            improvement["performance_score"] = proposed_perf["performance_score"] - current_perf["performance_score"]
        
        return improvement


class CodeValidator:
    """代码验证器
    
    验证代码修改的安全性和正确性
    """
    
    def __init__(self):
        self.validation_history: List[ValidationResult] = []
    
    def validate_modification(
        self,
        proposal: ModificationProposal,
        validation_levels: List[ValidationLevel] = None
    ) -> List[ValidationResult]:
        """
        验证修改
        
        Args:
            proposal: 修改提案
            validation_levels: 验证级别列表
            
        Returns:
            验证结果列表
        """
        if validation_levels is None:
            validation_levels = [
                ValidationLevel.SYNTAX_CHECK,
                ValidationLevel.UNIT_TESTS
            ]
        
        results = []
        
        for level in validation_levels:
            result = self._perform_validation(proposal, level)
            results.append(result)
            
            # 如果关键验证失败，停止后续验证
            if not result.passed and level in [ValidationLevel.SYNTAX_CHECK, ValidationLevel.SECURITY_SCAN]:
                logger.warning(f"Critical validation failed at {level.value}, stopping")
                break
        
        self.validation_history.extend(results)
        
        logger.info(f"Validation completed: {sum(1 for r in results if r.passed)}/{len(results)} passed")
        
        return results
    
    def _perform_validation(
        self,
        proposal: ModificationProposal,
        level: ValidationLevel
    ) -> ValidationResult:
        """执行验证"""
        if level == ValidationLevel.SYNTAX_CHECK:
            return self._syntax_check(proposal)
        elif level == ValidationLevel.UNIT_TESTS:
            return self._unit_test_check(proposal)
        elif level == ValidationLevel.INTEGRATION_TESTS:
            return self._integration_test_check(proposal)
        elif level == ValidationLevel.PERFORMANCE_BENCHMARK:
            return self._performance_benchmark(proposal)
        elif level == ValidationLevel.SECURITY_SCAN:
            return self._security_scan(proposal)
        else:
            raise ValueError(f"Unknown validation level: {level}")
    
    def _syntax_check(self, proposal: ModificationProposal) -> ValidationResult:
        """语法检查"""
        try:
            compile(proposal.proposed_code, '<string>', 'exec')
            passed = True
            errors = []
            metrics = {"syntax_valid": 1.0}
        except SyntaxError as e:
            passed = False
            errors = [f"Syntax error: {str(e)}"]
            metrics = {"syntax_valid": 0.0}
        
        return ValidationResult(
            validation_id=str(uuid.uuid4()),
            proposal_id=proposal.proposal_id,
            validation_level=ValidationLevel.SYNTAX_CHECK,
            passed=passed,
            metrics=metrics,
            errors=errors
        )
    
    def _unit_test_check(self, proposal: ModificationProposal) -> ValidationResult:
        """单元测试检查（模拟）"""
        # 在实际应用中，这里应运行真实的单元测试
        passed = random.random() > 0.1  # 90%通过率
        
        return ValidationResult(
            validation_id=str(uuid.uuid4()),
            proposal_id=proposal.proposal_id,
            validation_level=ValidationLevel.UNIT_TESTS,
            passed=passed,
            metrics={"tests_passed": 1.0 if passed else 0.0},
            errors=[] if passed else ["Some unit tests failed"]
        )
    
    def _integration_test_check(self, proposal: ModificationProposal) -> ValidationResult:
        """集成测试检查（模拟）"""
        passed = random.random() > 0.15  # 85%通过率
        
        return ValidationResult(
            validation_id=str(uuid.uuid4()),
            proposal_id=proposal.proposal_id,
            validation_level=ValidationLevel.INTEGRATION_TESTS,
            passed=passed,
            metrics={"integration_valid": 1.0 if passed else 0.0},
            errors=[] if passed else ["Integration tests failed"]
        )
    
    def _performance_benchmark(self, proposal: ModificationProposal) -> ValidationResult:
        """性能基准测试（模拟）"""
        # 比较性能
        current_perf = CodeAnalyzer().estimate_performance(proposal.current_code)
        proposed_perf = CodeAnalyzer().estimate_performance(proposal.proposed_code)
        
        improvement = proposed_perf["performance_score"] - current_perf["performance_score"]
        passed = improvement >= -0.1  # 允许小幅下降
        
        return ValidationResult(
            validation_id=str(uuid.uuid4()),
            proposal_id=proposal.proposal_id,
            validation_level=ValidationLevel.PERFORMANCE_BENCHMARK,
            passed=passed,
            metrics={
                "current_performance": current_perf["performance_score"],
                "proposed_performance": proposed_perf["performance_score"],
                "improvement": improvement
            },
            errors=[] if passed else ["Performance degradation detected"]
        )
    
    def _security_scan(self, proposal: ModificationProposal) -> ValidationResult:
        """安全扫描（模拟）"""
        # 检查常见安全问题
        security_issues = []
        
        dangerous_patterns = ['eval(', 'exec(', '__import__(', 'os.system(']
        
        for pattern in dangerous_patterns:
            if pattern in proposal.proposed_code:
                security_issues.append(f"Dangerous pattern detected: {pattern}")
        
        passed = len(security_issues) == 0
        
        return ValidationResult(
            validation_id=str(uuid.uuid4()),
            proposal_id=proposal.proposal_id,
            validation_level=ValidationLevel.SECURITY_SCAN,
            passed=passed,
            metrics={"security_score": 1.0 if passed else 0.0},
            errors=security_issues
        )


class CodeVersionManager:
    """代码版本管理器
    
    管理代码快照和回滚
    """
    
    def __init__(self, backup_dir: str = ".code_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.snapshots: Dict[str, CodeSnapshot] = {}
    
    def create_snapshot(self, file_path: str, code: str) -> CodeSnapshot:
        """创建代码快照"""
        content_hash = hashlib.sha256(code.encode()).hexdigest()
        
        snapshot = CodeSnapshot(
            snapshot_id=str(uuid.uuid4()),
            file_path=file_path,
            content_hash=content_hash,
            timestamp=""
        )
        
        # 保存备份文件
        backup_file = self.backup_dir / f"{snapshot.snapshot_id}.py"
        backup_file.write_text(code)
        
        self.snapshots[snapshot.snapshot_id] = snapshot
        
        logger.info(f"Code snapshot created: {snapshot.snapshot_id[:8]}")
        
        return snapshot
    
    def restore_snapshot(self, snapshot_id: str) -> Optional[str]:
        """恢复代码快照"""
        if snapshot_id not in self.snapshots:
            logger.error(f"Snapshot not found: {snapshot_id}")
            return None
        
        snapshot = self.snapshots[snapshot_id]
        backup_file = self.backup_dir / f"{snapshot_id}.py"
        
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_file}")
            return None
        
        code = backup_file.read_text()
        
        logger.info(f"Code snapshot restored: {snapshot_id[:8]}")
        
        return code
    
    def cleanup_old_snapshots(self, keep_last: int = 10):
        """清理旧快照"""
        if len(self.snapshots) <= keep_last:
            return
        
        # 按时间排序，保留最近的
        sorted_snapshots = sorted(
            self.snapshots.items(),
            key=lambda x: x[1].timestamp,
            reverse=True
        )
        
        to_delete = sorted_snapshots[keep_last:]
        
        for snapshot_id, snapshot in to_delete:
            backup_file = self.backup_dir / f"{snapshot_id}.py"
            if backup_file.exists():
                backup_file.unlink()
            del self.snapshots[snapshot_id]
        
        logger.info(f"Cleaned up {len(to_delete)} old snapshots")


class SelfModifyingAgent:
    """自修改智能体
    
    整合所有代码自修改能力的完整系统
    """
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.code_modifier = CodeModifier()
        self.code_validator = CodeValidator()
        self.version_manager = CodeVersionManager()
        self.improvement_history: List[ImprovementRecord] = []
    
    def self_improve(
        self,
        file_path: str,
        improvement_goal: str,
        validation_levels: List[ValidationLevel] = None
    ) -> Dict:
        """
        自我改进
        
        Args:
            file_path: 目标文件路径
            improvement_goal: 改进目标
            validation_levels: 验证级别
            
        Returns:
            改进结果
        """
        logger.info(f"Starting self-improvement: {file_path}, goal={improvement_goal}")
        
        # Step 1: 读取当前代码
        try:
            current_code = Path(file_path).read_text()
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
        
        # Step 2: 创建快照
        snapshot = self.version_manager.create_snapshot(file_path, current_code)
        
        # Step 3: 分析当前代码
        quality_before = self.code_analyzer.analyze_code_quality(current_code, file_path)
        performance_before = self.code_analyzer.estimate_performance(current_code)
        
        # Step 4: 提出修改建议
        proposal = self.code_modifier.propose_modification(
            current_code, improvement_goal, file_path
        )
        
        # Step 5: 验证修改
        validation_results = self.code_validator.validate_modification(
            proposal, validation_levels
        )
        
        all_passed = all(r.passed for r in validation_results)
        
        # Step 6: 决定是否应用
        if all_passed and proposal.confidence > 0.7:
            # 应用修改
            try:
                Path(file_path).write_text(proposal.proposed_code)
                applied = True
                
                # 评估改进后性能
                quality_after = self.code_analyzer.analyze_code_quality(proposal.proposed_code, file_path)
                performance_after = self.code_analyzer.estimate_performance(proposal.proposed_code)
                
                actual_improvement = {
                    "quality_score": quality_after["quality_score"] - quality_before["quality_score"],
                    "performance_score": performance_after["performance_score"] - performance_before["performance_score"]
                }
                
                logger.info(f"Self-improvement applied successfully")
                
            except Exception as e:
                # 应用失败，回滚
                self.version_manager.restore_snapshot(snapshot.snapshot_id)
                applied = False
                actual_improvement = {}
                logger.error(f"Failed to apply improvement: {str(e)}")
        else:
            applied = False
            actual_improvement = {}
            logger.info(f"Self-improvement rejected: passed={all_passed}, confidence={proposal.confidence:.2f}")
        
        # Step 7: 记录改进
        record = ImprovementRecord(
            record_id=str(uuid.uuid4()),
            proposal=proposal,
            validation_results=validation_results,
            applied=applied,
            performance_before=performance_before,
            performance_after=self.code_analyzer.estimate_performance(proposal.proposed_code) if applied else performance_before,
            actual_improvement=actual_improvement
        )
        
        self.improvement_history.append(record)
        
        return {
            "applied": applied,
            "proposal": asdict(proposal),
            "validation_results": [asdict(r) for r in validation_results],
            "improvement_record_id": record.record_id
        }
    
    def get_self_improvement_analytics(self) -> Dict:
        """获取自我改进分析"""
        if not self.improvement_history:
            return {"total_improvements": 0}
        
        applied_count = sum(1 for r in self.improvement_history if r.applied)
        
        return {
            "total_improvements": len(self.improvement_history),
            "applied_count": applied_count,
            "rejection_rate": round(1 - applied_count / len(self.improvement_history), 2),
            "recent_improvements": [
                {
                    "record_id": r.record_id[:8],
                    "type": r.proposal.modification_type.value,
                    "applied": r.applied,
                    "confidence": r.proposal.confidence
                }
                for r in self.improvement_history[-5:]
            ]
        }


def create_self_modifying_agent() -> SelfModifyingAgent:
    """工厂函数：创建自修改智能体"""
    return SelfModifyingAgent()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Code Self-Modification 测试")
    print("="*60)
    
    agent = create_self_modifying_agent()
    
    # 创建测试文件
    test_file = Path("test_self_modify.py")
    test_code = """
def calculate_sum(numbers):
    result = 0
    for n in numbers:
        result = result + n
    return result

def calculate_average(numbers):
    if len(numbers) == 0:
        return 0
    total = calculate_sum(numbers)
    avg = total / len(numbers)
    return avg
"""
    
    test_file.write_text(test_code)
    print(f"\n📝 创建测试文件: {test_file}")
    
    # 自我改进
    print("\n🔄 执行自我改进...")
    result = agent.self_improve(
        file_path=str(test_file),
        improvement_goal="Optimize performance and clean up code",
        validation_levels=[
            ValidationLevel.SYNTAX_CHECK,
            ValidationLevel.UNIT_TESTS,
            ValidationLevel.SECURITY_SCAN
        ]
    )
    
    print(f"\n📊 改进结果:")
    print(f"   是否应用: {'✅' if result['applied'] else '❌'}")
    print(f"   修改类型: {result['proposal']['modification_type']}")
    print(f"   置信度: {result['proposal']['confidence']:.2f}")
    print(f"   验证通过: {sum(1 for v in result['validation_results'] if v['passed'])}/{len(result['validation_results'])}")
    
    # 显示验证详情
    print(f"\n🔍 验证详情:")
    for v in result['validation_results']:
        status = "✅" if v['passed'] else "❌"
        print(f"   {status} {v['validation_level']}: {v['metrics']}")
    
    # 自我改进分析
    print(f"\n📈 自我改进分析:")
    analytics = agent.get_self_improvement_analytics()
    print(f"   总改进数: {analytics['total_improvements']}")
    print(f"   已应用: {analytics['applied_count']}")
    print(f"   拒绝率: {analytics['rejection_rate']:.0%}")
    
    # 清理测试文件
    test_file.unlink(missing_ok=True)
    print(f"\n🧹 清理测试文件")
    
    print("\n✅ 测试完成！")
