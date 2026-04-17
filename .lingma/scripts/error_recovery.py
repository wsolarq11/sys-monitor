#!/usr/bin/env python3
"""
Error Recovery System - 错误恢复系统

智能重试、断路器模式、根因分析、状态回滚
构建容错 AI Agent 系统

参考社区最佳实践:
- Smart retry with exponential backoff
- Circuit breaker pattern for fault tolerance
- Root cause analysis for agent failures
- State checkpoint and rollback
- Error classification and handling
"""

import json
import time
import random
import logging
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型"""
    TRANSIENT = "transient"  # 临时性错误（可重试）
    PERMANENT = "permanent"  # 永久性错误（不可重试）
    RATE_LIMIT = "rate_limit"  # 速率限制
    TIMEOUT = "timeout"  # 超时
    AUTHENTICATION = "authentication"  # 认证错误
    VALIDATION = "validation"  # 验证错误
    RESOURCE_NOT_FOUND = "resource_not_found"  # 资源未找到
    INTERNAL_ERROR = "internal_error"  # 内部错误


class CircuitState(Enum):
    """断路器状态"""
    CLOSED = "closed"  # 关闭（正常）
    OPEN = "open"  # 打开（熔断）
    HALF_OPEN = "half_open"  # 半开（试探）


@dataclass
class ErrorEvent:
    """错误事件"""
    error_id: str
    error_type: ErrorType
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    occurred_at: str = ""
    retry_count: int = 0
    root_cause_hint: Optional[str] = None
    
    def __post_init__(self):
        if not self.occurred_at:
            self.occurred_at = datetime.now(timezone.utc).isoformat()


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0  # 基础延迟（秒）
    max_delay: float = 60.0  # 最大延迟（秒）
    backoff_factor: float = 2.0  # 退避因子
    jitter: bool = True  # 是否添加抖动
    retryable_errors: List[ErrorType] = field(default_factory=lambda: [
        ErrorType.TRANSIENT,
        ErrorType.RATE_LIMIT,
        ErrorType.TIMEOUT
    ])


@dataclass
class CircuitBreakerConfig:
    """断路器配置"""
    failure_threshold: int = 5  # 失败阈值
    reset_timeout: int = 60  # 重置超时（秒）
    half_open_max_calls: int = 3  # 半开状态最大调用数


@dataclass
class Checkpoint:
    """检查点"""
    checkpoint_id: str
    state: Dict[str, Any]
    created_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class ErrorClassifier:
    """错误分类器
    
    自动识别错误类型并提供根因提示
    """
    
    def __init__(self):
        self.error_patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """加载错误模式"""
        return {
            "404": {
                "type": ErrorType.RESOURCE_NOT_FOUND,
                "hint": "Resource not found - check if the path/ID is correct"
            },
            "401": {
                "type": ErrorType.AUTHENTICATION,
                "hint": "Authentication failed - check credentials or API key"
            },
            "403": {
                "type": ErrorType.AUTHENTICATION,
                "hint": "Access forbidden - check permissions"
            },
            "429": {
                "type": ErrorType.RATE_LIMIT,
                "hint": "Rate limit exceeded - wait and retry with backoff"
            },
            "500": {
                "type": ErrorType.INTERNAL_ERROR,
                "hint": "Internal server error - may be transient, retry recommended"
            },
            "502": {
                "type": ErrorType.TRANSIENT,
                "hint": "Bad gateway - service temporarily unavailable"
            },
            "503": {
                "type": ErrorType.TRANSIENT,
                "hint": "Service unavailable - retry with exponential backoff"
            },
            "504": {
                "type": ErrorType.TIMEOUT,
                "hint": "Gateway timeout - increase timeout or retry"
            },
            "timeout": {
                "type": ErrorType.TIMEOUT,
                "hint": "Operation timed out - consider increasing timeout value"
            },
            "connection": {
                "type": ErrorType.TRANSIENT,
                "hint": "Connection error - network issue, retry recommended"
            }
        }
    
    def classify(self, error: Exception, context: Dict = None) -> ErrorEvent:
        """
        分类错误
        
        Args:
            error: 异常对象
            context: 上下文信息
            
        Returns:
            错误事件
        """
        import uuid
        
        error_str = str(error).lower()
        error_type = ErrorType.PERMANENT
        root_cause_hint = "Unknown error - manual investigation required"
        
        # 匹配错误模式
        for pattern, info in self.error_patterns.items():
            if pattern in error_str or pattern in str(type(error).__name__).lower():
                error_type = info["type"]
                root_cause_hint = info["hint"]
                break
        
        # 特殊处理
        if isinstance(error, TimeoutError):
            error_type = ErrorType.TIMEOUT
        elif isinstance(error, ConnectionError):
            error_type = ErrorType.TRANSIENT
        elif isinstance(error, ValueError):
            error_type = ErrorType.VALIDATION
        
        event = ErrorEvent(
            error_id=str(uuid.uuid4()),
            error_type=error_type,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            context=context or {},
            root_cause_hint=root_cause_hint
        )
        
        logger.warning(f"Error classified: {error_type.value} - {root_cause_hint}")
        
        return event


class SmartRetry:
    """智能重试机制
    
    带指数退避和抖动的重试策略
    """
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.error_classifier = ErrorClassifier()
        self.retry_history: List[Dict] = []
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        带重试执行函数
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            函数返回值
            
        Raises:
            Exception: 最后一次重试仍然失败时抛出
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                result = func(*args, **kwargs)
                
                # 记录成功
                self.retry_history.append({
                    "attempt": attempt + 1,
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                logger.info(f"Success on attempt {attempt + 1}")
                return result
            
            except Exception as e:
                last_exception = e
                
                # 分类错误
                error_event = self.error_classifier.classify(e)
                
                # 检查是否可重试
                if error_event.error_type not in self.config.retryable_errors:
                    logger.error(f"Non-retryable error: {error_event.error_type.value}")
                    raise
                
                # 如果是最后一次尝试，抛出异常
                if attempt == self.config.max_retries - 1:
                    logger.error(f"Max retries ({self.config.max_retries}) reached")
                    raise
                
                # 计算延迟时间（指数退避 + 抖动）
                delay = self._calculate_delay(attempt)
                
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                
                # 记录重试
                self.retry_history.append({
                    "attempt": attempt + 1,
                    "status": "failed",
                    "error": str(e),
                    "delay": delay,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                # 等待后重试
                time.sleep(delay)
        
        # 不应该到达这里
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        计算延迟时间
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            延迟时间（秒）
        """
        # 指数退避
        delay = self.config.base_delay * (self.config.backoff_factor ** attempt)
        
        # 限制最大延迟
        delay = min(delay, self.config.max_delay)
        
        # 添加抖动（避免惊群效应）
        if self.config.jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay
    
    def get_retry_stats(self) -> Dict:
        """获取重试统计"""
        total = len(self.retry_history)
        successes = sum(1 for h in self.retry_history if h["status"] == "success")
        failures = total - successes
        
        return {
            "total_attempts": total,
            "successes": successes,
            "failures": failures,
            "success_rate": round(successes / total * 100, 2) if total > 0 else 0
        }


