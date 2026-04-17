#!/usr/bin/env python3
"""
Feedback Loop Manager - 反馈循环管理器

基于 Ralph Wiggum 模式的自动迭代修复系统
核心思想: while True: 执行 → 验证 → 修复 → 直到满足条件

参考社区最佳实践:
- Ralph Wiggum Loop (Claude Code)
- AutoCodeRover (iterative code search and patch)
- PATCHAGENT (integrated verifier)
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class IterationStatus(Enum):
    """迭代状态"""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MAX_ITERATIONS = "max_iterations_reached"
    ABORTED = "aborted"


@dataclass
class IterationResult:
    """单次迭代结果"""
    iteration_number: int
    status: str
    output: Any = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class FeedbackSignal:
    """反馈信号"""
    signal_type: str  # "test_failure", "lint_error", "quality_low", etc.
    severity: str  # "critical", "high", "medium", "low"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: Optional[str] = None


@dataclass
class LoopConfig:
    """循环配置"""
    max_iterations: int = 10
    min_iterations: int = 1
    timeout_seconds: int = 300
    completion_promise: str = "COMPLETE"
    abort_promise: str = "ABORT"
    auto_commit: bool = False
    verbose: bool = False
    
    # 退出条件
    exit_on_success: bool = True
    exit_on_max_iterations: bool = True
    exit_on_timeout: bool = True
    
    # 重试策略
    retry_on_error: bool = True
    max_consecutive_failures: int = 3
    
    # 质量阈值
    min_quality_score: float = 0.7


class FeedbackCollector:
    """反馈收集器
    
    从多种来源收集反馈信号:
    - 测试运行结果
    - Linter/静态分析工具
    - 质量评估 (Reflection Engine)
    - 用户反馈
    """
    
    def __init__(self):
        self.signals: List[FeedbackSignal] = []
    
    def collect_from_tests(self, test_results: Dict) -> List[FeedbackSignal]:
        """从测试结果收集反馈"""
        signals = []
        
        if not test_results.get("passed", True):
            failures = test_results.get("failures", [])
            for failure in failures:
                signals.append(FeedbackSignal(
                    signal_type="test_failure",
                    severity="critical",
                    message=f"测试失败: {failure.get('test_name', 'unknown')}",
                    details=failure,
                    suggested_fix=failure.get("error_message")
                ))
        
        return signals
    
    def collect_from_linter(self, lint_results: Dict) -> List[FeedbackSignal]:
        """从 linter 结果收集反馈"""
        signals = []
        
        errors = lint_results.get("errors", [])
        for error in errors:
            severity_map = {
                "error": "high",
                "warning": "medium",
                "info": "low"
            }
            
            signals.append(FeedbackSignal(
                signal_type="lint_error",
                severity=severity_map.get(error.get("level", "error"), "medium"),
                message=error.get("message", "Linting error"),
                details=error,
                suggested_fix=error.get("suggestion")
            ))
        
        return signals
    
    def collect_from_reflection(self, reflection_result: Dict) -> List[FeedbackSignal]:
        """从反思结果收集反馈"""
        signals = []
        
        issues = reflection_result.get("issues", [])
        for issue in issues:
            signals.append(FeedbackSignal(
                signal_type="quality_issue",
                severity=issue.get("severity", "medium"),
                message=issue.get("description", "Quality issue detected"),
                details=issue,
                suggested_fix=issue.get("suggested_fix")
            ))
        
        return signals
    
    def collect_from_user(self, feedback_text: str, severity: str = "medium") -> FeedbackSignal:
        """收集用户反馈"""
        return FeedbackSignal(
            signal_type="user_feedback",
            severity=severity,
            message=feedback_text
        )
    
    def get_critical_signals(self) -> List[FeedbackSignal]:
        """获取关键反馈信号"""
        return [s for s in self.signals if s.severity in ["critical", "high"]]
    
    def clear(self):
        """清空所有信号"""
        self.signals.clear()


class AutoFixLibrary:
    """自动修复库
    
    根据反馈信号类型应用预定义的修复策略
    """
    
    def __init__(self):
        self.fix_strategies = self._load_strategies()
    
    def _load_strategies(self) -> Dict:
        """加载修复策略"""
        return {
            "test_failure": {
                "action": "analyze_and_fix_test",
                "description": "分析测试失败原因并修复代码",
                "steps": [
                    "读取错误堆栈",
                    "定位失败代码行",
                    "分析失败原因",
                    "生成修复方案",
                    "应用修复"
                ]
            },
            "lint_error": {
                "action": "apply_linter_fix",
                "description": "应用 linter 建议的修复",
                "tools": ["black", "pylint --fix", "autopep8"]
            },
            "syntax_error": {
                "action": "fix_syntax",
                "description": "修复语法错误",
                "method": "parse_error_and_correct"
            },
            "security_risk": {
                "action": "replace_unsafe_pattern",
                "description": "替换不安全的代码模式",
                "patterns": {
                    "eval(": "ast.literal_eval()",
                    "exec(": "subprocess.run()",
                    "os.system(": "subprocess.run()"
                }
            },
            "performance_issue": {
                "action": "optimize_performance",
                "description": "优化性能问题",
                "optimizations": {
                    "string_concat_in_loop": "use_list_join",
                    "nested_loop_lookup": "use_dict_or_set",
                    "repeated_computation": "add_caching"
                }
            }
        }
    
    def apply_fix(self, signal: FeedbackSignal, context: Dict) -> Dict:
        """
        应用修复策略
        
        Args:
            signal: 反馈信号
            context: 上下文信息（代码、文件路径等）
            
        Returns:
            修复结果
        """
        strategy = self.fix_strategies.get(signal.signal_type)
        
        if not strategy:
            return {
                "success": False,
                "message": f"No fix strategy for signal type: {signal.signal_type}"
            }
        
        try:
            # 根据信号类型执行相应的修复
            if signal.signal_type == "test_failure":
                return self._fix_test_failure(signal, context)
            elif signal.signal_type == "lint_error":
                return self._fix_lint_error(signal, context)
            elif signal.signal_type == "syntax_error":
                return self._fix_syntax_error(signal, context)
            elif signal.signal_type == "security_risk":
                return self._fix_security_risk(signal, context)
            elif signal.signal_type == "performance_issue":
                return self._fix_performance_issue(signal, context)
            else:
                return {
                    "success": False,
                    "message": f"Unhandled signal type: {signal.signal_type}"
                }
        
        except Exception as e:
            logger.error(f"Fix application failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "error": str(e)
            }
    
    def _fix_test_failure(self, signal: FeedbackSignal, context: Dict) -> Dict:
        """修复测试失败"""
        # TODO: 集成实际的测试框架和修复逻辑
        return {
            "success": True,
            "action": "analyze_test_failure",
            "details": signal.details,
            "suggested_fix": signal.suggested_fix
        }
    
    def _fix_lint_error(self, signal: FeedbackSignal, context: Dict) -> Dict:
        """修复 lint 错误"""
        # TODO: 集成 black/pylint/autopep8
        return {
            "success": True,
            "action": "apply_linter_suggestion",
            "tool": "black",
            "details": signal.details
        }
    
    def _fix_syntax_error(self, signal: FeedbackSignal, context: Dict) -> Dict:
        """修复语法错误"""
        return {
            "success": True,
            "action": "correct_syntax",
            "details": signal.details
        }
    
    def _fix_security_risk(self, signal: FeedbackSignal, context: Dict) -> Dict:
        """修复安全风险"""
        # 查找并替换不安全模式
        code = context.get("code", "")
        fixed_code = code
        
        unsafe_patterns = {
            "eval(": "ast.literal_eval(",
            "exec(": "# TODO: Replace exec with safer alternative\n# subprocess.run(...)",
        }
        
        for unsafe, safe in unsafe_patterns.items():
            if unsafe in fixed_code:
                fixed_code = fixed_code.replace(unsafe, safe, 1)
        
        return {
            "success": True,
            "action": "replace_unsafe_pattern",
            "original_code_snippet": signal.details.get("evidence"),
            "fixed_code": fixed_code
        }
    
    def _fix_performance_issue(self, signal: FeedbackSignal, context: Dict) -> Dict:
        """修复性能问题"""
        code = context.get("code", "")
        
        # 示例：优化字符串拼接
        if "for " in code and "+=" in code and "'" in code:
            optimized = code.replace(
                "result = ''\n    for item in items:\n        result += str(item)",
                "result = ''.join(str(item) for item in items)"
            )
            return {
                "success": True,
                "action": "optimize_string_concatenation",
                "original": code,
                "optimized": optimized,
                "improvement": "O(n²) → O(n)"
            }
        
        return {
            "success": False,
            "message": "No applicable optimization found"
        }


class IterationManager:
    """迭代管理器
    
    实现 Ralph Wiggum 循环模式:
    while True:
        执行任务
        收集反馈
        应用修复
        检查退出条件
    """
    
    def __init__(self, config: Optional[LoopConfig] = None):
        self.config = config or LoopConfig()
        self.feedback_collector = FeedbackCollector()
        self.auto_fix_library = AutoFixLibrary()
        self.iteration_history: List[IterationResult] = []
        self.current_iteration = 0
    
    def run_loop(
        self,
        task_function: Callable,
        validation_function: Callable,
        context: Dict = None
    ) -> Dict:
        """
        运行反馈循环
        
        Args:
            task_function: 任务执行函数
            validation_function: 验证函数，返回 (passed: bool, feedback: Dict)
            context: 上下文信息
            
        Returns:
            循环执行结果
        """
        start_time = time.time()
        consecutive_failures = 0
        
        logger.info(f"Starting feedback loop (max_iterations={self.config.max_iterations})")
        
        while True:
            self.current_iteration += 1
            
            # 检查最大迭代次数
            if self.current_iteration > self.config.max_iterations:
                return self._create_final_result(
                    status=IterationStatus.MAX_ITERATIONS,
                    start_time=start_time
                )
            
            # 检查超时
            elapsed = time.time() - start_time
            if elapsed > self.config.timeout_seconds:
                return self._create_final_result(
                    status=IterationStatus.TIMEOUT,
                    start_time=start_time
                )
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {self.current_iteration}/{self.config.max_iterations}")
            logger.info(f"{'='*60}")
            
            try:
                # Step 1: 执行任务
                iteration_start = time.time()
                task_output = task_function(context or {})
                iteration_time = time.time() - iteration_start
                
                # Step 2: 验证结果
                passed, validation_feedback = validation_function(task_output, context or {})
                
                # 确保 validation_feedback 是字典
                if not isinstance(validation_feedback, dict):
                    validation_feedback = {"message": str(validation_feedback)}
                
                # Step 3: 收集反馈
                self._collect_feedback(validation_feedback)
                
                # Step 4: 检查结果
                if passed:
                    # 检查是否达到最小迭代次数
                    if self.current_iteration >= self.config.min_iterations:
                        logger.info(f"✅ Validation passed!")
                        return self._create_final_result(
                            status=IterationStatus.SUCCESS,
                            output=task_output,
                            start_time=start_time
                        )
                    else:
                        logger.info(f"⚠️ Passed but minimum iterations not reached ({self.current_iteration}/{self.config.min_iterations})")
                
                # Step 5: 处理失败
                consecutive_failures += 1
                logger.warning(f"❌ Validation failed (consecutive failures: {consecutive_failures})")
                
                # 检查连续失败次数
                if consecutive_failures >= self.config.max_consecutive_failures:
                    logger.error(f"Max consecutive failures reached ({consecutive_failures})")
                    return self._create_final_result(
                        status=IterationStatus.FAILED,
                        output=task_output,
                        start_time=start_time
                    )
                
                # Step 6: 应用自动修复
                critical_signals = self.feedback_collector.get_critical_signals()
                if critical_signals and self.config.retry_on_error:
                    logger.info(f"🔧 Applying auto-fix for {len(critical_signals)} critical issues...")
                    fix_results = []
                    for signal in critical_signals:
                        fix_result = self.auto_fix_library.apply_fix(
                            signal, 
                            {"output": task_output, **(context or {})}
                        )
                        fix_results.append(fix_result)
                    
                    # 更新上下文（如果修复成功）
                    successful_fixes = [r for r in fix_results if r.get("success")]
                    if successful_fixes:
                        logger.info(f"✅ Applied {len(successful_fixes)} fixes")
                        # TODO: 将修复应用到实际代码
                    
                    # 清空反馈，准备下一轮
                    self.feedback_collector.clear()
                
                # 记录迭代历史
                self.iteration_history.append(IterationResult(
                    iteration_number=self.current_iteration,
                    status="failed" if not passed else "success",
                    output=task_output,
                    execution_time=round(iteration_time, 3)
                ))
                
            except Exception as e:
                logger.error(f"Iteration {self.current_iteration} failed with exception: {e}")
                import traceback
                traceback.print_exc()
                consecutive_failures += 1
                
                if consecutive_failures >= self.config.max_consecutive_failures:
                    return self._create_final_result(
                        status=IterationStatus.FAILED,
                        error=str(e),
                        start_time=start_time
                    )
        
        # Should never reach here
        return self._create_final_result(
            status=IterationStatus.ABORTED,
            start_time=start_time
        )
    
    def _collect_feedback(self, validation_feedback: Dict):
        """收集验证反馈"""
        if not validation_feedback:
            return
        
        # 从测试结果收集
        if "test_results" in validation_feedback:
            signals = self.feedback_collector.collect_from_tests(
                validation_feedback["test_results"]
            )
            self.feedback_collector.signals.extend(signals)
        
        # 从 linter 结果收集
        if "lint_results" in validation_feedback:
            signals = self.feedback_collector.collect_from_linter(
                validation_feedback["lint_results"]
            )
            self.feedback_collector.signals.extend(signals)
        
        # 从反思结果收集
        if "reflection" in validation_feedback:
            signals = self.feedback_collector.collect_from_reflection(
                validation_feedback["reflection"]
            )
            self.feedback_collector.signals.extend(signals)
    
    def _create_final_result(
        self,
        status: IterationStatus,
        output: Any = None,
        error: str = None,
        start_time: float = None
    ) -> Dict:
        """创建最终结果"""
        total_time = time.time() - start_time if start_time else 0
        
        result = {
            "status": status.value,
            "total_iterations": self.current_iteration,
            "total_time_seconds": round(total_time, 3),
            "iteration_history": [asdict(h) for h in self.iteration_history],
            "final_output": output,
            "error": error
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Loop completed: {status.value}")
        logger.info(f"Total iterations: {self.current_iteration}")
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info(f"{'='*60}\n")
        
        return result
    
    def get_summary(self) -> Dict:
        """获取循环摘要"""
        if not self.iteration_history:
            return {"total_iterations": 0}
        
        return {
            "total_iterations": len(self.iteration_history),
            "successful_iterations": sum(
                1 for h in self.iteration_history if h.status == "success"
            ),
            "failed_iterations": sum(
                1 for h in self.iteration_history if h.status == "failed"
            ),
            "average_iteration_time": round(
                sum(h.execution_time for h in self.iteration_history) / len(self.iteration_history),
                3
            )
        }


def create_iteration_manager(config: Optional[Dict] = None) -> IterationManager:
    """工厂函数：创建迭代管理器"""
    if config:
        loop_config = LoopConfig(**config)
    else:
        loop_config = LoopConfig()
    
    return IterationManager(loop_config)


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Feedback Loop Manager 测试")
    print("="*60)
    
    manager = create_iteration_manager({
        "max_iterations": 5,
        "min_iterations": 1,
        "verbose": True
    })
    
    # 模拟任务函数
    iteration_count = 0
    def mock_task(context):
        global iteration_count
        iteration_count += 1
        return {"result": f"Iteration {iteration_count}", "code": "print('hello')"}
    
    # 模拟验证函数
    def mock_validation(output, context):
        if iteration_count >= 3:
            return True, {"message": "All tests passed"}
        else:
            return False, {
                "test_results": {
                    "passed": False,
                    "failures": [{
                        "test_name": "test_example",
                        "error_message": "AssertionError: Expected 3, got 2"
                    }]
                }
            }
    
    # 运行循环
    result = manager.run_loop(mock_task, mock_validation)
    
    print(f"\n最终结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n循环摘要:")
    summary = manager.get_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