class CircuitBreaker:
    """断路器
    
    防止级联故障的保护机制
    """
    
    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        self.state_history: List[Dict] = []
    
    def can_execute(self) -> bool:
        """
        检查是否可以执行
        
        Returns:
            是否允许执行
        """
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # 检查是否超过重置超时
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.config.reset_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
                    return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            # 半开状态允许有限调用
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def record_success(self):
        """记录成功"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            
            # 如果半开状态下的调用都成功，关闭断路器
            if self.half_open_calls >= self.config.half_open_max_calls:
                self._transition_to(CircuitState.CLOSED)
        elif self.state == CircuitState.CLOSED:
            # 重置失败计数
            self.failure_count = 0
    
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # 半开状态下失败，重新打开
            self._transition_to(CircuitState.OPEN)
        elif self.state == CircuitState.CLOSED:
            # 检查是否达到失败阈值
            if self.failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
    
    def _transition_to(self, new_state: CircuitState):
        """状态转换"""
        old_state = self.state
        self.state = new_state
        
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.half_open_calls = 0
        
        logger.info(f"Circuit breaker: {old_state.value} → {new_state.value}")
        
        # 记录状态历史
        self.state_history.append({
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "failure_count": self.failure_count
        })
    
    def get_status(self) -> Dict:
        """获取断路器状态"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "half_open_calls": self.half_open_calls,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "reset_timeout": self.config.reset_timeout,
                "half_open_max_calls": self.config.half_open_max_calls
            }
        }


class StateManager:
    """状态管理器
    
    检查点保存和恢复
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("./checkpoints")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.checkpoints: Dict[str, Checkpoint] = {}
    
    def save_checkpoint(self, checkpoint_id: str, state: Dict, metadata: Dict = None) -> str:
        """
        保存检查点
        
        Args:
            checkpoint_id: 检查点ID
            state: 状态数据
            metadata: 元数据
            
        Returns:
            检查点ID
        """
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            state=state,
            metadata=metadata or {}
        )
        
        # 保存到内存
        self.checkpoints[checkpoint_id] = checkpoint
        
        # 持久化到文件
        file_path = self.storage_path / f"{checkpoint_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(checkpoint), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Checkpoint saved: {checkpoint_id}")
        
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        加载检查点
        
        Args:
            checkpoint_id: 检查点ID
            
        Returns:
            检查点对象，如果不存在则返回 None
        """
        # 先从内存加载
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id]
        
        # 从文件加载
        file_path = self.storage_path / f"{checkpoint_id}.json"
        if not file_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            checkpoint = Checkpoint(**data)
            self.checkpoints[checkpoint_id] = checkpoint
            
            logger.info(f"Checkpoint loaded: {checkpoint_id}")
            
            return checkpoint
        
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """删除检查点"""
        if checkpoint_id in self.checkpoints:
            del self.checkpoints[checkpoint_id]
        
        file_path = self.storage_path / f"{checkpoint_id}.json"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Checkpoint deleted: {checkpoint_id}")
            return True
        
        return False
    
    def list_checkpoints(self) -> List[str]:
        """列出所有检查点"""
        return list(self.checkpoints.keys())


class RootCauseAnalyzer:
    """根因分析器
    
    分析错误的根本原因
    """
    
    def __init__(self):
        self.analysis_history: List[Dict] = []
    
    def analyze(self, error_event: ErrorEvent, execution_context: Dict) -> Dict:
        """
        分析根因
        
        Args:
            error_event: 错误事件
            execution_context: 执行上下文
            
        Returns:
            分析结果
        """
        analysis = {
            "error_id": error_event.error_id,
            "error_type": error_event.error_type.value,
            "root_cause": error_event.root_cause_hint,
            "severity": self._assess_severity(error_event),
            "recommended_action": self._recommend_action(error_event),
            "prevention_tips": self._get_prevention_tips(error_event),
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.analysis_history.append(analysis)
        
        logger.info(f"Root cause analysis completed: {analysis['root_cause']}")
        
        return analysis
    
    def _assess_severity(self, error_event: ErrorEvent) -> str:
        """评估严重程度"""
        severity_map = {
            ErrorType.PERMANENT: "high",
            ErrorType.AUTHENTICATION: "high",
            ErrorType.INTERNAL_ERROR: "medium",
            ErrorType.TIMEOUT: "medium",
            ErrorType.RATE_LIMIT: "low",
            ErrorType.TRANSIENT: "low",
            ErrorType.VALIDATION: "medium",
            ErrorType.RESOURCE_NOT_FOUND: "medium"
        }
        
        return severity_map.get(error_event.error_type, "medium")
    
    def _recommend_action(self, error_event: ErrorEvent) -> str:
        """推荐行动"""
        action_map = {
            ErrorType.PERMANENT: "Manual intervention required - fix the underlying issue",
            ErrorType.AUTHENTICATION: "Update credentials or API keys",
            ErrorType.INTERNAL_ERROR: "Retry with exponential backoff, contact support if persists",
            ErrorType.TIMEOUT: "Increase timeout value or optimize operation",
            ErrorType.RATE_LIMIT: "Implement rate limiting and retry with backoff",
            ErrorType.TRANSIENT: "Automatic retry should resolve this",
            ErrorType.VALIDATION: "Fix input data or validation logic",
            ErrorType.RESOURCE_NOT_FOUND: "Verify resource ID/path exists"
        }
        
        return action_map.get(error_event.error_type, "Investigate manually")
    
    def _get_prevention_tips(self, error_event: ErrorEvent) -> List[str]:
        """获取预防建议"""
        tips_map = {
            ErrorType.PERMANENT: [
                "Add comprehensive error handling",
                "Implement fallback mechanisms",
                "Add monitoring and alerting"
            ],
            ErrorType.AUTHENTICATION: [
                "Use environment variables for credentials",
                "Implement token refresh mechanism",
                "Add authentication health checks"
            ],
            ErrorType.RATE_LIMIT: [
                "Implement request queuing",
                "Add rate limit monitoring",
                "Use caching to reduce API calls"
            ],
            ErrorType.TIMEOUT: [
                "Optimize slow operations",
                "Implement async processing",
                "Add timeout monitoring"
            ]
        }
        
        return tips_map.get(error_event.error_type, ["Monitor and investigate"])


class ErrorRecoveryEngine:
    """错误恢复引擎
    
    整合智能重试、断路器、状态管理、根因分析的完整系统
    """
    
    def __init__(
        self,
        retry_config: RetryConfig = None,
        circuit_breaker_config: CircuitBreakerConfig = None
    ):
        self.smart_retry = SmartRetry(retry_config)
        self.circuit_breaker = CircuitBreaker(circuit_breaker_config)
        self.state_manager = StateManager()
        self.error_classifier = ErrorClassifier()
        self.root_cause_analyzer = RootCauseAnalyzer()
        
        self.recovery_history: List[Dict] = []
    
    def execute_with_recovery(
        self,
        operation_name: str,
        func: Callable,
        *args,
        save_checkpoint: bool = True,
        checkpoint_state: Dict = None,
        **kwargs
    ) -> Any:
        """
        带恢复机制执行操作
        
        Args:
            operation_name: 操作名称
            func: 要执行的函数
            *args: 位置参数
            save_checkpoint: 是否保存检查点
            checkpoint_state: 检查点状态
            **kwargs: 关键字参数
            
        Returns:
            函数返回值
        """
        import uuid
        
        recovery_result = {
            "operation": operation_name,
            "execution_id": str(uuid.uuid4()),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending"
        }
        
        try:
            # Step 1: 检查断路器状态
            if not self.circuit_breaker.can_execute():
                logger.warning(f"Circuit breaker is OPEN for {operation_name}")
                recovery_result["status"] = "blocked_by_circuit_breaker"
                raise RuntimeError(f"Circuit breaker is open for {operation_name}")
            
            # Step 2: 保存检查点（如果需要）
            checkpoint_id = None
            if save_checkpoint and checkpoint_state:
                checkpoint_id = f"checkpoint-{uuid.uuid4().hex[:8]}"
                self.state_manager.save_checkpoint(checkpoint_id, checkpoint_state)
                recovery_result["checkpoint_id"] = checkpoint_id
            
            # Step 3: 执行操作（带智能重试）
            result = self.smart_retry.execute_with_retry(func, *args, **kwargs)
            
            # Step 4: 记录成功
            self.circuit_breaker.record_success()
            recovery_result["status"] = "success"
            recovery_result["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Operation '{operation_name}' completed successfully")
            
            return result
        
        except Exception as e:
            # Step 5: 记录失败
            self.circuit_breaker.record_failure()
            
            # Step 6: 分类错误
            error_event = self.error_classifier.classify(e)
            recovery_result["error"] = {
                "error_id": error_event.error_id,
                "error_type": error_event.error_type.value,
                "message": str(e)
            }
            
            # Step 7: 根因分析
            analysis = self.root_cause_analyzer.analyze(error_event, {})
            recovery_result["root_cause_analysis"] = analysis
            
            # Step 8: 尝试恢复（如果有检查点）
            if checkpoint_id:
                recovery_result["recovery_attempted"] = True
                checkpoint = self.state_manager.load_checkpoint(checkpoint_id)
                if checkpoint:
                    recovery_result["recovery_status"] = "checkpoint_available"
                    logger.info(f"Checkpoint available for recovery: {checkpoint_id}")
            
            recovery_result["status"] = "failed"
            recovery_result["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            # 记录恢复历史
            self.recovery_history.append(recovery_result)
            
            logger.error(f"Operation '{operation_name}' failed: {e}")
            
            raise
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            "circuit_breaker": self.circuit_breaker.get_status(),
            "retry_stats": self.smart_retry.get_retry_stats(),
            "checkpoints": len(self.state_manager.list_checkpoints()),
            "total_recoveries": len(self.recovery_history),
            "recent_failures": len([
                r for r in self.recovery_history 
                if r["status"] == "failed"
            ])
        }


def create_error_recovery_engine() -> ErrorRecoveryEngine:
    """工厂函数：创建错误恢复引擎"""
    return ErrorRecoveryEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Error Recovery System 测试")
    print("="*60)
    
    engine = create_error_recovery_engine()
    
    # 测试1: 成功执行
    print("\n✅ 测试1: 成功执行")
    def successful_operation():
        return "Success!"
    
    result = engine.execute_with_recovery(
        "test_success",
        successful_operation
    )
    print(f"   结果: {result}")
    
    # 测试2: 临时性错误（自动重试）
    print("\n🔄 测试2: 临时性错误（自动重试）")
    attempt_count = [0]
    
    def flaky_operation():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ConnectionError("Temporary connection error")
        return "Success after retry!"
    
    result = engine.execute_with_recovery(
        "test_retry",
        flaky_operation
    )
    print(f"   结果: {result}")
    print(f"   尝试次数: {attempt_count[0]}")
    
    # 测试3: 断路器测试
    print("\n⚡ 测试3: 断路器状态")
    status = engine.get_system_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # 测试4: 检查点管理
    print("\n💾 测试4: 检查点管理")
    checkpoint_id = engine.state_manager.save_checkpoint(
        "test-checkpoint",
        {"user_id": "user-001", "progress": 50}
    )
    print(f"   检查点ID: {checkpoint_id}")
    
    loaded = engine.state_manager.load_checkpoint(checkpoint_id)
    if loaded:
        print(f"   加载成功: {loaded.state}")
    
    print("\n✅ 所有测试完成！")
